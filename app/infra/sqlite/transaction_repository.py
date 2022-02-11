import sqlite3
from dataclasses import dataclass
from typing import List

from app.core.transaction.interactor import Transaction
from app.core.wallet.interactor import IWalletRepository


@dataclass(init=False)
class TransactionRepository:
    def __init__(self, filename: str, wallet_repository: IWalletRepository) -> None:
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.wallet_repository = wallet_repository
        self.conn.executescript(
            """
            create table if not exists Transaction_tbl (
                source_wallet text,
                destination_wallet text,
                amount integer not null,
                fee integer not null
            );
            """
        )
        self.conn.commit()

    def create_transaction(self, transaction: Transaction) -> None:
        self.conn.execute(
            " INSERT INTO Transaction_tbl VALUES (?, ?, ?, ?)",
            (
                transaction.source,
                transaction.destination,
                transaction.amount,
                transaction.fee,
            ),
        )
        self.conn.commit()

    # FIXME: two same transactions
    def get_all_user_transactions(self, user_api_key: str) -> List[Transaction]:
        user_wallets = self.wallet_repository.get_user_wallets(user_api_key)
        user_wallet_addresses = set(w.address for w in user_wallets)

        transactions: List[Transaction] = list()
        for a in user_wallet_addresses:
            transactions.extend(self.get_all_wallet_transactions(a))

        return transactions

    def get_all_wallet_transactions(self, wallet_address: str) -> List[Transaction]:
        transactions: List[Transaction] = list()
        for row in self.conn.execute(
            " SELECT * FROM Transaction_tbl WHERE source_wallet = ? or destination_wallet = ?",
            (
                wallet_address,
                wallet_address,
            ),
        ):
            transactions.append(Transaction(*row))

        return transactions

    def get_all_transactions(self) -> List[Transaction]:
        transactions: List[Transaction] = list()
        for row in self.conn.execute(
            " SELECT * FROM Transaction_tbl",
        ):
            transactions.append(Transaction(*row))

        return transactions
