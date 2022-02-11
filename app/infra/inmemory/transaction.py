from dataclasses import dataclass, field
from typing import List

from app.core.transaction.entity import Transaction
from app.core.wallet.interactor import IWalletRepository


@dataclass
class InMemoryTransactionRepository:
    wallet_repository: IWalletRepository
    data: List[Transaction] = field(default_factory=list)

    def create_transaction(self, transaction: Transaction) -> None:
        self.data.append(transaction)

    # FIXME: two same transactions
    def get_all_user_transactions(self, user_api_key: str) -> List[Transaction]:
        user_wallets = self.wallet_repository.get_user_wallets(user_api_key)
        user_wallet_addresses = set(w.address for w in user_wallets)
        return [
            t
            for t in self.data
            if t.source in user_wallet_addresses
            or t.destination in user_wallet_addresses
        ]

    def get_all_wallet_transactions(self, wallet_address: str) -> List[Transaction]:
        return [
            t
            for t in self.data
            if t.source == wallet_address or t.destination == wallet_address
        ]

    def get_all_transactions(self) -> List[Transaction]:
        return list(self.data)
