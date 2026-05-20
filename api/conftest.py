import os
import socket
import time

import pytest
import requests

from api_manager import ApiManager


BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
DEMO_EMAIL = os.getenv("DEMO_USER_EMAIL", "test@taskflow.io")
DEMO_PASSWORD = os.getenv("DEMO_USER_PASSWORD", "Test123!")


def _wait_for_server(url: str, timeout: float = 10.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{url}/v1/health", timeout=1)
            if r.ok:
                return
        except requests.RequestException:
            pass
        time.sleep(0.2)
    raise RuntimeError(f"backend at {url} did not become healthy in {timeout}s")


@pytest.fixture(scope="session", autouse=True)
def _backend_healthcheck():
    _wait_for_server(BASE_URL)


@pytest.fixture(scope="session")
def http_session():
    # one session for the whole test run — keeps TCP+TLS alive and shares
    # default headers across every request
    s = requests.Session()
    s.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    yield s
    s.close()


@pytest.fixture(scope="session")
def auth_token(http_session):
    # POST /auth/login once per run; share the JWT everywhere
    r = http_session.post(
        f"{BASE_URL}/v1/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
        timeout=5,
    )
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def auth_session(http_session, auth_token):
    http_session.headers["Authorization"] = f"Bearer {auth_token}"
    return http_session


@pytest.fixture(scope="class")
def api_manager(auth_session):
    return ApiManager(auth_session, BASE_URL)


@pytest.fixture
def clean_tasks(api_manager):
    # wipe before each test that asks for it. Most tests should.
    api_manager.tasks.clear()
    yield
