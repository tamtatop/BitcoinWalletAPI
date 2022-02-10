import sqlite3
from dataclasses import dataclass
from typing import Optional, List

from app.core.transaction.interactor import ITransactionRepository, Transaction
from app.core.wallet.interactor import Wallet

INITIAL_BALANCE = 1


@dataclass
class TransactionRepository:
    def __init__(self, filename: str) -> None:
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.conn.executescript(
            """
            create table if not exists Transaction (
                source text,
                destination text,
                amount integer not null,
                fee integer not null
            );
            """
        )
        self.conn.commit()

    def create_transaction(self, transaction: Transaction) -> None:
        self.conn.execute(
            " INSERT INTO Transaction VALUES (?, ?, ?, ?)", (transaction.source, transaction.destination, transaction.amount, transaction.fee)
        )
        self.conn.commit()

    def get_all_user_transactions(self, user_api_key: str) -> List[Transaction]:
        transactions: List[Transaction] = list()
        for row in self.conn.execute(
                " SELECT * FROM Wallet WHERE owner_key = ?", (user_api_key,)
        ):
            for transaction in self.get_all_wallet_transactions(Wallet(*row).address):
                transactions.append(transaction)

        return transactions

    def get_all_wallet_transactions(self, wallet_address: str) -> List[Transaction]:
        transactions: List[Transaction] = list()
        for row in self.conn.execute(
            " SELECT * FROM Transaction WHERE source = ? or destination = ?", (wallet_address, wallet_address,)
        ):
            transactions.append(Transaction(*row))

        return transactions

    def get_all_transactions(self) -> List[Transaction]:
        transactions: List[Transaction] = list()
        for row in self.conn.execute(
                " SELECT * FROM Transaction",
        ):
            transactions.append(Transaction(*row))

        return transactions
