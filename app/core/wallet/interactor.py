import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional, Protocol

from result import Err, Ok, Result

from app.core.user.interactor import IUserRepository

MAX_WALLETS_PER_PERSON = 3
INITIAL_WALLET_VALUE_SATOSHIS = 100000000


class FiatCurrency(Enum):
    GEL = 0
    USD = 1
    EUR = 2
    RUB = 3


class ConversionError(Enum):
    UNSUPPORTED_CURRENCY = 1


class ICurrencyConverter(Protocol):
    def convert_btc_to_fiat(
        self, satoshis: int, currency: FiatCurrency
    ) -> Result[float, ConversionError]:
        raise NotImplementedError()


class WalletError(Enum):
    USER_NOT_FOUND = 0
    WALLET_NOT_FOUND = 1
    WALLET_LIMIT_REACHED = 2
    UNSUPPORTED_CURRENCY = 3


@dataclass
class Wallet:
    address: str
    owner_key: str
    balance: int


@dataclass
class WalletResponse:
    wallet_address: str
    balance_satoshi: int
    balance_usd: float


@dataclass
class CreateWalletRequest:
    user_api_key: str


@dataclass
class GetWalletRequest:
    user_api_key: str
    wallet_address: str


# TODO: Update it
ApiKeyGenerator = Callable[[], str]


def generate_wallet_address() -> str:
    return uuid.uuid1().hex


class IWalletRepository(Protocol):
    def create_wallet(
        self, user_api_key: str, wallet_address: str, init_balance: int
    ) -> Wallet:
        raise NotImplementedError()

    def get_wallet(self, wallet_address: str) -> Optional[Wallet]:
        raise NotImplementedError()

    def get_user_wallets(self, user_api_key: str) -> List[Wallet]:
        raise NotImplementedError()


class IWalletInteractor:
    def create_wallet(
        self, request: CreateWalletRequest
    ) -> Result[WalletResponse, WalletError]:
        raise NotImplementedError()

    def get_wallet(
        self, request: GetWalletRequest
    ) -> Result[WalletResponse, WalletError]:
        raise NotImplementedError()


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

        if converted_to_fiat.is_err():
            return Err(WalletError.UNSUPPORTED_CURRENCY)

        return Ok(
            WalletResponse(
                wallet_address=wallet.address,
                balance_satoshi=wallet.balance,
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

        converted_to_fiat: Result[
            float, ConversionError
        ] = self.currency_convertor.convert_btc_to_fiat(
            satoshis=wallet.balance, currency=FiatCurrency.USD
        )

        if not converted_to_fiat.is_ok():
            return Err(WalletError.UNSUPPORTED_CURRENCY)

        return Ok(
            WalletResponse(
                wallet_address=wallet.address,
                balance_satoshi=wallet.balance,
                balance_usd=converted_to_fiat.value,
            )
        )
