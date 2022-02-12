from unittest.mock import MagicMock

from result import Ok, Result
from result.result import Err

from app.core.btc_constants import INITIAL_WALLET_VALUE_SATOSHIS, SATOSHI_IN_BTC
from app.core.currency_converter import ConversionError, FiatCurrency
from app.core.user.entity import User
from app.core.user.interactor import IUserRepository
from app.core.wallet.entity import Wallet
from app.core.wallet.interactor import (
    CreateWalletRequest,
    GetWalletRequest,
    IWalletRepository,
    WalletError,
    WalletInteractor,
    WalletResponse,
    IWalletInteractor,
)


class FakeCurrencyConverter:
    def convert_btc_to_fiat(
        self, satoshis: int, currency: FiatCurrency
    ) -> Result[float, ConversionError]:
        return Ok(satoshis * 2)


def wallet_address_creator() -> str:
    return "wallet address"


def test_create_wallet_magin_mock() -> None:
    wallet_address = wallet_address_creator()
    user_api_key = "bla"

    fake_wallet_repository = MagicMock()
    fake_wallet_repository.create_wallet = MagicMock(
        return_value=Wallet(wallet_address, user_api_key, INITIAL_WALLET_VALUE_SATOSHIS)
    )
    fake_wallet_repository.get_user_wallets = MagicMock(
        return_value=[
            Wallet(wallet_address, user_api_key, INITIAL_WALLET_VALUE_SATOSHIS)
        ]
    )

    fake_user_repository = MagicMock()
    fake_user_repository.get_user = MagicMock(return_value=User(user_api_key))

    wallet_interactor = WalletInteractor(
        fake_wallet_repository,
        fake_user_repository,
        FakeCurrencyConverter(),
        wallet_address_creator,
    )
    response = wallet_interactor.create_wallet(CreateWalletRequest(user_api_key))

    fake_user_repository.get_user.assert_called_once_with(user_api_key)
    fake_wallet_repository.create_wallet.assert_called_once()

    assert isinstance(response, Ok)
    assert response.value.wallet_address == wallet_address
    assert response.value.balance_btc == INITIAL_WALLET_VALUE_SATOSHIS / SATOSHI_IN_BTC
    assert response.value.balance_usd == INITIAL_WALLET_VALUE_SATOSHIS * 2


def test_create_wallet(
    wallet_repository: IWalletRepository, user_repository: IUserRepository
) -> None:

    test_user_api = "Dummy Key"

    user_repository.create_user(test_user_api)

    interactor = WalletInteractor(
        wallet_repository,
        user_repository,
        FakeCurrencyConverter(),
        wallet_address_creator,
    )

    result_err_no_user = interactor.create_wallet(CreateWalletRequest(""))
    assert isinstance(result_err_no_user, Err)
    assert result_err_no_user.value == WalletError.USER_NOT_FOUND

    result_ok = interactor.create_wallet(CreateWalletRequest(test_user_api))
    assert isinstance(result_ok, Ok)
    assert result_ok.value.wallet_address == wallet_address_creator()
    assert result_ok.value.balance_btc == INITIAL_WALLET_VALUE_SATOSHIS / SATOSHI_IN_BTC
    assert result_ok.value.balance_usd == INITIAL_WALLET_VALUE_SATOSHIS * 2

    interactor.create_wallet(CreateWalletRequest(test_user_api))
    interactor.create_wallet(CreateWalletRequest(test_user_api))

    result_err_wallet_limit = interactor.create_wallet(
        CreateWalletRequest(test_user_api)
    )
    assert isinstance(result_err_wallet_limit, Err)
    assert result_err_wallet_limit.value == WalletError.WALLET_LIMIT_REACHED


def test_create_wallet_user_not_found_no_user(
    wallet_interactor: IWalletInteractor, user_repository: IUserRepository
) -> None:
    wallet_creating_attempt_with_no_user = wallet_interactor.create_wallet(
        CreateWalletRequest("")
    )
    assert isinstance(wallet_creating_attempt_with_no_user, Err)
    assert wallet_creating_attempt_with_no_user.value == WalletError.USER_NOT_FOUND


def test_create_wallet_user_not_found_fake_user(
    wallet_interactor: IWalletInteractor, user_repository: IUserRepository
) -> None:
    fake_user_api = "Fake Key"
    wallet_creating_attempt_with_fake_user = wallet_interactor.create_wallet(
        CreateWalletRequest(fake_user_api)
    )
    assert isinstance(wallet_creating_attempt_with_fake_user, Err)
    assert wallet_creating_attempt_with_fake_user.value == WalletError.USER_NOT_FOUND


