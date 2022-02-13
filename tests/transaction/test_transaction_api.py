from typing import Callable, Dict

from starlette.testclient import TestClient

from app.core.btc_constants import INITIAL_WALLET_VALUE_SATOSHIS
from tests.test_api import API_ARG_KEY_NAME, WALLET_ADDRES_KEY_NAME, StatusCode


def test_api_error_messages_transaction(
    api_client: TestClient, from_msg: Callable[[str], Dict[str, str]]
) -> None:
    test_user_1 = api_client.post("/users").json()[API_ARG_KEY_NAME]
    test_user_2 = api_client.post("/users").json()[API_ARG_KEY_NAME]

    test_user_1_wallet = api_client.post(
        "/wallets", params={API_ARG_KEY_NAME: test_user_1}
    ).json()[WALLET_ADDRES_KEY_NAME]
    test_user_2_wallet = api_client.post(
        "/wallets", params={API_ARG_KEY_NAME: test_user_2}
    ).json()[WALLET_ADDRES_KEY_NAME]

    response_no_user = api_client.get("/transactions", params={API_ARG_KEY_NAME: ""})
    assert response_no_user.status_code == StatusCode.USER_NOT_FOUND
    assert response_no_user.json() == from_msg("User not found")

    response_no_wallet = api_client.get(
        "/wallets/no_wallet/transactions", params={API_ARG_KEY_NAME: test_user_1}
    )
    assert response_no_wallet.status_code == StatusCode.WALLET_NOT_FOUND
    assert response_no_wallet.json() == from_msg("Wallet not found")

    response_no_src_wallet = api_client.post(
        "/transactions",
        params={
            API_ARG_KEY_NAME: test_user_1,
            "source": "",
            "destination": test_user_1_wallet,
            "amount": 1,
        },
    )
    response_no_dest_wallet = api_client.post(
        "/transactions",
        params={
            API_ARG_KEY_NAME: test_user_1,
            "source": test_user_1_wallet,
            "destination": "",
            "amount": 1,
        },
    )

    assert response_no_src_wallet.status_code == StatusCode.NO_SOURCE_WALLET
    assert response_no_src_wallet.json() == from_msg(
        "Transactions's source wallet not found"
    )
    assert response_no_dest_wallet.status_code == StatusCode.NO_DESTINATION_WALLET
    assert response_no_dest_wallet.json() == from_msg(
        "Transaction's destination wallet not found"
    )

    response_no_couns = api_client.post(
        "/transactions",
        params={
            API_ARG_KEY_NAME: test_user_2,
            "source": test_user_1_wallet,
            "destination": test_user_2_wallet,
            "amount": 1,
        },
    )
    assert response_no_couns.status_code == StatusCode.UNAUTHORIZED
    assert response_no_couns.json() == from_msg(
        "Provided api key does not own source wallet"
    )

    response_no_couns = api_client.post(
        "/transactions",
        params={
            API_ARG_KEY_NAME: test_user_1,
            "source": test_user_1_wallet,
            "destination": test_user_2_wallet,
            "amount": INITIAL_WALLET_VALUE_SATOSHIS**2,
        },
    )
    assert response_no_couns.status_code == StatusCode.INSUFFICIENT_FUNDS
    assert response_no_couns.json() == from_msg(
        "Not enough coins on source wallet to complete transaction"
    )
