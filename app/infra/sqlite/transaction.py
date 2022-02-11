import sqlite3
from dataclasses import dataclass
from typing import List, Set

from app.core.transaction.entity import Transaction
from app.core.wallet.interactor import IWalletRepository
from app.infra.repository.id_transaction import IdTransaction


@dataclass(init=False)
class TransactionRepository:
    def __init__(self, filename: str, wallet_repository: IWalletRepository) -> None:
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.wallet_repository = wallet_repository
        self.conn.executescript(
            """
            create table if not exists Transaction_tbl (
                transaction_id integer PRIMARY KEY AUTOINCREMENT,
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
            " INSERT INTO Transaction_tbl VALUES (?, ?, ?, ?, ?)",
            (
                None,
                transaction.source,
                transaction.destination,
                transaction.amount,
                transaction.fee,
            ),
        )
        self.conn.commit()

    def get_all_user_transactions(self, user_api_key: str) -> List[Transaction]:
        user_wallets = self.wallet_repository.get_user_wallets(user_api_key)
        user_wallet_addresses = list(w.address for w in user_wallets)

        idtransactions: Set[IdTransaction] = set()

        for a in user_wallet_addresses:
            idtransactions.update(self._get_all_wallet_idtransactions(a))

        return [t.transaction for t in idtransactions]

    def _get_all_wallet_idtransactions(
        self, wallet_address: str
    ) -> List[IdTransaction]:
        idtransactions: List[IdTransaction] = list()
        for row in self.conn.execute(
            " SELECT * FROM Transaction_tbl WHERE source_wallet = ? or destination_wallet = ?",
            (
                wallet_address,
                wallet_address,
            ),
        ):
            idtransactions.append(IdTransaction.from_row(row))
        return idtransactions

    def get_all_wallet_transactions(self, wallet_address: str) -> List[Transaction]:
        return [
            t.transaction for t in self._get_all_wallet_idtransactions(wallet_address)
        ]

    def get_all_transactions(self) -> List[Transaction]:
        idtransactions: List[Transaction] = list()
        for row in self.conn.execute(
            " SELECT * FROM Transaction_tbl",
        ):
            idtransactions.append(IdTransaction.from_row(row).transaction)

        return idtransactions
