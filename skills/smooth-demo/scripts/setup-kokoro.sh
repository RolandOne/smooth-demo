#!/usr/bin/env bash
# One-time setup for free local narration: Kokoro-82M (Hugging Face) through mlx-audio. Apple Silicon only.
# Downloads about 1.1 GB (tool environment, includes PyTorch) plus a 341 MB model; uv also caches wheels.
# Do NOT add the README's --prerelease=allow: it pulls spaCy 4 dev + thinc 9, which crash with a numpy ABI error.
set -euo pipefail
[ "$(uname -m)" = "arm64" ] || { echo "mlx-audio needs an Apple Silicon Mac" >&2; exit 1; }
command -v uv >/dev/null || { echo "uv is required: brew install uv" >&2; exit 1; }
uv tool install --force mlx-audio \
  --with "misaki[en]" --with "spacy>=3.8,<4" --with "thinc>=8.3,<9" \
  --with "en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
"$HOME/.local/share/uv/tools/mlx-audio/bin/python" - <<'PY'
from mlx_audio.tts.utils import load_model
load_model("mlx-community/Kokoro-82M-bf16")  # downloads the model into the Hugging Face cache
print("Kokoro ready")
PY
