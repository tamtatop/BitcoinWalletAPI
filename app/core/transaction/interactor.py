from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Protocol

from result import Err, Ok, Result

from app.core.btc_constants import SATOSHI_IN_BTC
from app.core.transaction.entity import Transaction
from app.core.transaction.fee_calculator import IFeeCalculator
from app.core.user.interactor import IUserRepository
from app.core.wallet.interactor import IWalletRepository


class TransactionError(Enum):
    USER_NOT_FOUND = 0
    WALLET_NOT_FOUND = 1
    SOURCE_WALLET_NOT_FOUND = 2
    DESTINATION_WALLET_NOT_FOUND = 3
    INCORRECT_API_KEY = 4
    NOT_ENOUGH_AMOUNT_ON_SOURCE_ACCOUNT = 5


@dataclass
class MakeTransactionRequest:
    user_api_key: str
    source_address: str
    destination_address: str
    amount: int


@dataclass
class MakeTransactionResponse:
    amount_left_btc: float


@dataclass
class GetTransactionsRequest:
    user_api_key: str
    wallet_address: Optional[str] = None


@dataclass
class GetTransactionsResponse:
    transactions: List[Transaction]


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


class ITransactionInteractor(Protocol):
    def make_transaction(
        self, request: MakeTransactionRequest
    ) -> Result[MakeTransactionResponse, TransactionError]:
        raise NotImplementedError()

    def get_transactions(
        self, request: GetTransactionsRequest
    ) -> Result[GetTransactionsResponse, TransactionError]:
        raise NotImplementedError()


@dataclass
class TransactionInteractor:
    transaction_repository: ITransactionRepository
    user_repository: IUserRepository
    wallet_repository: IWalletRepository
    fee_calculator: IFeeCalculator

    # `POST /transactions`
    #   - Requires API key
    #   - Makes a transaction from one wallet to another
    #   - Transaction is free if the same user is the owner of both wallets
    #   - System takes a 1.5% (of the transferred amount) fee for transfers to the foreign wallets
    def make_transaction(
        self, request: MakeTransactionRequest
    ) -> Result[MakeTransactionResponse, TransactionError]:
        if self.user_repository.get_user(request.user_api_key) is None:
            return Err(TransactionError.USER_NOT_FOUND)

        source = self.wallet_repository.get_wallet(request.source_address)
        destination = self.wallet_repository.get_wallet(request.destination_address)

        if source is None:
            return Err(TransactionError.SOURCE_WALLET_NOT_FOUND)
        if destination is None:
            return Err(TransactionError.DESTINATION_WALLET_NOT_FOUND)

        if source.owner_key != request.user_api_key:
            return Err(TransactionError.INCORRECT_API_KEY)

        fee_amount = self.fee_calculator(source, destination, request.amount)

        if source.balance < request.amount:
            return Err(TransactionError.NOT_ENOUGH_AMOUNT_ON_SOURCE_ACCOUNT)

        source.balance -= request.amount
        destination.balance += request.amount - fee_amount

        self.wallet_repository.update_balance(source.address, source.balance)
        self.wallet_repository.update_balance(destination.address, destination.balance)

        self.transaction_repository.create_transaction(
            Transaction(
                source=source.address,
                destination=destination.address,
                amount=request.amount,
                fee=fee_amount,
            )
        )

        return Ok(
            MakeTransactionResponse(amount_left_btc=source.balance / SATOSHI_IN_BTC)
        )

    def get_transactions(
        self, request: GetTransactionsRequest
    ) -> Result[GetTransactionsResponse, TransactionError]:
        if self.user_repository.get_user(request.user_api_key) is None:
            return Err(TransactionError.USER_NOT_FOUND)

        if request.wallet_address is None:
            return Ok(
                GetTransactionsResponse(
                    self.transaction_repository.get_all_user_transactions(
                        request.user_api_key
                    )
                )
            )

        wallet = self.wallet_repository.get_wallet(request.wallet_address)
        if wallet is None:
            return Err(TransactionError.WALLET_NOT_FOUND)

        return Ok(
            GetTransactionsResponse(
                self.transaction_repository.get_all_wallet_transactions(
                    request.wallet_address
                )
            )
        )
