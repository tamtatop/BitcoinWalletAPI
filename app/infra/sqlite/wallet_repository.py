import sqlite3
from dataclasses import dataclass
from typing import Optional, List

from result import Result

from app.core.wallet.interactor import IWalletRepository, Wallet, WalletError
INITIAL_BALANCE = 1


@dataclass
class WalletRepository:
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

    def create_wallet(self, address: str, user_api_key: str, initial_balance: int) -> Wallet:
        self.conn.execute(
            " INSERT INTO Wallet VALUES (?, ?, ?)", (address, user_api_key, initial_balance)
        )
        self.conn.commit()
        return Wallet(address, user_api_key, initial_balance)

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

    def update_balance(self, wallet_address: str, amount: int) -> Optional[Wallet]:
        self.conn.execute(
            "UPDATE Wallet SET balance = ? WHERE address = ?",
            (
                amount,
                wallet_address,
            ),
        )
        self.conn.commit()
        return self.get_wallet(wallet_address)

