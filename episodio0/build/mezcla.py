"""Línea de tiempo + banda sonora 100% sintetizada (sin samples de terceros) + mezcla con la VO.

Diseño sonoro para retención:
  - impacto en el fotograma 0 (el gancho se OYE antes de leerse)
  - sin música "de relleno": ritmo de 112 bpm desde el logo, con silencios dramáticos antes de los golpes clave
  - un golpe en cada palabra de énfasis, un 'boom' en cada SLAM y un silbido en cada corte de escena
"""
import json, subprocess, sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import guion

ROOT = pathlib.Path(__file__).resolve().parents[1]
VO = ROOT / "assets" / "vo"
OUT = ROOT / "out"
SR = 48000
BPM = 112


# ---------------------------------------------------------------- línea de tiempo
def construir_timeline():
    tiempos = json.loads((VO / "tiempos.json").read_text())
    t = 0.0
    lineas = []
    for lid, escena, texto in guion.LINEAS:
        t += guion.PAUSA_ANTES[lid]
        info = tiempos[lid]
        toks = guion.tokens(texto)
        pal = info["palabras"]
        n_dichas = sum(len(d.split()) for d, _, _, _ in toks)
        t0 = pal[0]["s"] if pal else 0.0
        t1 = pal[-1]["e"] if pal else info["duracion"]
        out_toks = []
        if len(pal) == n_dichas:
            i = 0
            for d, m, enf, slam in toks:
                k = len(d.split())
                out_toks.append({"txt": m, "enf": enf, "slam": slam, "s": t + pal[i]["s"], "e": t + pal[i + k - 1]["e"]})
                i += k
        else:  # reparto proporcional por caracteres
            total = sum(len(d) for d, _, _, _ in toks)
            acc = 0
            for d, m, enf, slam in toks:
                s = t0 + (t1 - t0) * acc / total
                acc += len(d)
                e = t0 + (t1 - t0) * acc / total
                out_toks.append({"txt": m, "enf": enf, "slam": slam, "s": t + s, "e": t + e})
        lineas.append({"id": lid, "escena": escena, "inicio": t, "fin": t + info["duracion"],
                       "voz_ini": t + t0, "voz_fin": t + t1, "tokens": out_toks,
                       "alineado": len(pal) == n_dichas})
        t += info["duracion"]
    total = t + guion.COLA_FINAL
    tl = {"duracion": total, "lineas": lineas}
    (OUT / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1))
    return tl


# ---------------------------------------------------------------- síntesis
def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def kick(f0=95, f1=42, dur=0.35, tau=0.10):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tt / 0.04)
    fase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(fase) * env_exp(n, tau)


def ruido_lp(n, a=0.02, rng=None):
    rng = rng or np.random.default_rng(1)
    x = rng.standard_normal(n)
    y = np.empty(n)
    acc = 0.0
    for i in range(n):  # paso bajo de un polo
        acc += a * (x[i] - acc)
        y[i] = acc
    return y / (np.abs(y).max() + 1e-9)


def boom(dur=2.2):
    n = int(dur * SR)
    k = kick(80, 30, dur, 0.55)
    nz = ruido_lp(n, 0.01) * env_exp(n, 0.35) * 0.6
    sub = np.sin(2 * np.pi * 36 * np.arange(n) / SR) * env_exp(n, 0.9) * 0.5
    return (k + nz + sub) * 0.9


def glitch(dur=0.08, seed=0):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = rng.standard_normal(n)
    paso = rng.integers(20, 90)
    x = np.repeat(x[::paso], paso)[:n]           # sample & hold = bitcrush
    x = np.round(x * 3) / 3
    e = np.ones(n); e[-n // 4:] = np.linspace(1, 0, n - (n - n // 4))
    return x * e * 0.35


def click():
    n = int(0.03 * SR)
    tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2300 * tt) * 0.5 + np.random.default_rng(3).standard_normal(n) * 0.3) * env_exp(n, 0.006)


def tecla(seed):
    n = int(0.025 * SR)
    rng = np.random.default_rng(seed)
    tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * (1400 + rng.integers(0, 500)) * tt) * 0.3 + rng.standard_normal(n) * 0.15) * env_exp(n, 0.005)


def subida(dur=0.9):
    n = int(dur * SR)
    nz = np.random.default_rng(7).standard_normal(n)
    nz = np.diff(np.concatenate([[0], nz]))     # paso alto barato
    return nz * np.linspace(0, 1, n) ** 3 * 0.12


def hat(seed=0):
    n = int(0.05 * SR)
    nz = np.diff(np.concatenate([[0], np.random.default_rng(100 + seed).standard_normal(n)]))
    return nz * env_exp(n, 0.012) * 0.25


