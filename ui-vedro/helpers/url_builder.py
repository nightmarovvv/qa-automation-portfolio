# Pure URL helpers. No Page, no IO — those belong in contexts/steps.

from urllib.parse import urlencode

from config import app


def app_url(*parts: str, **query: str) -> str:
    path = "/".join(p.strip("/") for p in parts if p)
    base = f"{app.base_url.rstrip('/')}/{path}" if path else app.base_url.rstrip("/")
    return f"{base}?{urlencode(query)}" if query else base


def api_url(*parts: str, **query: str) -> str:
    path = "/".join(p.strip("/") for p in parts if p)
    base = f"{app.api_base_url.rstrip('/')}/{path}"
    return f"{base}?{urlencode(query)}" if query else base
