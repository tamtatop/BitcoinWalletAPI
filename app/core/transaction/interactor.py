from dataclasses import dataclass
from enum import Enum
from typing import List, Protocol

from result import Err, Ok, Result

from app.core.facade import MakeTransactionRequest
from app.core.transaction.entity import Transaction
from app.core.user.interactor import IUserRepository
from app.core.wallet.interactor import IWalletRepository

INNER_API_TRANSACTION_RATE = 0
OUTER_API_TRANSACTION_RATE = 1.5


class TransactionError(Enum):
    pass


@dataclass
class MakeTransactionResponse:
    pass


@dataclass
class GetTransactionsResponse:
    pass


@dataclass
class GetStatisticsResponse:
    pass


#
# `POST /transactions`
#   - Requires API key
#   - Makes a transaction from one wallet to another
#   - Transaction is free if the same user is the owner of both wallets
#   - System takes a 1.5% (of the transferred amount) fee for transfers to the foreign wallets
#
# `GET /transactions`
#   - Requires API key
#   - Returns list of transactions
# `GET /wallets/{address}/transactions`
#   - Requires API key
#   - returns transactions related to the wallet


class ITransactionRepository(Protocol):
    def create_transaction(self, transaction: Transaction) -> None:
        raise NotImplementedError()

    def get_all_user_transactions(self, user_api_key: str) -> List[Transaction]:
        raise NotImplementedError()

    def get_all_wallet_transactions(self, wallet_address: str) -> List[Transaction]:
        raise NotImplementedError()


class TransactionError:
    pass


@dataclass
class TransactionInteractor:
    transaction_repository: ITransactionRepository
    user_repository: IUserRepository
    wallet_repository: IWalletRepository

    def make_transaction(self, request: MakeTransactionRequest) -> Result[MakeTransactionResponse, TransactionError]:
        if self.user_repository.get_user(request.user_api_key) is not None:
            return Err(TransactionError.USER_NOT_FOUND)
        source = self.wallet_repository.get_wallet(request.source)
        destination = self.wallet_repository.get_wallet(request.destination)

        if source is None:
            return Err(TransactionError.SOURCE_WALLET_NOT_FOUND)
        if destination is None:
            return Err(TransactionError.DESTINATION_WALLET_NOT_FOUND)

        if source.owner_key != request.user_api_key:
            return Err(TransactionError.INCORRECT_API_KEY)

        rate: float
        if source.owner_key == destination.owner_key:
            rate = INNER_API_TRANSACTION_RATE / 100
        else:
            rate = OUTER_API_TRANSACTION_RATE / 100

        amount_including_fee = request.amount * rate
        if self.wallet_repository.charge(request.source, amount_including_fee) is None:
            return Err(TransactionError.NOT_ENOUGH_AMOUNT_ON_SOURCE_ACCOUNT)
        self.wallet_repository.make_deposit(request.destination, request.amount)
        res = self.transaction_repository.create_transaction()
        return Ok(MakeTransactionResponse())

