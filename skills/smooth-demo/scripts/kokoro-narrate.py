#!/usr/bin/env python3
"""Free local narration for smooth-demo: Kokoro-82M (Hugging Face mlx-community/Kokoro-82M-bf16) via mlx-audio.

No API key and no per-use cost; it runs on-device (Apple Silicon). The only network use is the one-time
model download. Run it with the mlx-audio tool's Python (setup: scripts/setup-kokoro.sh):

  ~/.local/share/uv/tools/mlx-audio/bin/python scripts/kokoro-narrate.py script.json --out narration/ \
      [--voice af_heart] [--speed 1.0] [--lang a] [--respell respell.json] [--force]

script.json   [{"id": "ch01", "text": "Narration for chapter one."}, ...]
respell.json  optional {"401": "four oh one", "auth": "oath"}: whole-token replacements applied before synthesis
Output        <out>/<id>.wav (24 kHz mono, edges trimmed) and <out>/narration.json
              (id, text, spoken, hash, model, voice, speed, lang, file, duration)
A clip is reused when the hash of (spoken text, model, voice, speed, lang) is unchanged, so editing one
line regenerates only that clip.
"""
import argparse, hashlib, json, os, re, sys

MODEL = "mlx-community/Kokoro-82M-bf16"
SR = 24000
# Acronyms Kokoro reads badly. A plain "A P I" can be read as the article "uh", hence the phonetic respelling.
BUILTIN = {"API": "ay pee eye", "APIs": "ay pee eyes", "UI": "you eye", "URL": "U R L", "URLs": "U R Ls",
           "SQL": "sequel", "PR": "pull request", "PRs": "pull requests"}


def spoken(text, extra):
    table = {**BUILTIN, **extra}
    text = text.replace("’", "'")
    for k in sorted(table, key=len, reverse=True):
        text = re.sub(r"(?<![\w])" + re.escape(k) + r"(?![\w])", table[k], text)
    # camelCase identifiers become words: requireAuthenticatedUser -> require authenticated user
    return re.sub(r"\b[a-z]+(?:[A-Z][a-z0-9]*)+\b",
                  lambda m: re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", m.group(0)).lower(), text)


def trim(np, a, lead=0.06, tail=0.14, thr=0.012):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    s, e = max(0, idx[0] - int(lead * SR)), min(len(a), idx[-1] + int(tail * SR))
    a = a[s:e].copy()
    f = int(0.006 * SR)
    a[:f] *= np.linspace(0, 1, f)
    a[-f:] *= np.linspace(1, 0, f)
    return a


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script")
    ap.add_argument("--out", default="narration")
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--lang", default=None, help="a = American English, b = British English; default: first letter of the voice")
    ap.add_argument("--respell", help="JSON file of {\"text\": \"spoken\"} replacements")
    ap.add_argument("--force", action="store_true", help="ignore the cache and regenerate every clip")
    a = ap.parse_args()
    lang = a.lang or a.voice[0]
    if lang not in ("a", "b"):
        print(f"note: lang '{lang}' needs extra misaki packages that setup-kokoro.sh does not install", file=sys.stderr)
    try:
        import numpy as np
        from scipy.io import wavfile
    except ImportError as e:
        sys.exit(f"Missing {e.name}. Run this file with ~/.local/share/uv/tools/mlx-audio/bin/python (setup: scripts/setup-kokoro.sh)")
    clips = json.load(open(a.script))
    extra = json.load(open(a.respell)) if a.respell else {}
    os.makedirs(a.out, exist_ok=True)
    meta = os.path.join(a.out, "narration.json")
    old = {r["id"]: r for r in json.load(open(meta))} if os.path.exists(meta) and not a.force else {}
    model, rows = None, []
    for c in clips:
        text = spoken(c["text"], extra)
        h = hashlib.sha256(json.dumps([text, MODEL, a.voice, a.speed, lang]).encode()).hexdigest()[:16]
        fn = os.path.join(a.out, f"{c['id']}.wav")
        prev = old.get(c["id"])
        if prev and prev.get("hash") == h and os.path.exists(fn):
            rows.append({**prev, "text": c["text"]})
            print(f"{c['id']:<14} reused  {prev['duration']:5.2f}s")
            continue
        if model is None:
            try:
                from mlx_audio.tts.utils import load_model
            except ImportError as e:
                sys.exit(f"Missing {e.name}. Run scripts/setup-kokoro.sh once, then use ~/.local/share/uv/tools/mlx-audio/bin/python")
            model = load_model(MODEL)
        segs = [np.array(r.audio, dtype=np.float32).reshape(-1)
                for r in model.generate(text=text, voice=a.voice, speed=a.speed, lang_code=lang)]
        audio = trim(np, np.concatenate(segs))
        wavfile.write(fn, SR, (np.clip(audio, -1, 1) * 32767).astype(np.int16))
        dur = round(len(audio) / SR, 3)
        rows.append({"id": c["id"], "text": c["text"], "spoken": text, "hash": h, "model": MODEL, "voice": a.voice,
                     "speed": a.speed, "lang": lang, "file": fn, "duration": dur})
        print(f"{c['id']:<14} made    {dur:5.2f}s  {text[:70]}")
    json.dump(rows, open(meta, "w"), indent=1, ensure_ascii=False)
    print(f"{len(rows)} clips, {sum(r['duration'] for r in rows):.1f}s of speech -> {meta}")


if __name__ == "__main__":
    main()
