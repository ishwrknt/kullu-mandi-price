#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"
OUT_DIR="$PROJECT_DIR/reel_output"

mkdir -p "$OUT_DIR" "$PROJECT_DIR"

# --- pick the latest price JSON ---
LATEST=$(ls -1t "$DATA_DIR"/prices_*.json 2>/dev/null | head -1
        || ls -1t "$DATA_DIR"/prices.json 2>/dev/null | head -1
        || { echo "❌ No price JSON found (prices.json or prices_YYYYMMDD.json)"; exit 1; })

echo "📦 Using price data: $LATEST"

# --- extract rows into temporary CSVs (one per market) ---
python3 - <<'PY' "$LATEST"
import json, sys, pathlib
path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text())
commodities = [k for k in data['prices'].keys()]
rows = []
for comm in commodities:
    for market, rec in data['prices'][comm].items():
        if rec is None: continue
        label = f"{comm.upper()} – {market}: ₹{rec.get('modal_price_kg', rec.get('modal_price_kg', '-')):.1f}"
        rows.append(label)
path = pathlib.Path(sys.argv[2])
path.write_text("\n".join(rows) + "\n")
PY "$LATEST" "$OUT_DIR/captions.txt"

# --- create simple PNG frames using Python (no ImageMagick needed) ---
python3 - <<'PY' "$OUT_DIR"
import json, pathlib, os, math
src = pathlib.Path(sys.argv[1])          # captions.txt
lines = src.read_text().splitlines()
w, h = 800, 600
try:
    from PIL import Image, ImageDraw, ImageFont
    have_pillow = True
except Exception:
    have_pillow = False

out = pathlib.Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)

if have_pillow:
    fontObj = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    for i, line in enumerate(lines):
        img = Image.new('RGB', (w, h), (255,255,255))
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), line, font=fontObj, fill=(0,0,0))
        img.save(out / f"frame_{i:03d}.png")
else:
    # fallback: write a PPM text image (very small)
    for i, line in enumerate(lines):
        ppm = f"P6\n{w} {h}\n255\n"
        with open(out / f"frame_{i:03d}.ppm", "wb") as f:
            f.write(ppm.encode())
PY "$OUT_DIR/captions.txt" "$OUT_DIR"

# --- ffmpeg command (print it, user can run) ---
echo "▶️  To create the reel run (ffmpeg must be installed):"
echo "ffmpeg -framerate 1 -i ${OUT_DIR}/frame_%03d.png -c:v libx264 -pix_fmt yuv420p ${PROJECT_DIR}/reel.mp4"
echo "⏱️  This will produce a ~15‑second Instagram‑style reel."
