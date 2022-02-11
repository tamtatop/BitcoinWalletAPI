from typing import Protocol

from fastapi import FastAPI

from app.core.admin.interactor import IAdminRepository
from app.core.facade import WalletService
from app.core.transaction.interactor import ITransactionRepository
from app.core.user.interactor import IUserRepository
from app.core.wallet.interactor import IWalletRepository
from app.infra.fastapi.api_main import setup_fastapi
from app.infra.sqlite.transaction import SqlTransactionRepository
from app.infra.sqlite.user import SqlUserRepository
from app.infra.sqlite.wallet import SqlWalletRepository


# helper for representing IAdminRepository + ITransactionRepository
class IAdminAndTransactionRepository(
    IAdminRepository, ITransactionRepository, Protocol
):
    pass


def setup_user_repository() -> IUserRepository:
    return SqlUserRepository("db.db")


def setup_wallet_repository() -> IWalletRepository:
    return SqlWalletRepository("db.db")


def setup_admin_and_transaction_repository(
    wallet_repository: IWalletRepository,
) -> IAdminAndTransactionRepository:
    return SqlTransactionRepository("db.db", wallet_repository)


def setup() -> FastAPI:
    user_repository = setup_user_repository()
    wallet_repository = setup_wallet_repository()
    transaction_and_admin_repository = setup_admin_and_transaction_repository(
        wallet_repository
    )
    return setup_fastapi(
        WalletService.create(
            user_repository=user_repository,
            wallet_repository=wallet_repository,
            transaction_repository=transaction_and_admin_repository,
            admin_repository=transaction_and_admin_repository,
        )
    )
