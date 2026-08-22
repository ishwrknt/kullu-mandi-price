from .commodity_config import COMMODITIES
from .market_config import ALL_MARKETS
from .market_config import MAIN_MARKETS
from .api_client import APIError
from .normalizer import clean, match_commodity, normalized_record


def market_matches(actual, market):
    actual_clean = clean(actual)
    return any(actual_clean == clean(alias) for alias in market["aliases"])


def fetch_prices(client, target_date):
    prices = {item["key"]: {market["display"]: None for market in ALL_MARKETS} for item in COMMODITIES}
    verification, unmatched_markets, unmatched_commodities = [], set(), set()
    scopes = {(market["state"], market.get("district")) for market in ALL_MARKETS}
    required_scopes = {(market["state"], market.get("district")) for market in MAIN_MARKETS}
    for state, district in scopes:
        try:
            records = client.records_for_scope(state, district)
        except APIError as exc:
            if (state, district) in required_scopes:
                raise
            print(f"WARNING: comparison scope unavailable: {exc}", flush=True)
            continue
        configured_markets = [m for m in ALL_MARKETS if m["state"] == state and m.get("district") == district]
        for raw in records:
            if str(raw.get("arrival_date", "")).strip() != target_date:
                continue
            market = next((m for m in configured_markets if market_matches(raw.get("market"), m)), None)
            if market is None:
                unmatched_markets.add(str(raw.get("market", "")))
                continue
            commodity = next((item for item in COMMODITIES if match_commodity(raw.get("commodity"), item)), None)
            if commodity is None:
                unmatched_commodities.add(str(raw.get("commodity", "")))
                continue
            normalized = normalized_record(raw, market, commodity, target_date)
            if normalized is None:
                continue
            slot = prices[commodity["key"]][market["display"]]
            if slot is None or (slot["modal_price_quintal"] is None and normalized["modal_price_quintal"] is not None):
                prices[commodity["key"]][market["display"]] = normalized
                verification.append(normalized)
    return prices, verification, sorted(unmatched_markets), sorted(unmatched_commodities)
