import re


def clean(value):
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def match_commodity(actual, config):
    raw = str(actual or "").strip().lower()
    actual_clean = clean(raw)
    for alias in config["aliases"]:
        wanted = clean(alias)
        if actual_clean == wanted:
            return True
        if raw.startswith(alias.lower()) and len(raw) > len(alias) and raw[len(alias)] in " ([-/":
            return True
    return False



def number(value):
    try:
        parsed = float(str(value).replace(",", "").strip())
        return parsed if parsed >= 0 else None
    except (TypeError, ValueError):
        return None


def normalized_record(record, market, commodity, target_date):
    modal = number(record.get("modal_price"))
    minimum = number(record.get("min_price"))
    maximum = number(record.get("max_price"))
    if modal is None and minimum is None and maximum is None:
        return None
    return {
        "market": market["display"], "api_market": record.get("market"),
        "commodity": commodity["name"], "api_commodity": record.get("commodity"),
        "date": target_date, "min_price_quintal": minimum,
        "max_price_quintal": maximum, "modal_price_quintal": modal,
        "min_price_kg": minimum / 100 if minimum is not None else None,
        "max_price_kg": maximum / 100 if maximum is not None else None,
        "modal_price_kg": modal / 100 if modal is not None else None,
        "source": "AGMARKNET / data.gov.in",
    }
