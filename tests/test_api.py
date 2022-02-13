from fastapi.testclient import TestClient

from app.core.admin.interactor import ADMIN_KEY

API_ADMIN_KEY = "admin_key"
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


def test_url_existence(api_client: TestClient) -> None:
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
            API_ADMIN_KEY: ADMIN_KEY,
        },
    )
    assert response_stats.status_code == StatusCode.OK