def caja():
    n = int(0.16 * SR)
    nz = np.diff(np.concatenate([[0], np.random.default_rng(55).standard_normal(n)]))
    tt = np.arange(n) / SR
    return (nz * 0.5 + np.sin(2 * np.pi * 190 * tt) * 0.5) * env_exp(n, 0.045) * 0.7


def silbido(dur=0.32):
    """Whoosh: ruido que sube y baja. Se precalcula una vez."""
    n = int(dur * SR)
    x = np.random.default_rng(21).standard_normal(n)
    y = np.empty(n)
    acc = 0.0
    for i in range(n):
        a = 0.03 + 0.5 * np.sin(np.pi * i / n) ** 2        # el filtro se abre y se cierra
        acc += a * (x[i] - acc)
        y[i] = acc
    return y / (np.abs(y).max() + 1e-9) * np.sin(np.pi * np.arange(n) / n) ** 1.5 * 0.55


def drone(total, brillo):
    n = int(total * SR)
    tt = np.arange(n) / SR
    y = np.zeros(n)
    for base, amp in ((55.0, 1.0), (82.41, 0.55), (110.3, 0.25)):
        for h in range(1, 9):
            a = amp / h * np.exp(-(h - 1) / brillo(tt))
            det = 1 + 0.0015 * np.sin(2 * np.pi * 0.11 * tt + h)
            y += a * np.sin(2 * np.pi * base * h * det * tt + h * 1.3)
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.07 * tt)
    return y * lfo / 6.0


def colocar(buf, sig, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf) or i < -len(sig):
        return
    if i < 0:
        sig, i = sig[-i:], 0
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * g


def leer_vo(lid):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(VO / f"{lid}.mp3"), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def tok(linea, pref):
    """Inicio del primer token cuyo texto empieza por `pref`."""
    for tk in linea["tokens"]:
        if tk["txt"].upper().startswith(pref):
            return tk["s"]
    return linea["tokens"][0]["s"]


