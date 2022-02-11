import copy
from dataclasses import dataclass, field
from typing import List

from app.core.transaction.entity import Transaction
from app.core.wallet.interactor import IWalletRepository


@dataclass(eq=False)
class IdTransaction:
    id: int
    transaction: Transaction

    def is_related_to_addresses(self, addresses: List[str]) -> bool:
        return (
            self.transaction.source in addresses
            or self.transaction.destination in addresses
        )

    def __eq__(self, other):
        return isinstance(other, IdTransaction) and self.id == other.id

    def __hash__(self):
        # use the hashcode of self.ssn since that is used
        # for equality checks as well
        return hash(self.id)


@dataclass
class InMemoryTransactionRepository:
    wallet_repository: IWalletRepository
    data: List[IdTransaction] = field(default_factory=list)
    id_counter = 0

    def create_transaction(self, transaction: Transaction) -> None:
        self.data.append(IdTransaction(id=self.id_counter, transaction=transaction))
        self.id_counter += 1

    def get_all_user_transactions(self, user_api_key: str) -> List[Transaction]:
        user_wallets = self.wallet_repository.get_user_wallets(user_api_key)
        user_wallet_addresses = [w.address for w in user_wallets]
        unique_transactions = set(
            t for t in self.data if t.is_related_to_addresses(user_wallet_addresses)
        )
        return [copy.copy(t.transaction) for t in unique_transactions]

    def get_all_wallet_transactions(self, wallet_address: str) -> List[Transaction]:
        return [
            copy.copy(t.transaction)
            for t in self.data
            if t.is_related_to_addresses([wallet_address])
        ]

    def get_all_transactions(self) -> List[Transaction]:
        return [copy.copy(t.transaction) for t in self.data]