def test_create_wallet_with_correct_user(
    wallet_interactor: IWalletInteractor, user_repository: IUserRepository
) -> None:
    test_user_api = "Dummy Key"
    user_repository.create_user(test_user_api)

    wallet_creating_attempt_with_real_api = wallet_interactor.create_wallet(
        CreateWalletRequest(test_user_api)
    )
    assert isinstance(wallet_creating_attempt_with_real_api, Ok)

    successfully_created_wallet = wallet_creating_attempt_with_real_api.value
    assert successfully_created_wallet.wallet_address == wallet_address_creator()
    assert (
        successfully_created_wallet.balance_btc
        == INITIAL_WALLET_VALUE_SATOSHIS / SATOSHI_IN_BTC
    )
    assert successfully_created_wallet.balance_usd == INITIAL_WALLET_VALUE_SATOSHIS * 2


def test_create_wallet_multiple_wallets(
    wallet_interactor: IWalletInteractor,
    user_repository: IUserRepository,
    wallet_repository: IWalletRepository,
) -> None:
    test_user_api = "Dummy Key"
    user_repository.create_user(test_user_api)

    assert len(wallet_repository.get_user_wallets(test_user_api)) == 0
    assert isinstance(
        wallet_interactor.create_wallet(CreateWalletRequest(test_user_api)), Ok
    )
    assert len(wallet_repository.get_user_wallets(test_user_api)) == 1
    assert isinstance(
        wallet_interactor.create_wallet(CreateWalletRequest(test_user_api)), Ok
    )
    assert len(wallet_repository.get_user_wallets(test_user_api)) == 2
    assert isinstance(
        wallet_interactor.create_wallet(CreateWalletRequest(test_user_api)), Ok
    )
    assert len(wallet_repository.get_user_wallets(test_user_api)) == 3


def test_create_wallet_limit_reached(
    wallet_interactor: IWalletInteractor, user_repository: IUserRepository
) -> None:
    test_user_api = "Dummy Key"
    user_repository.create_user(test_user_api)

    wallet_interactor.create_wallet(CreateWalletRequest(test_user_api))
    wallet_interactor.create_wallet(CreateWalletRequest(test_user_api))
    wallet_interactor.create_wallet(CreateWalletRequest(test_user_api))

    wallet_creating_attempt_with_limit_reached = wallet_interactor.create_wallet(
        CreateWalletRequest(test_user_api)
    )
    assert isinstance(wallet_creating_attempt_with_limit_reached, Err)
    assert (
        wallet_creating_attempt_with_limit_reached.value
        == WalletError.WALLET_LIMIT_REACHED
    )


def test_get_wallet(
    wallet_repository: IWalletRepository, user_repository: IUserRepository
) -> None:
    test_user_api = "Dummy Key"

    user_repository.create_user(test_user_api)
    interactor = WalletInteractor(
        wallet_repository,
        user_repository,
        FakeCurrencyConverter(),
        wallet_address_creator,
    )
    response = interactor.create_wallet(CreateWalletRequest(test_user_api))
    assert isinstance(response, Ok)
    new_wallet: WalletResponse = response.value

    result_err_no_user = interactor.get_wallet(
        GetWalletRequest("", new_wallet.wallet_address)
    )
    assert isinstance(result_err_no_user, Err)
    assert result_err_no_user.value == WalletError.USER_NOT_FOUND

    result_err_no_wallet = interactor.get_wallet(GetWalletRequest(test_user_api, ""))
    assert isinstance(result_err_no_wallet, Err)
    assert result_err_no_wallet.value == WalletError.WALLET_NOT_FOUND

    wallet = interactor.get_wallet(
        GetWalletRequest(test_user_api, new_wallet.wallet_address)
    )
    assert isinstance(wallet, Ok)
    assert wallet.value.wallet_address == new_wallet.wallet_address
    assert wallet.value.balance_btc == new_wallet.balance_btc
    assert wallet.value.balance_usd == new_wallet.balance_usd


def test_get_wallet_user_not_found_no_user(
    wallet_interactor: IWalletInteractor, user_repository: IUserRepository
) -> None:
    wallet_acquiring_attempt_with_no_user = wallet_interactor.get_wallet(
        GetWalletRequest("", "aaa")
    )
    assert isinstance(wallet_acquiring_attempt_with_no_user, Err)
    assert wallet_acquiring_attempt_with_no_user.value == WalletError.USER_NOT_FOUND


