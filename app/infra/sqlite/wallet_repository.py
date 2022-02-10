import sqlite3
from dataclasses import dataclass
from typing import Optional

from result import Result

from app.core.wallet.interactor import IWalletRepository, Wallet, WalletError
INITIAL_BALANCE = 1


@dataclass
class WalletRepository:
    def __init__(self) -> None:
        self.conn = sqlite3.connect("db.db", check_same_thread=False)
        self.conn.executescript(
            """
            create table if not exists Wallet (
                address text primary key,
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

    def make_deposit(self, wallet_address: str, deposit: int) -> Optional[Wallet]:
        self.conn.execute(
            "UPDATE Wallet SET balance = balance + ? WHERE address = ?",
            (
                deposit,
                wallet_address,
            ),
        )
        self.conn.commit()
        return self.get_wallet(wallet_address)

    def charge(self, wallet_address: str, amount: int) -> Optional[Wallet]:
        wallet = self.get_wallet(wallet_address)
        if wallet.balance - amount < 0:
            return None

        self.conn.execute(
            "UPDATE Wallet SET balance = balance - ? WHERE address = ?",
            (
                amount,
                wallet_address,
            ),
        )
        self.conn.commit()
        return self.get_wallet(wallet_address)

