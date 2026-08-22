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
    required_scopes = {(market["state"], market.get("district")) for market in MAIN_MARKETS}
    all_scopes = {(market["state"], market.get("district")) for market in ALL_MARKETS}
    scopes = list(required_scopes) + sorted(all_scopes - required_scopes)
    for state, district in scopes:
        configured_markets = [m for m in ALL_MARKETS if m["state"] == state and m.get("district") == district]
        scope_records = 0
        last_error = None
        for commodity in COMMODITIES:
            try:
                records = client.records_for_commodity(state, district, commodity["name"], target_date)
            except APIError as exc:
                last_error = exc
                continue
            scope_records += len(records)
            for raw in records:
                market = next((m for m in configured_markets if market_matches(raw.get("market"), m)), None)
                if market is None:
                    unmatched_markets.add(str(raw.get("market", "")))
                    continue
                matched = next((item for item in COMMODITIES if match_commodity(raw.get("commodity"), item)), None)
                if matched is None:
                    unmatched_commodities.add(str(raw.get("commodity", "")))
                    continue
                normalized = normalized_record(raw, market, matched, target_date)
                if normalized is None:
                    continue
                slot = prices[matched["key"]][market["display"]]
                if slot is None or (slot["modal_price_quintal"] is None and normalized["modal_price_quintal"] is not None):
                    prices[matched["key"]][market["display"]] = normalized
                    verification.append(normalized)
        if (state, district) in required_scopes and scope_records == 0 and last_error:
            raise last_error
    return prices, verification, sorted(unmatched_markets), sorted(unmatched_commodities)
