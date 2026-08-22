#!/usr/bin/env python3
"""Fetch configured market slices and atomically publish data/prices.json."""
import json, os, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.api_client_scoped import APIClient, APIError
from src.data.commodity_config import COMMODITIES
from src.data.market_config import ALL_MARKETS, MAIN_MARKETS, COMPARISON_MARKETS
from src.data.price_service_scoped import fetch_prices

OUTPUT = ROOT / "data" / "prices.json"
TZ = ZoneInfo("Asia/Kolkata")


def validate(prices, target_date):
    if set(prices) != {item["key"] for item in COMMODITIES}:
        raise ValueError("required seven-commodity schema is incomplete")
    valid_markets = {market["display"] for market in ALL_MARKETS}
    for item in COMMODITIES:
        if set(prices[item["key"]]) != valid_markets:
            raise ValueError(f"market schema incomplete for {item['name']}")
        for display_market, record in prices[item["key"]].items():
            if record is None: continue
            if record["date"] != target_date or record["market"] != display_market:
                raise ValueError("record date or market mismatch")
            for field in ("min_price_quintal", "max_price_quintal", "modal_price_quintal", "min_price_kg", "max_price_kg", "modal_price_kg"):
                value = record[field]
                if value is not None and (not isinstance(value, (int, float)) or value < 0): raise ValueError(f"invalid {field}")
            for source, converted in (("min_price_quintal", "min_price_kg"), ("max_price_quintal", "max_price_kg"), ("modal_price_quintal", "modal_price_kg")):
                if record[source] is not None and record[converted] != record[source] / 100: raise ValueError(f"conversion mismatch for {display_market}")


def main():
    api_key = os.environ.get("MANDI_API_KEY")
    if not api_key: raise SystemExit("MANDI_API_KEY is required")
    now = datetime.now(TZ); target_date = now.strftime("%d/%m/%Y")
    print(f"KULLU MANDI PRICE FETCHER | {target_date} Asia/Kolkata")
    try:
        prices, verification, missing_markets, unmatched_commodities = fetch_prices(APIClient(api_key), target_date)
        validate(prices, target_date)
    except (APIError, ValueError) as exc:
        print(f"ERROR: {exc}\nExisting prices.json was preserved.", file=sys.stderr); raise SystemExit(1)
    payload = {"schema_version": 1, "date": now.strftime("%Y-%m-%d"), "display_date": target_date, "updated_at": now.isoformat(), "source": "AGMARKNET / data.gov.in", "price_unit": "₹/kg", "conversion": "₹/quintal ÷ 100", "commodities": COMMODITIES, "main_markets": MAIN_MARKETS, "comparison_markets": COMPARISON_MARKETS, "prices": prices, "verification": verification, "unmatched_api_markets": missing_markets, "unmatched_api_commodities": unmatched_commodities}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True); temporary = OUTPUT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"); temporary.replace(OUTPUT)
    print("\nDATA CHECK\n----------")
    for item in COMMODITIES:
        values = []
        for market in MAIN_MARKETS:
            record = prices[item["key"]][market["display"]]
            values.append(f"{market['display']}: ₹{record['modal_price_kg']:.1f}" if record and record["modal_price_kg"] is not None else f"{market['display']}: -")
        print(f"{item['emoji']} {item['name']}: " + " | ".join(values))
    if missing_markets: print("\nMarkets with no records returned: " + ", ".join(missing_markets))
    if unmatched_commodities: print("Unmatched API commodities: " + ", ".join(unmatched_commodities))
    print(f"\nSaved {len(verification)} normalized records to {OUTPUT}")


if __name__ == "__main__": main()
