from dataclasses import dataclass, field
from typing import List, Optional

from app.core.wallet.interactor import Wallet


@dataclass
class InMemoryWalletRepository:
    data: List[Wallet] = field(default_factory=list)

    def create_wallet(
        self, user_api_key: str, wallet_address: str, init_balance: int
    ) -> Wallet:
        wallet = Wallet(wallet_address, user_api_key, init_balance)
        self.data.append(wallet)
        return wallet

    def get_wallet(self, wallet_address: str) -> Optional[Wallet]:
        found_wallet = [w for w in self.data if w.address == wallet_address]
        if len(found_wallet) == 0:
            return None
        return found_wallet[0]

    def get_user_wallets(self, user_api_key: str) -> List[Wallet]:
        return [w for w in self.data if w.owner_key == user_api_key]
