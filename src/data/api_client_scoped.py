import time
import requests
from .api_client import API_URL, APIError


class APIClient:
    """Use district-scoped requests because market-filter queries can hang on AGMARKNET."""
    def __init__(self, api_key, timeout=(5, 15), retries=1, session=None):
        self.api_key, self.timeout, self.retries = api_key, timeout, retries
        self.session, self.cache = session or requests.Session(), {}

    def records_for_scope(self, state, district):
        key = (state, district)
        if key in self.cache:
            return self.cache[key]
        records, offset = [], 0
        page_size = 50
        while True:
            params = {"api-key": self.api_key, "format": "json", "limit": page_size, "offset": offset,
                      "filters[state]": state}
            if district:
                params["filters[district]"] = district
            last_error = None
            for attempt in range(self.retries + 1):
                try:
                    print(f"REQUEST scope={state}/{district or '*'} offset={offset}", flush=True)
                    response = self.session.get(API_URL, params=params, timeout=self.timeout)
                    response.raise_for_status()
                    payload = response.json()
                    batch = payload.get("records", [])
                    records.extend(batch)
                    total = int(payload.get("total", len(records)))
                    if not batch or len(records) >= total or len(batch) < page_size:
                        self.cache[key] = records
                        return records
                    offset += len(batch)
                    break
                except (requests.RequestException, ValueError) as exc:
                    last_error = exc
                    print(f"  attempt {attempt + 1} failed: {type(exc).__name__}", flush=True)
                    if attempt < self.retries:
                        time.sleep(1)
            else:
                raise APIError(f"API failed for scope {state}/{district or '*'}: {last_error}")
