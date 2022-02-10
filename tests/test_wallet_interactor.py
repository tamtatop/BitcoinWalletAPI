from unittest.mock import MagicMock

from result import Ok, Result

from app.core.user.interactor import User
from app.core.wallet.interactor import (
    INITIAL_WALLET_VALUE_SATOSHIS,
    ConversionError,
    CreateWalletRequest,
    FiatCurrency,
    GetWalletRequest,
    Wallet,
    WalletError,
    WalletInteractor,
    WalletResponse,
)
from app.infra.inmemory.user import InMemoryUserRepository
from app.infra.inmemory.wallet import InMemoryWalletRepository


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
    assert response.value.balance_satoshi == INITIAL_WALLET_VALUE_SATOSHIS
    assert response.value.balance_usd == INITIAL_WALLET_VALUE_SATOSHIS * 2


def test_create_wallet_im() -> None:
    wallet_repository = InMemoryWalletRepository()
    user_repository = InMemoryUserRepository()

    test_user_api = "Dummy Key"

    user_repository.create_user(test_user_api)

    interactor = WalletInteractor(
        wallet_repository,
        user_repository,
        FakeCurrencyConverter(),
        wallet_address_creator,
    )

    result_err_no_user = interactor.create_wallet(CreateWalletRequest(""))
    assert result_err_no_user.is_err()
    assert result_err_no_user.value == WalletError.USER_NOT_FOUND

    result_ok = interactor.create_wallet(CreateWalletRequest(test_user_api))
    assert result_ok.is_ok()
    assert result_ok.value.wallet_address == wallet_address_creator()
    assert result_ok.value.balance_satoshi == INITIAL_WALLET_VALUE_SATOSHIS
    assert result_ok.value.balance_usd == INITIAL_WALLET_VALUE_SATOSHIS * 2

    interactor.create_wallet(CreateWalletRequest(test_user_api))
    interactor.create_wallet(CreateWalletRequest(test_user_api))

    result_err_wallet_limit = interactor.create_wallet(
        CreateWalletRequest(test_user_api)
    )
    assert result_err_wallet_limit.is_err()
    assert result_err_wallet_limit.value == WalletError.WALLET_LIMIT_REACHED


def test_get_wallet_im() -> None:
    wallet_repository = InMemoryWalletRepository()
    user_repository = InMemoryUserRepository()

    test_user_api = "Dummy Key"

    user_repository.create_user(test_user_api)
    interactor = WalletInteractor(
        wallet_repository,
        user_repository,
        FakeCurrencyConverter(),
        wallet_address_creator,
    )

    new_wallet: WalletResponse = interactor.create_wallet(
        CreateWalletRequest(test_user_api)
    ).value

    result_err_no_user = interactor.get_wallet(
        GetWalletRequest("", new_wallet.wallet_address)
    )
    assert result_err_no_user.is_err()
    assert result_err_no_user.value == WalletError.USER_NOT_FOUND

    result_err_no_wallet = interactor.get_wallet(GetWalletRequest(test_user_api, ""))
    assert result_err_no_wallet.is_err()
    assert result_err_no_wallet.value == WalletError.WALLET_NOT_FOUND

    wallet = interactor.get_wallet(
        GetWalletRequest(test_user_api, new_wallet.wallet_address)
    )
    assert wallet.value.wallet_address == new_wallet.wallet_address
    assert wallet.value.balance_satoshi == new_wallet.balance_satoshi
    assert wallet.value.balance_usd == new_wallet.balance_usd
