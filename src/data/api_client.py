import time
import requests

API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"


class APIError(RuntimeError):
    pass


class APIClient:
    def __init__(self, api_key, timeout=(10, 30), retries=2, session=None):
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries
        self.session = session or requests.Session()
        self.cache = {}

    def records_for_market(self, market):
        key = (market["state"], market["district"], tuple(market["aliases"]))
        if key in self.cache:
            return self.cache[key]
        errors = []
        for alias in market["aliases"]:
            params = {"api-key": self.api_key, "format": "json", "limit": 100,
                      "filters[state]": market["state"], "filters[market]": alias}
            if market.get("district"):
                params["filters[district]"] = market["district"]
            for attempt in range(self.retries + 1):
                try:
                    response = self.session.get(API_URL, params=params, timeout=self.timeout)
                    response.raise_for_status()
                    payload = response.json()
                    records = payload.get("records", [])
                    if records:
                        self.cache[key] = records
                        return records
                    break
                except (requests.RequestException, ValueError) as exc:
                    errors.append(f"{alias}: {exc}")
                    if attempt < self.retries:
                        time.sleep(2 ** attempt)
        if errors:
            raise APIError(f"API failed for {market['display']}: {'; '.join(errors[-2:])}")
        self.cache[key] = []
        return []
