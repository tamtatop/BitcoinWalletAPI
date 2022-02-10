from unittest.mock import MagicMock

from result import Err, Ok, Result

from app.core.user.interactor import User
from app.core.wallet.interactor import (
    INITIAL_WALLET_VALUE_SATOSHIS,
    ConversionError,
    CreateWalletRequest,
    FiatCurrency,
    Wallet,
    WalletInteractor,
)


class FakeCurrencyConverter:
    def convert_btc_to_fiat(
        self, satoshis: int, currency: FiatCurrency
    ) -> Result[float, ConversionError]:
        return Ok(satoshis * 2)


def wallet_address_creator() -> str:
    return "wallet address"


def test_create_wallet() -> None:
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
