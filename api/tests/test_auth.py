import os

import allure
import pytest
import requests

from api_manager import ApiManager

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


@allure.feature("Auth")
@allure.story("Login")
class TestAuthLogin:

    @allure.title("POST /auth/login with valid creds returns a bearer token")
    @pytest.mark.smoke
    def test_login_returns_token(self, http_session):
        api = ApiManager(http_session, BASE_URL)
        r = api.auth.login("test@taskflow.io", "Test123!")
        body = r.json()
        assert body["token_type"] == "Bearer"
        assert isinstance(body["access_token"], str) and len(body["access_token"]) > 20
        assert body["expires_in"] > 0

    @allure.title("Login with wrong password returns 401")
    @pytest.mark.negative
    def test_login_wrong_password(self, http_session):
        api = ApiManager(http_session, BASE_URL)
        r = api.auth.login("test@taskflow.io", "nope", expected_status=401)
        assert "bad credentials" in r.text.lower()

    @allure.title("Login with unknown email returns 401")
    @pytest.mark.negative
    def test_login_unknown_email(self, http_session):
        api = ApiManager(http_session, BASE_URL)
        api.auth.login("ghost@taskflow.io", "Test123!", expected_status=401)

    @allure.title("Tasks endpoints require bearer token")
    @pytest.mark.negative
    def test_tasks_require_auth(self):
        r = requests.get(f"{BASE_URL}/v1/tasks", timeout=5)
        assert r.status_code == 401

    @allure.title("Garbage token is rejected with 401")
    @pytest.mark.negative
    def test_tasks_bad_token(self):
        r = requests.get(
            f"{BASE_URL}/v1/tasks",
            headers={"Authorization": "Bearer not.a.jwt"},
            timeout=5,
        )
        assert r.status_code == 401
