"""Fixture search is default. Live adapter needs an explicit injected transport."""
import asyncio
from urllib.parse import urlparse

class SearchFailure(RuntimeError): pass

def normalize(record, query_id, provider):
    url = record["url"]
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http") or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("invalid source URL")
    for field in ("id", "title", "text", "topic", "value"):
        if not isinstance(record.get(field), str) or not record[field]:
            raise ValueError(f"missing source {field}")
    return {**record, "query_id": query_id, "provider": provider,
            "published": record.get("published"), "retrieved": record.get("retrieved")}

class FixtureSearch:
    def __init__(self, records): self.records = records
    async def search(self, query):
        await asyncio.sleep(0)
        terms = set(query["text"].lower().split())
        return [normalize(r, query["id"], "academy-synthetic-fixture") for r in self.records
                if r["topic"].lower() in terms]

class LiveSearch:
    """Transport returns normalized provider records; no credential or URL is built in.

    The application, not a research question, chooses transport/endpoint. Pass a
    restricted HTTPS provider client after explicit configuration and consent.
    This class never fetches arbitrary result URLs or retries a paid request.
    """
    def __init__(self, transport, *, enabled=False, timeout=15):
        if not enabled: raise ValueError("live search requires explicit opt-in")
        if not 0 < timeout <= 60: raise ValueError("bounded timeout required")
        self.transport, self.timeout = transport, timeout
    async def search(self, query):
        rows = await asyncio.wait_for(self.transport(query["text"]), self.timeout)
        return [normalize(r, query["id"], "configured-live-provider") for r in rows]

async def parallel_search(queries, backend, workers=3):
    if not 1 <= workers <= 8: raise ValueError("workers must be 1..8")
    sem = asyncio.Semaphore(workers)
    async def one(query):
        async with sem:
            try:
                return {"query": query, "sources": await backend.search(query), "error": None}
            except (TimeoutError, SearchFailure, ValueError) as error:
                return {"query": query, "sources": [], "error": type(error).__name__}
    return await asyncio.gather(*(one(q) for q in queries))
