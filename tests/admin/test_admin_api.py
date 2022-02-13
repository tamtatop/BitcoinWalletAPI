from typing import Callable, Dict

from starlette.testclient import TestClient

from tests.test_api import API_ARG_KEY_NAME, StatusCode


def test_api_error_messages_admin(
    api_client: TestClient, from_msg: Callable[[str], Dict[str, str]]
) -> None:
    response = api_client.get(
        "/statistics",
        params={
            API_ARG_KEY_NAME: "hacker",
        },
    )
    assert response.status_code == StatusCode.WRONG_ADMIN_KEY
    assert response.json() == from_msg("Incorrect api key for admin")
