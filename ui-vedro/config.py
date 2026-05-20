import os
from dataclasses import dataclass


@dataclass(frozen=True)
class _AppConfig:
    base_url: str
    api_base_url: str
    app_port: int


app = _AppConfig(
    base_url=os.getenv("BASE_URL", "http://127.0.0.1:5173"),
    api_base_url=os.getenv("API_BASE_URL", "http://127.0.0.1:5173/api"),
    app_port=int(os.getenv("APP_PORT", "5173")),
)
