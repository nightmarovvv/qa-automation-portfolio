from typing import Optional

import requests

from custom_requester import CustomRequester


class AuthAPI(CustomRequester):
    LOGIN = "/v1/auth/login"

    def login(
        self,
        email: str,
        password: str,
        expected_status: Optional[int] = 200,
    ) -> requests.Response:
        return self.send_request(
            "POST",
            self.LOGIN,
            json_body={"email": email, "password": password},
            expected_status=expected_status,
        )
