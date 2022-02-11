from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Protocol

from result import Err, Ok, Result

from app.core.btc_constants import INITIAL_WALLET_VALUE_SATOSHIS, SATOSHI_IN_BTC
from app.core.currency_converter import (
    ConversionError,
    FiatCurrency,
    ICurrencyConverter,
)
from app.core.key_generator import ApiKeyGenerator
from app.core.user.interactor import IUserRepository
from app.core.wallet.entity import Wallet


class WalletError(Enum):
    USER_NOT_FOUND = 0
    WALLET_NOT_FOUND = 1
    WALLET_LIMIT_REACHED = 2
    UNSUPPORTED_CURRENCY = 3
    NOT_THIS_USERS_WALLET = 4


@dataclass
class WalletResponse:
    wallet_address: str
    balance_btc: float
    balance_usd: float


@dataclass
class CreateWalletRequest:
    user_api_key: str


@dataclass
class GetWalletRequest:
    user_api_key: str
    wallet_address: str


class IWalletRepository(Protocol):
    def create_wallet(
        self, user_api_key: str, wallet_address: str, initial_balance: int
    ) -> Wallet:
        raise NotImplementedError()

    def get_wallet(self, wallet_address: str) -> Optional[Wallet]:
        raise NotImplementedError()

    def get_user_wallets(self, user_api_key: str) -> List[Wallet]:
        raise NotImplementedError()

    def update_balance(self, wallet_address: str, balance: int) -> None:
        raise NotImplementedError()


class IWalletInteractor(Protocol):
    def create_wallet(
        self, request: CreateWalletRequest
    ) -> Result[WalletResponse, WalletError]:
        raise NotImplementedError()

    def get_wallet(
        self, request: GetWalletRequest
    ) -> Result[WalletResponse, WalletError]:
        raise NotImplementedError()


MAX_WALLETS_PER_PERSON = 3


@dataclass
class WalletInteractor:
    wallet_repository: IWalletRepository
    user_repository: IUserRepository
    currency_convertor: ICurrencyConverter
    wallet_address_creator: ApiKeyGenerator

    def create_wallet(
        self, request: CreateWalletRequest
    ) -> Result[WalletResponse, WalletError]:
        if self.user_repository.get_user(request.user_api_key) is None:
            return Err(WalletError.USER_NOT_FOUND)

        user_wallets = self.wallet_repository.get_user_wallets(request.user_api_key)

        if len(user_wallets) == MAX_WALLETS_PER_PERSON:
            return Err(WalletError.WALLET_LIMIT_REACHED)

        wallet = self.wallet_repository.create_wallet(
            request.user_api_key,
            self.wallet_address_creator(),
            INITIAL_WALLET_VALUE_SATOSHIS,
        )

        converted_to_fiat: Result[
            float, ConversionError
        ] = self.currency_convertor.convert_btc_to_fiat(
            satoshis=wallet.balance, currency=FiatCurrency.USD
        )

        if isinstance(converted_to_fiat, Err):
            return Err(WalletError.UNSUPPORTED_CURRENCY)

        return Ok(
            WalletResponse(
                wallet_address=wallet.address,
                balance_btc=wallet.balance / SATOSHI_IN_BTC,
                balance_usd=converted_to_fiat.value,
            )
        )

    def get_wallet(
        self, request: GetWalletRequest
    ) -> Result[WalletResponse, WalletError]:
        if self.user_repository.get_user(request.user_api_key) is None:
            return Err(WalletError.USER_NOT_FOUND)

        wallet = self.wallet_repository.get_wallet(request.wallet_address)
        if wallet is None:
            return Err(WalletError.WALLET_NOT_FOUND)
        if wallet.owner_key != request.user_api_key:
            return Err(WalletError.NOT_THIS_USERS_WALLET)

        converted_to_fiat: Result[
            float, ConversionError
        ] = self.currency_convertor.convert_btc_to_fiat(
            satoshis=wallet.balance, currency=FiatCurrency.USD
        )

        if isinstance(converted_to_fiat, Err):
            return Err(WalletError.UNSUPPORTED_CURRENCY)

        return Ok(
            WalletResponse(
                wallet_address=wallet.address,
                balance_btc=wallet.balance / SATOSHI_IN_BTC,
                balance_usd=converted_to_fiat.value,
            )
        )
