# 🌾 Kullu Mandi Prices

A lightweight Android-friendly PWA for the seven public commodities: Apple, Pear, Plum, Peach, Tomato, Cabbage and Cauliflower.

## Architecture

- Browser reads only public JSON under `data/`; it never calls AGMARKNET and never sees a key.
- `scripts/fetch_prices.py` is the single cloud fetcher. It reads `AGMARKNET_API_KEY`, queries the official data.gov.in resource, matches aliases, converts ₹/quintal to ₹/kg and preserves min/max/modal values.
- GitHub Actions runs the fetcher daily and supports manual dispatch. Failed fetches do not overwrite the last good data.
- GitHub Pages serves the PWA.

## Local run

```bash
python -m pip install requests
export AGMARKNET_API_KEY="your-key"
python scripts/fetch_prices.py
python -m http.server 8000
```

Open `http://localhost:8000`. Never put the key in `data/`, HTML, JavaScript, or a committed file. Keep local secrets in an ignored `.env` if desired.

## GitHub setup

1. Repository **Settings → Secrets and variables → Actions → New repository secret**.
2. Name it exactly `AGMARKNET_API_KEY`.
3. Enable **Settings → Pages → Source: GitHub Actions**.
4. Run **Actions → Update mandi prices → Run workflow** once. The scheduled job runs at 08:00 IST (`02:30 UTC`).
5. Website: https://ishwrknt.github.io/kullu-mandi-price/

The update workflow commits `data/prices.json`, `data/dates.json`, and `data/dates/YYYY-MM-DD.json`. The phone only needs the website; no Node, Python, Termux or laptop is needed after deployment.
