"""Línea de tiempo + banda sonora 100% sintetizada (sin samples de terceros) + mezcla con la VO."""
import json, subprocess, sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import guion

ROOT = pathlib.Path(__file__).resolve().parents[1]
VO = ROOT / "assets" / "vo"
OUT = ROOT / "out"
SR = 48000


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
        n_dichas = sum(len(d.split()) for d, _, _ in toks)
        t0 = pal[0]["s"] if pal else 0.0
        t1 = pal[-1]["e"] if pal else info["duracion"]
        out_toks = []
        if len(pal) == n_dichas:
            i = 0
            for d, m, enf in toks:
                k = len(d.split())
                out_toks.append({"txt": m, "enf": enf, "s": t + pal[i]["s"], "e": t + pal[i + k - 1]["e"]})
                i += k
        else:  # reparto proporcional por caracteres
            total = sum(len(d) for d, _, _ in toks)
            acc = 0
            for d, m, enf in toks:
                s = t0 + (t1 - t0) * acc / total
                acc += len(d)
                e = t0 + (t1 - t0) * acc / total
                out_toks.append({"txt": m, "enf": enf, "s": t + s, "e": t + e})
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
    # paso alto barato + crescendo
    nz = np.diff(np.concatenate([[0], nz]))
    return nz * np.linspace(0, 1, n) ** 3 * 0.12


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
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * g


def leer_vo(lid):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(VO / f"{lid}.mp3"), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def tok_t(linea, i):
    return linea["tokens"][min(i, len(linea["tokens"]) - 1)]["s"]


def mezclar(tl):
    T = tl["duracion"]
    n = int(T * SR) + SR
    L = {l["id"]: l for l in tl["lineas"]}
    t_logo = L["L03"]["inicio"] - 0.12
    t_final = L["L15"]["inicio"] - 0.12

    # brillo del drone: sube a lo largo del video, cae en el silencio previo a la pregunta final
    def brillo(tt):
        b = 1.3 + 3.2 * np.clip(tt / T, 0, 1)
        return np.where((tt > t_final - 0.6) & (tt < t_final + 0.4), 0.6, b)

    musica = drone(T + 1, brillo)
    vol = np.interp(np.arange(len(musica)) / SR, [0, 1.0, t_final - 0.8, t_final - 0.2, t_final + 0.5, T - 1.2, T + 1],
                    [0, 0.55, 0.75, 0.0, 0.8, 0.8, 0])
    musica *= vol
    sfx = np.zeros(n)

    # latido 70 bpm desde L04 hasta antes del final
    lat = kick(70, 38, 0.4, 0.09)
    t = L["L04"]["inicio"] - 0.12
    beat = 60 / 70
    while t < t_final - 0.9:
        prog = (t - L["L04"]["inicio"]) / (t_final - L["L04"]["inicio"])
        colocar(sfx, lat, t, 0.35 + 0.35 * prog)
        colocar(sfx, lat, t + 0.22, 0.2 + 0.2 * prog)
        t += beat

    colocar(sfx, subida(0.9), t_logo - 0.9, 1.0)
    colocar(sfx, boom(), t_logo, 0.95)
    for k in range(9):  # desintegración de la multitud
        colocar(sfx, glitch(0.05 + 0.03 * (k % 3), k), L["L02"]["inicio"] + 0.12 + k * 0.19, 0.8)
    for k in range(4):
        colocar(sfx, glitch(0.06, 40 + k), t_logo + k * 0.07, 0.7)
    # ID: tic de ruleta mientras se dice "recibes un número"
    t = L["L05"]["inicio"] + 0.9
    while t < L["L05"]["fin"]:
        colocar(sfx, tecla(int(t * 100)), t, 0.35)
        t += 0.07
    colocar(sfx, click(), L["L06"]["inicio"] - 0.1, 0.9)
    # candado
    l7 = L["L07"]
    colocar(sfx, click(), tok_t(l7, len(l7["tokens"]) - 1), 1.0)
    colocar(sfx, kick(120, 60, 0.25, 0.05), tok_t(l7, len(l7["tokens"]) - 1), 0.5)
    # fantasma
    l9 = L["L09"]
    for k in range(6):
        colocar(sfx, glitch(0.07, 70 + k), tok_t(l9, 2) + k * 0.08, 0.7)
    # votos: una papeleta por fantasma
    l10 = L["L10"]
    for k in range(5):
        colocar(sfx, click(), l10["inicio"] + 0.35 + k * 0.42, 0.45)
    # tecleo de ENTRO
    l11 = L["L11"]
    for k in range(6):
        colocar(sfx, tecla(200 + k), tok_t(l11, 3) + k * 0.09, 0.8)
    # fecha y puertas
    colocar(sfx, kick(90, 40, 0.6, 0.18), L["L12"]["inicio"] - 0.1, 0.8)
    colocar(sfx, subida(1.4) * 0.8, L["L14"]["inicio"] + 0.4, 1.0)
    colocar(sfx, kick(60, 30, 1.0, 0.35), tok_t(L["L14"], 4), 0.7)
    # golpe final
    colocar(sfx, boom(2.8), t_final + 0.05, 1.0)
    for k in range(3):
        colocar(sfx, glitch(0.05, 90 + k), t_final + 0.05 + k * 0.06, 0.6)

    voz = np.zeros(n)
    for l in tl["lineas"]:
        colocar(voz, leer_vo(l["id"]), l["inicio"], 1.0)

    # ducking simple de la música bajo la voz
    env = np.abs(voz)
    k = int(0.15 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    duck = 1 - 0.45 * np.clip(env / (env.max() * 0.25 + 1e-9), 0, 1)
    mus = np.zeros(n); mus[: min(n, len(musica))] = musica[:n]
    mezcla = voz * 1.0 + mus * duck * 0.32 + sfx * 0.55
    mezcla = mezcla[: int(T * SR)]
    mezcla /= np.abs(mezcla).max() * 1.05
    # ligera amplitud estéreo para la música/SFX (la voz va al centro)
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
