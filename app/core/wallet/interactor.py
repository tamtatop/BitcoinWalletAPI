from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol

from result import Err, Ok, Result

from app.core.user.interactor import IUserRepository, User

MAX_WALLETS_PER_PERSON = 3

class FiatCurrency(Enum):
    GEL = 0
    USD = 1
    EUR = 2
    RUB = 3


# TODO: should we handle network errors?
class ConversionError(Enum):
    UNKNOWN_ERROR = 0
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


@dataclass
class Wallet:
    address: str
    owner_key: str
    balance: int


# @dataclass
# class WalletCreatedResponse:
#     wallet_address: str
#     balance_satoshi: int
#     balance_usd: float

# - Returns wallet address and balance in BTC and USD
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


class IWalletRepository(Protocol):
    def create_wallet(
        self, user_api_key: str
    ) -> Wallet:  # TODO: should we consider database fails
        raise NotImplementedError()

    def get_wallet(self, wallet_address: str) -> Optional[Wallet]:
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

    def create_wallet(
        self, request: CreateWalletRequest
    ) -> Result[WalletResponse, WalletError]:
        if self.user_repository.get_user(request.user_api_key) is not None:
            return Err(WalletError.USER_NOT_FOUND)
        return Ok(
            WalletResponse(
                wallet=self.wallet_repository.create_wallet(request.user_api_key)
            )
        )

    def get_wallet(
        self, request: GetWalletRequest
    ) -> Result[WalletResponse, WalletError]:
        if self.user_repository.get_user(request.user_api_key) is not None:
            return Err(WalletError.USER_NOT_FOUND)
        res = self.wallet_repository.get_wallet(request.wallet_address)
        if res is not None:
            return Ok(GetWalletResponse())
        else:
            return Err(WalletError.WALLET_NOT_FOUND)
