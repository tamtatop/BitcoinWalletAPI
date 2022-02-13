from typing import Callable, Dict

from fastapi.testclient import TestClient

from app.core.admin.interactor import ADMIN_KEY
from app.core.btc_constants import INITIAL_WALLET_VALUE_SATOSHIS
from app.core.wallet.interactor import MAX_WALLETS_PER_PERSON

API_ARG_KEY_NAME = "api_key"
WALLET_ADDRES_KEY_NAME = "wallet_address"
TRANSACTIONS_KEY_NAME = "transactions"


class StatusCode:
    OK = 200

    API_ENDPOINT_NOT_FOUND = 404

    USER_NOT_FOUND = 410
    WALLET_NOT_FOUND = 411
    NO_SOURCE_WALLET = 412
    NO_DESTINATION_WALLET = 413
    UNAUTHORIZED = 414
    INSUFFICIENT_FUNDS = 415
    MAX_WALLETS_REACHED = 412
    WRONG_ADMIN_KEY = 410


def test_url_existance(api_client: TestClient) -> None:
    invalid_url = "/if_you_make_request_to_this_url_you_will_get_A_in_Design_Patterns"

    assert api_client.get(invalid_url).status_code == StatusCode.API_ENDPOINT_NOT_FOUND
    assert api_client.post(invalid_url).status_code == StatusCode.API_ENDPOINT_NOT_FOUND

    response_user_created = api_client.post("/users")
    assert response_user_created.status_code == StatusCode.OK

    user_api_key = response_user_created.json()[API_ARG_KEY_NAME]

    response_wallet_created = api_client.post(
        "/wallets", params={API_ARG_KEY_NAME: user_api_key}
    )
    assert response_wallet_created.status_code == StatusCode.OK

    wallet_1 = response_wallet_created.json()

    response_get_wallet = api_client.get(
        f"/wallets/{wallet_1[WALLET_ADDRES_KEY_NAME]}",
        params={
            API_ARG_KEY_NAME: user_api_key,
        },
    )
    assert response_get_wallet.status_code == StatusCode.OK

    wallet_2 = api_client.post(
        "/wallets", params={API_ARG_KEY_NAME: user_api_key}
    ).json()

    assert wallet_1[WALLET_ADDRES_KEY_NAME] != wallet_2[WALLET_ADDRES_KEY_NAME]

    response_make_transaction = api_client.post(
        "/transactions",
        params={
            API_ARG_KEY_NAME: user_api_key,
            "source": wallet_1[WALLET_ADDRES_KEY_NAME],
            "destination": wallet_2[WALLET_ADDRES_KEY_NAME],
            "amount": 1000,
        },
    )
    assert response_make_transaction.status_code == StatusCode.OK

    response_get_transactions = api_client.get(
        "/transactions", params={API_ARG_KEY_NAME: user_api_key}
    )
    assert response_get_transactions.status_code == StatusCode.OK

    user_transactions = response_get_transactions.json()[TRANSACTIONS_KEY_NAME]
    assert len(user_transactions) == 1

    response_get_wallet_transactions = api_client.get(
        f"/wallets/{wallet_1[WALLET_ADDRES_KEY_NAME]}/transactions",
        params={
            API_ARG_KEY_NAME: user_api_key,
        },
    )
    assert response_get_wallet_transactions.status_code == StatusCode.OK

    wallet_1_transactions = response_get_wallet_transactions.json()[
        TRANSACTIONS_KEY_NAME
    ]
    assert len(wallet_1_transactions) == 1

    assert user_transactions == wallet_1_transactions

    response_stats = api_client.get(
        "/statistics",
        params={
            API_ARG_KEY_NAME: ADMIN_KEY,
        },
    )
    assert response_stats.status_code == StatusCode.OK


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
        "Provided api key does now own source wallet"
    )

    response_no_couns = api_client.post(
        "/transactions",
        params={
            API_ARG_KEY_NAME: test_user_1,
            "source": test_user_1_wallet,
            "destination": test_user_2_wallet,
            "amount": INITIAL_WALLET_VALUE_SATOSHIS ** 2,
        },
    )
    assert response_no_couns.status_code == StatusCode.INSUFFICIENT_FUNDS
    assert response_no_couns.json() == from_msg(
        "Not enough coins on source wallet to complete transaction"
    )
