import sqlite3
from dataclasses import dataclass
from typing import List, Optional

from app.core.wallet.entity import Wallet

INITIAL_BALANCE = 1


@dataclass
class SqlWalletRepository:
    def __init__(self, filename: str) -> None:
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.conn.executescript(
            """
            create table if not exists Wallet (
                address text,
                owner_key text,
                balance integer not null
            );
            """
        )
        self.conn.commit()

    def create_wallet(
        self, user_api_key: str, wallet_address: str, initial_balance: int
    ) -> Wallet:
        self.conn.execute(
            " INSERT INTO Wallet VALUES (?, ?, ?)",
            (wallet_address, user_api_key, initial_balance),
        )
        self.conn.commit()
        return Wallet(wallet_address, user_api_key, initial_balance)

    def get_wallet(self, wallet_address: str) -> Optional[Wallet]:
        for row in self.conn.execute(
            " SELECT * FROM Wallet WHERE address = ?", (wallet_address,)
        ):
            return Wallet(*row)
        return None

    def get_user_wallets(self, user_api_key: str) -> List[Wallet]:
        wallets: List[Wallet] = list()
        for row in self.conn.execute(
            " SELECT * FROM Wallet WHERE owner_key = ?", (user_api_key,)
        ):
            wallets.append(Wallet(*row))

        return wallets

    def update_balance(self, wallet_address: str, balance: int) -> None:
        self.conn.execute(
            "UPDATE Wallet SET balance = ? WHERE address = ?",
            (
                balance,
                wallet_address,
            ),
        )
        self.conn.commit()