def mezclar(tl):
    T = tl["duracion"]
    n = int(T * SR) + SR
    L = {l["id"]: l for l in tl["lineas"]}
    ids = [l["id"] for l in tl["lineas"]]
    t_logo = L["K03"]["inicio"] - 0.10
    t_final = L["K15"]["inicio"] - 0.12
    t_elim = tok(L["K01"], "ELIMINARTE")
    t_ni = tok(L["K08"], "NI NOSOTROS")
    beat = 60 / BPM

    def brillo(tt):
        b = 1.6 + 3.0 * np.clip(tt / T, 0, 1)
        return np.where((tt > t_final - 0.6) & (tt < t_final + 0.4), 0.7, b)

    musica = drone(T + 1, brillo)
    tt = np.arange(len(musica)) / SR
    vol = np.interp(tt, [0, 0.4, t_logo - 0.1, t_logo, t_ni - 0.5, t_ni, t_final - 0.6, t_final - 0.05, t_final + 0.3, T - 0.03, T],
                    [0.55, 0.65, 0.75, 0.55, 0.60, 0.0, 0.7, 0.0, 0.85, 0.85, 0.0])
    musica *= vol
    sfx = np.zeros(n)

    # ---- GANCHO: impacto en el fotograma 0 y colapso de la tarjeta
    colocar(sfx, boom(1.6), 0.0, 1.0)
    for k in range(3):
        colocar(sfx, glitch(0.05, 30 + k), 0.02 + k * 0.05, 0.8)
    colocar(sfx, boom(2.0), t_elim, 1.0)
    for k in range(8):
        colocar(sfx, glitch(0.05 + 0.02 * (k % 3), k), t_elim + k * 0.06, 0.8)

    # ---- K02: la multitud se desintegra mientras sube la tensión hacia el logo
    k2 = L["K02"]
    colocar(sfx, subida(t_logo - k2["inicio"] + 0.1), k2["inicio"] - 0.05, 1.0)
    for k in range(8):
        colocar(sfx, glitch(0.05 + 0.03 * (k % 3), 10 + k), k2["inicio"] + 0.1 + k * 0.17, 0.7)

    # ---- logo
    colocar(sfx, boom(2.2), t_logo, 0.95)
    for k in range(4):
        colocar(sfx, glitch(0.06, 40 + k), t_logo + k * 0.07, 0.7)

    # ---- ritmo desde el logo hasta el final (con silencios dramáticos)
    vacios = [(t_ni - 0.45, t_ni + 0.05), (t_final - 0.65, t_final + 0.1)]
    lat = kick(75, 40, 0.3, 0.07)
    t, i = t_logo + 0.35, 0
    while t < t_final - 0.1:
        if not any(a <= t < b for a, b in vacios):
            prog = (t - t_logo) / (t_final - t_logo)
            colocar(sfx, lat, t, 0.55 + 0.25 * prog)
            colocar(sfx, hat(i % 4), t + beat / 2, 0.8)
            if i % 2 == 1:
                colocar(sfx, caja(), t, 0.55)
        t += beat
        i += 1

    # ---- un golpe por palabra de énfasis y un boom por SLAM
    golpe = kick(115, 55, 0.2, 0.07)
    for lid in ids:
        for tk in L[lid]["tokens"]:
            if tk["slam"]:
                colocar(sfx, boom(1.1) * 0.8, tk["s"], 0.9)
                colocar(sfx, glitch(0.05, int(tk["s"] * 100) % 50), tk["s"], 0.7)
            elif tk["enf"] and lid not in ("K01", "K15"):
                colocar(sfx, golpe, tk["s"], 0.55)
                colocar(sfx, click(), tk["s"], 0.5)

    # ---- silbido en cada corte de escena (menos los continuos)
    sil = silbido()
    seguidas = {("K06", "K07"), ("K10", "K11")}
    for a, b in zip(ids[1:], ids[2:] + [None]):
        pass
    for prev, cur in zip(ids[:-1], ids[1:]):
        if (prev, cur) in seguidas or cur in ("K03", "K15", "K02"):
            continue
        colocar(sfx, sil, L[cur]["inicio"] - 0.12 - 0.22, 0.6)

    # ---- detalles por escena
    colocar(sfx, glitch(0.06, 60), tok(L["K05"], "NADIE"), 0.8)
    k6 = L["K06"]
    t = tok(k6, "UN") if any(tk["txt"] == "UN" for tk in k6["tokens"]) else k6["inicio"] + 1.2
    while t < k6["fin"]:
        colocar(sfx, tecla(int(t * 100)), t, 0.35)
        t += 0.06
    colocar(sfx, click(), L["K07"]["inicio"] - 0.1, 0.9)
    k8 = L["K08"]
    colocar(sfx, click(), t_ni, 1.0)
    colocar(sfx, kick(120, 60, 0.25, 0.05), t_ni, 0.5)
    t_cae = tok(L["K10"], "CAES")
    for k in range(6):
        colocar(sfx, glitch(0.07, 70 + k), t_cae + k * 0.08, 0.7)
    k11 = L["K11"]
    for k in range(5):
        colocar(sfx, click(), k11["inicio"] + 0.25 + k * 0.38, 0.45)
    t_entro = tok(L["K12"], "ENTRO")
    for k in range(6):
        colocar(sfx, tecla(200 + k), t_entro + k * 0.07, 0.8)
    k13 = L["K13"]
    for pref in ("MARTES", "20:00", "HORA"):
        colocar(sfx, kick(90, 40, 0.4, 0.12), tok(k13, pref), 0.65)
    k14 = L["K14"]
    colocar(sfx, subida(1.1) * 0.8, k14["inicio"] - 0.1, 1.0)
    colocar(sfx, kick(60, 30, 1.0, 0.35), tok(k14, "ABRE"), 0.8)

    # ---- bucle: un riser sube justo antes de reiniciar y el impacto del segundo 0 lo resuelve
    colocar(sfx, subida(0.85) * 1.3, T - 0.85, 1.0)

    # ---- final: golpe y glitch (el corte en seco al reiniciar el bucle hace el resto)
    colocar(sfx, boom(1.6), t_final + 0.05, 1.0)
    for k in range(3):
        colocar(sfx, glitch(0.05, 90 + k), t_final + 0.05 + k * 0.06, 0.6)

    voz = np.zeros(n)
    for l in tl["lineas"]:
        colocar(voz, leer_vo(l["id"]), l["inicio"], 1.0)

    # ducking de la música bajo la voz
    env = np.abs(voz)
    k = int(0.15 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    duck = 1 - 0.45 * np.clip(env / (env.max() * 0.25 + 1e-9), 0, 1)
    mus = np.zeros(n); mus[: min(n, len(musica))] = musica[:n]
    mezcla = voz * 1.0 + mus * duck * 0.30 + sfx * 0.55
    mezcla = mezcla[: int(T * SR)]
    mezcla /= np.abs(mezcla).max() * 1.05
    f = int(0.02 * SR)
    mezcla[-f:] *= np.linspace(1, 0, f)          # fundido de 20 ms: evita el 'clic' al repetir
    lado = np.roll(mus[: len(mezcla)] * 0.03, int(0.012 * SR))
    est = np.stack([mezcla + lado, mezcla - lado], axis=1).astype(np.float32)
    wav = OUT / "mezcla_cruda.f32"
    est.tofile(wav)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", str(wav),
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", str(SR), str(OUT / "audio.wav")], check=True)
    wav.unlink()
    print("audio listo", round(T, 2), "s")


if __name__ == "__main__":
    tl = construir_timeline()
    for l in tl["lineas"]:
        print(l["id"], l["escena"], round(l["inicio"], 2), round(l["fin"], 2), "alineado" if l["alineado"] else "PROPORCIONAL")
    mezclar(tl)
