from .commodity_config import COMMODITIES
from .market_config import ALL_MARKETS
from .normalizer import match_commodity, normalized_record


def fetch_prices(client, target_date):
    prices = {item["key"]: {market["display"]: None for market in ALL_MARKETS} for item in COMMODITIES}
    verification = []
    unmatched_markets = set()
    unmatched_commodities = set()
    for market in ALL_MARKETS:
        records = client.records_for_market(market)
        for raw in records:
            if str(raw.get("arrival_date", "")).strip() != target_date:
                continue
            commodity = next((item for item in COMMODITIES if match_commodity(raw.get("commodity"), item)), None)
            if commodity is None:
                unmatched_commodities.add(str(raw.get("commodity", "")))
                continue
            normalized = normalized_record(raw, market, commodity, target_date)
            if normalized is None:
                continue
            slot = prices[commodity["key"]][market["display"]]
            if slot is None or normalized["modal_price_quintal"] is not None:
                prices[commodity["key"]][market["display"]] = normalized
                verification.append(normalized)
        if not records:
            unmatched_markets.add(market["display"])
    return prices, verification, sorted(unmatched_markets), sorted(unmatched_commodities)
