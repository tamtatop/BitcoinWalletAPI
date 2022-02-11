from unittest.mock import MagicMock

from result import Ok, Result

from app.core.btc_constants import SATOSHI_IN_BTC
from app.core.user.interactor import User, IUserRepository
from app.core.wallet.interactor import (
    INITIAL_WALLET_VALUE_SATOSHIS,
    ConversionError,
    CreateWalletRequest,
    FiatCurrency,
    GetWalletRequest,
    Wallet,
    WalletError,
    WalletInteractor,
    WalletResponse, IWalletRepository,
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
    assert response.value.balance_btc == INITIAL_WALLET_VALUE_SATOSHIS / SATOSHI_IN_BTC
    assert response.value.balance_usd == INITIAL_WALLET_VALUE_SATOSHIS * 2


def test_create_wallet_im(wallet_repository: IWalletRepository, user_repository: IUserRepository) -> None:

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
    assert isinstance(result_ok, Ok)
    assert result_ok.value.wallet_address == wallet_address_creator()
    assert result_ok.value.balance_btc == INITIAL_WALLET_VALUE_SATOSHIS / SATOSHI_IN_BTC
    assert result_ok.value.balance_usd == INITIAL_WALLET_VALUE_SATOSHIS * 2

    interactor.create_wallet(CreateWalletRequest(test_user_api))
    interactor.create_wallet(CreateWalletRequest(test_user_api))

    result_err_wallet_limit = interactor.create_wallet(
        CreateWalletRequest(test_user_api)
    )
    assert result_err_wallet_limit.is_err()
    assert result_err_wallet_limit.value == WalletError.WALLET_LIMIT_REACHED


def test_get_wallet_im(wallet_repository: IWalletRepository, user_repository: IUserRepository) -> None:
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
    assert wallet.value.balance_btc == new_wallet.balance_btc
    assert wallet.value.balance_usd == new_wallet.balance_usd


def test_update_balance_im(wallet_repository: IWalletRepository) -> None:
    test_user_api_key = "dummy key"
    test_wallet_address = "dummy address"
    test_init_balance = 1
    test_new_balance = 10000

    wallet_repository.create_wallet(
        test_user_api_key, test_wallet_address, test_init_balance
    )

    pre_check = wallet_repository.get_wallet(test_wallet_address)
    assert pre_check.balance == test_init_balance

    wallet_repository.update_balance(test_wallet_address, test_new_balance)
    new_check = wallet_repository.get_wallet(test_wallet_address)
    assert new_check.balance == test_new_balance
