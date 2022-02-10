from dataclasses import dataclass
from enum import Enum
from typing import List, Protocol

from result import Err, Ok, Result

from app.core.transaction.entity import Transaction
from app.core.user.interactor import IUserRepository
from app.core.wallet.interactor import IWalletRepository


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


@dataclass
class TransactionInteractor:
    transaction_repository: ITransactionRepository
    user_repository: IUserRepository
    wallet_repository: IWalletRepository
