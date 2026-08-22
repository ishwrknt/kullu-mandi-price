# Kullu Mandi Price

A small mobile-first PWA that reads a generated `data/prices.json` file and copies a WhatsApp-ready mandi report. The browser never calls data.gov.in and never receives the API key.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export MANDI_API_KEY="..."
python scripts/fetch_prices_v2.py
python -m http.server 8000
```

Open `http://localhost:8000`. The fetcher uses Asia/Kolkata for the target date, makes small market-scoped requests, retries transient failures, and atomically replaces `data/prices.json` only after validation. If it fails, the old file is untouched.

## GitHub

Add a repository Actions secret named `MANDI_API_KEY`. Enable GitHub Pages using **GitHub Actions** as the source. `update-prices.yml` runs at 08:00 IST (`02:30 UTC`) and supports manual dispatch; `deploy.yml` publishes the static PWA.

## Aliases and debugging

Market display names and candidate API names live in `src/data/market_config.py`. The fetcher records the actual API market and commodity values in `verification`. Commodity matching accepts exact names and safe parenthesized variants such as `Pear(Marasebu)`; it does not use loose substring matching. Expand the `Data Verification` section in the app or inspect `data/prices.json` to correct a verified alias.

Prices retain original ₹/quintal values and derived ₹/kg values. Missing values are `null` internally and `-` in the report. Only modal, minimum, or maximum values from the underlying API record can be displayed.
