from typing import List

from result import Err, Ok

from app.core.btc_constants import SATOSHI_IN_BTC
from app.core.transaction.interactor import (
    GetTransactionsRequest,
    MakeTransactionRequest,
    TransactionError,
    TransactionInteractor,
)
from app.core.user.interactor import IUserRepository
from app.core.wallet.entity import Wallet
from app.core.wallet.interactor import IWalletRepository
from tests.conftest import IAdminAndTransactionRepository


class TestingFeeCalculator:
    def __call__(
        self, source_wallet: Wallet, destination_wallet: Wallet, transfer_amount: int
    ) -> int:
        if source_wallet.owner_key == destination_wallet.owner_key:
            return 0
        else:
            return round(transfer_amount * 0.1)


def test_make_transaction_one_user(
    user_repository: IUserRepository,
    wallet_repository: IWalletRepository,
    transaction_repository: IAdminAndTransactionRepository,
) -> None:
    interactor = TransactionInteractor(
        transaction_repository,
        user_repository,
        wallet_repository,
        TestingFeeCalculator(),
    )

    user_api_key = "User Key"
    user_repository.create_user(user_api_key)

    init_balance = 10000
    wallet_address_1 = "Wallet Address 1"
    wallet_address_2 = "Wallet Address 2"
    wallet_repository.create_wallet(user_api_key, wallet_address_1, init_balance)
    wallet_repository.create_wallet(user_api_key, wallet_address_2, init_balance)

    response_err_no_user = interactor.make_transaction(
        MakeTransactionRequest(
            user_api_key="Blaa",
            source_address=wallet_address_1,
            destination_address=wallet_address_2,
            amount=1,
        )
    )

    assert isinstance(response_err_no_user, Err)
    assert response_err_no_user.value == TransactionError.USER_NOT_FOUND

    transfer_amount = 5000

    response_ok = interactor.make_transaction(
        MakeTransactionRequest(
            user_api_key=user_api_key,
            source_address=wallet_address_1,
            destination_address=wallet_address_2,
            amount=transfer_amount,
        )
    )
    assert isinstance(response_ok, Ok)
    assert (
        response_ok.value.amount_left_btc
        == (init_balance - transfer_amount) / SATOSHI_IN_BTC
    )

    response_err_no_src = interactor.make_transaction(
        MakeTransactionRequest(
            user_api_key=user_api_key,
            source_address="",
            destination_address=wallet_address_2,
            amount=transfer_amount,
        )
    )
    response_err_no_dest = interactor.make_transaction(
        MakeTransactionRequest(
            user_api_key=user_api_key,
            source_address=wallet_address_1,
            destination_address="",
            amount=transfer_amount,
        )
    )

    assert isinstance(response_err_no_src, Err) and isinstance(
        response_err_no_dest, Err
    )
    assert response_err_no_src.value == TransactionError.SOURCE_WALLET_NOT_FOUND
    assert response_err_no_dest.value == TransactionError.DESTINATION_WALLET_NOT_FOUND

    response_err_not_enough = interactor.make_transaction(
        MakeTransactionRequest(
            user_api_key=user_api_key,
            source_address=wallet_address_1,
            destination_address=wallet_address_2,
            amount=init_balance**2,
        )
    )

    assert isinstance(response_err_not_enough, Err)
    assert (
        response_err_not_enough.value
        == TransactionError.NOT_ENOUGH_AMOUNT_ON_SOURCE_ACCOUNT
    )


