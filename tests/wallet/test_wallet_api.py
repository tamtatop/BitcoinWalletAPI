from typing import Callable, Dict

from starlette.testclient import TestClient

from app.core.wallet.interactor import MAX_WALLETS_PER_PERSON
from tests.test_api import API_ARG_KEY_NAME, WALLET_ADDRES_KEY_NAME, StatusCode


def test_api_error_messages_wallet(
    api_client: TestClient, from_msg: Callable[[str], Dict[str, str]]
) -> None:
    test_user_1 = api_client.post("/users").json()[API_ARG_KEY_NAME]
    test_user_2 = api_client.post("/users").json()[API_ARG_KEY_NAME]

    response_create_wallet = api_client.post("/wallets", params={API_ARG_KEY_NAME: ""})
    assert response_create_wallet.status_code == StatusCode.USER_NOT_FOUND
    assert response_create_wallet.json() == from_msg("User not found")

    response_get_wallet = api_client.get(
        "/wallets/no_wallet",
        params={
            API_ARG_KEY_NAME: test_user_1,
        },
    )
    assert response_get_wallet.status_code == StatusCode.WALLET_NOT_FOUND
    assert response_get_wallet.json() == from_msg("Wallet not found")

    test_user_2_wallet = api_client.post(
        "/wallets", params={API_ARG_KEY_NAME: test_user_2}
    ).json()[WALLET_ADDRES_KEY_NAME]

    assert (
        api_client.post("/wallets", params={API_ARG_KEY_NAME: test_user_2}).status_code
        == StatusCode.OK
    )
    assert (
        api_client.post("/wallets", params={API_ARG_KEY_NAME: test_user_2}).status_code
        == StatusCode.OK
    )

    response_wallet_limit = api_client.post(
        "/wallets", params={API_ARG_KEY_NAME: test_user_2}
    )
    assert response_wallet_limit.status_code == StatusCode.MAX_WALLETS_REACHED
    assert response_wallet_limit.json() == from_msg(
        f"Cannot create more than {MAX_WALLETS_PER_PERSON} wallets"
    )

    response_belonging_error = api_client.get(
        f"/wallets/{test_user_2_wallet}",
        params={
            API_ARG_KEY_NAME: test_user_1,
        },
    )
    assert response_belonging_error.status_code == StatusCode.UNAUTHORIZED
    assert response_belonging_error.json() == from_msg(
        "Provided wallet doesn't belong to provided user"
    )
