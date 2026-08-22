import time
import requests
from .api_client import API_URL, APIError


class APIClient:
    def __init__(self, api_key, timeout=(5, 10), retries=1, session=None):
        self.api_key, self.timeout, self.retries = api_key, timeout, retries
        self.session, self.cache = session or requests.Session(), {}

    def records_for_market(self, market):
        key = (market["state"], market.get("district"), tuple(market["aliases"]))
        if key in self.cache:
            return self.cache[key]
        combined, seen, errors = [], set(), []
        for alias in market["aliases"]:
            print(f"REQUEST {market['display']} / {alias}", flush=True)
            params = {"api-key": self.api_key, "format": "json", "limit": 100, "filters[state]": market["state"], "filters[market]": alias}
            if market.get("district"):
                params["filters[district]"] = market["district"]
            for attempt in range(self.retries + 1):
                try:
                    response = self.session.get(API_URL, params=params, timeout=self.timeout)
                    response.raise_for_status()
                    for record in response.json().get("records", []):
                        identity = tuple(sorted(record.items()))
                        if identity not in seen:
                            seen.add(identity); combined.append(record)
                    break
                except (requests.RequestException, ValueError) as exc:
                    errors.append(f"{alias}: {exc}")
                    print(f"  attempt {attempt + 1} failed: {type(exc).__name__}", flush=True)
                    if attempt < self.retries: time.sleep(2 ** attempt)
        if errors and not combined:
            raise APIError(f"API failed for {market['display']}: {'; '.join(errors[-2:])}")
        self.cache[key] = combined
        return combined