def test_make_transaction_two_users(
    user_repository: IUserRepository,
    wallet_repository: IWalletRepository,
    transaction_repository: IAdminAndTransactionRepository,
) -> None:
    interactor = TransactionInteractor(
        transaction_repository,
        user_repository,
        wallet_repository,
        TestingFeeCalculator(),
    )

    user_api_key_1 = "User Key 1"
    user_api_key_2 = "User Key 2"
    user_repository.create_user(user_api_key_1)
    user_repository.create_user(user_api_key_2)

    init_balance = 10000
    wallet_address_1 = "Wallet Address 1"
    wallet_address_2 = "Wallet Address 2"
    wallet_repository.create_wallet(user_api_key_1, wallet_address_1, init_balance)
    wallet_repository.create_wallet(user_api_key_2, wallet_address_2, init_balance)

    transfer_amount = 100

    response_ok = interactor.make_transaction(
        MakeTransactionRequest(
            user_api_key=user_api_key_1,
            source_address=wallet_address_1,
            destination_address=wallet_address_2,
            amount=transfer_amount,
        )
    )

    assert isinstance(response_ok, Ok)
    assert (
        response_ok.value.amount_left_btc
        == (init_balance - transfer_amount) / SATOSHI_IN_BTC
    )

    wallet_2 = wallet_repository.get_wallet(wallet_address_2)
    assert wallet_2 is not None
    assert wallet_2.balance == (init_balance + transfer_amount * 0.9)

    response_incr_api_key = interactor.make_transaction(
        MakeTransactionRequest(
            user_api_key=user_api_key_2,
            source_address=wallet_address_1,
            destination_address=wallet_address_2,
            amount=transfer_amount,
        )
    )

    assert isinstance(response_incr_api_key, Err)
    assert response_incr_api_key.value == TransactionError.INCORRECT_API_KEY


def test_get_transactions(
    user_repository: IUserRepository,
    wallet_repository: IWalletRepository,
    transaction_repository: IAdminAndTransactionRepository,
) -> None:
    interactor = TransactionInteractor(
        transaction_repository,
        user_repository,
        wallet_repository,
        TestingFeeCalculator(),
    )

    user_api_key_1 = "User Key 1"
    user_api_key_2 = "User Key 2"
    user_repository.create_user(user_api_key_1)
    user_repository.create_user(user_api_key_2)

    init_balance = 10000000
    transfer_amount = 100

    user_1_wallets: List[Wallet] = []
    user_2_wallets: List[Wallet] = []

    for i in range(100):
        user_1_wallets.append(
            wallet_repository.create_wallet(
                user_api_key_1, f"Wallet {i} of User 1", init_balance
            )
        )
        user_2_wallets.append(
            wallet_repository.create_wallet(
                user_api_key_2, f"Wallet {i} of User 2", init_balance
            )
        )

    response_ok_1 = interactor.get_transactions(GetTransactionsRequest(user_api_key_1))
    response_ok_2 = interactor.get_transactions(GetTransactionsRequest(user_api_key_2))

    assert isinstance(response_ok_1, Ok) and isinstance(response_ok_2, Ok)
    assert len(response_ok_1.value.transactions) == 0
    assert len(response_ok_2.value.transactions) == 0

    for a, b in zip(user_1_wallets, user_2_wallets):
        r1 = interactor.make_transaction(
            MakeTransactionRequest(
                user_api_key=user_api_key_1,
                source_address=a.address,
                destination_address=b.address,
                amount=transfer_amount,
            )
        )
        assert isinstance(r1, Ok)

        r2 = interactor.make_transaction(
            MakeTransactionRequest(
                user_api_key=user_api_key_2,
                source_address=b.address,
                destination_address=a.address,
                amount=transfer_amount,
            )
        )
        assert isinstance(r2, Ok)

    transactions_num = len(user_1_wallets) + len(user_2_wallets)

    response_ok_1 = interactor.get_transactions(GetTransactionsRequest(user_api_key_1))
    response_ok_2 = interactor.get_transactions(GetTransactionsRequest(user_api_key_2))

    assert isinstance(response_ok_1, Ok) and isinstance(response_ok_2, Ok)
    assert len(response_ok_1.value.transactions) == transactions_num
    assert len(response_ok_2.value.transactions) == transactions_num

    response_err_no_wallet = interactor.get_transactions(
        GetTransactionsRequest(user_api_key_1, "")
    )
    assert isinstance(response_err_no_wallet, Err)
    assert response_err_no_wallet.value == TransactionError.WALLET_NOT_FOUND

    for u, ws in [(user_api_key_1, user_1_wallets), (user_api_key_2, user_2_wallets)]:
        for w in ws:
            r = interactor.get_transactions(GetTransactionsRequest(u, w.address))
            assert isinstance(r, Ok)
            assert len(r.value.transactions) == 2
