"""Genera la locución por línea y los tiempos por palabra (Whisper)."""
import json, subprocess, sys, pathlib, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import guion

ROOT = pathlib.Path(__file__).resolve().parents[1]
VO = ROOT / "assets" / "vo"
VO.mkdir(parents=True, exist_ok=True)
BASE = "https://gen.pollinations.ai/v1/audio"


def tts(texto, dest):
    body = json.dumps({**guion.VOZ, "input": texto, "response_format": "mp3"}).encode()
    req = urllib.request.Request(f"{BASE}/speech", data=body, method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer x"})
    raw = dest.with_suffix(".raw.mp3")
    with urllib.request.urlopen(req, timeout=120) as r:
        raw.write_bytes(r.read())
    # recorta el silencio inicial y acelera sin cambiar el tono
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af",
                    f"silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.03,atempo={guion.VELOCIDAD}",
                    "-c:a", "libmp3lame", "-q:a", "2", str(dest)], check=True)
    raw.unlink()


def transcribir(src):
    out = subprocess.run(["curl", "-sS", f"{BASE}/transcriptions", "-H", "Authorization: Bearer x",
                          "-F", f"file=@{src}", "-F", "model=whisper-large-v3", "-F", "language=es",
                          "-F", "response_format=verbose_json", "-F", "timestamp_granularities[]=word"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def duracion(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout)


def main(forzar=()):
    res = {}
    for lid, escena, texto in guion.LINEAS:
        mp3 = VO / f"{lid}.mp3"
        dicho = guion.texto_dicho(texto)
        if not mp3.exists() or lid in forzar:
            tts(dicho, mp3)
        tr = transcribir(mp3)
        res[lid] = {"dicho": dicho, "duracion": duracion(mp3), "transcripcion": tr.get("text", "").strip(),
                    "palabras": [{"w": w["word"], "s": w["start"], "e": w["end"]} for w in tr.get("words", [])]}
        print(lid, round(res[lid]["duracion"], 2), "|", res[lid]["transcripcion"])
    (VO / "tiempos.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(set(sys.argv[1:]))