def test_get_wallet_user_not_found_fake_user(
    wallet_interactor: IWalletInteractor, user_repository: IUserRepository
) -> None:
    fake_user_api = "Fake Key"
    wallet_acquiring_attempt_with_fake_user = wallet_interactor.get_wallet(
        GetWalletRequest(fake_user_api, "aaa")
    )
    assert isinstance(wallet_acquiring_attempt_with_fake_user, Err)
    assert wallet_acquiring_attempt_with_fake_user.value == WalletError.USER_NOT_FOUND


def test_get_wallet_wallet_not_found_no_wallet(
    wallet_interactor: IWalletInteractor, user_repository: IUserRepository
) -> None:
    test_user_api = "Dummy Key"
    user_repository.create_user(test_user_api)

    wallet_acquiring_attempt_with_no_wallet = wallet_interactor.get_wallet(
        GetWalletRequest(test_user_api, "aaa")
    )
    assert isinstance(wallet_acquiring_attempt_with_no_wallet, Err)
    assert wallet_acquiring_attempt_with_no_wallet.value == WalletError.WALLET_NOT_FOUND


def test_get_wallet_wallet_not_found_fake_wallet(
    wallet_interactor: IWalletInteractor, user_repository: IUserRepository
) -> None:
    test_user_api = "Dummy Key"
    user_repository.create_user(test_user_api)

    fake_wallet_address = "Fake Address"
    wallet_acquiring_attempt_with_fake_wallet = wallet_interactor.get_wallet(
        GetWalletRequest(test_user_api, fake_wallet_address)
    )
    assert isinstance(wallet_acquiring_attempt_with_fake_wallet, Err)
    assert (
        wallet_acquiring_attempt_with_fake_wallet.value == WalletError.WALLET_NOT_FOUND
    )


def test_get_wallet_with_correct_user_matched_wallet(
    wallet_interactor: IWalletInteractor, user_repository: IUserRepository
) -> None:
    test_user_api = "Dummy Key"
    user_repository.create_user(test_user_api)

    wallet_creating_attempt_with_real_api = wallet_interactor.create_wallet(
        CreateWalletRequest(test_user_api)
    )
    successfully_created_wallet = wallet_creating_attempt_with_real_api.value
    test_wallet_address = successfully_created_wallet.wallet_address

    wallet_acquiring_attempt_with_real_api_matched_wallet = (
        wallet_interactor.get_wallet(
            GetWalletRequest(test_user_api, test_wallet_address)
        )
    )
    assert isinstance(wallet_acquiring_attempt_with_real_api_matched_wallet, Ok)

    successfully_acquired_wallet = (
        wallet_acquiring_attempt_with_real_api_matched_wallet.value
    )
    assert successfully_acquired_wallet.wallet_address == test_wallet_address
    assert (
        successfully_acquired_wallet.balance_btc
        == INITIAL_WALLET_VALUE_SATOSHIS / SATOSHI_IN_BTC
    )
    assert successfully_acquired_wallet.balance_usd == INITIAL_WALLET_VALUE_SATOSHIS * 2


def test_get_wallet_with_correct_user_mismatched_wallet(
    wallet_interactor_real_generator: IWalletInteractor,
    user_repository: IUserRepository,
) -> None:
    first_test_user_api = "Dummy Key"
    user_repository.create_user(first_test_user_api)

    second_test_user_api = "Dummy Key As well"
    user_repository.create_user(second_test_user_api)

    wallet_creating_attempt_with_real_api = (
        wallet_interactor_real_generator.create_wallet(
            CreateWalletRequest(second_test_user_api)
        )
    )
    successfully_created_second_wallet = wallet_creating_attempt_with_real_api.value
    second_test_wallet_address = successfully_created_second_wallet.wallet_address

    wallet_acquiring_attempt_with_real_api_mismatched_wallet = (
        wallet_interactor_real_generator.get_wallet(
            GetWalletRequest(first_test_user_api, second_test_wallet_address)
        )
    )
    assert isinstance(wallet_acquiring_attempt_with_real_api_mismatched_wallet, Err)
    assert (
        wallet_acquiring_attempt_with_real_api_mismatched_wallet.value
        == WalletError.NOT_THIS_USERS_WALLET
    )
