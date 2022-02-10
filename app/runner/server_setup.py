import os
from typing import Protocol

from fastapi import FastAPI
from app.core.admin.interactor import IAdminRepository

from app.core.facade import WalletService
from app.core.transaction.interactor import ITransactionRepository
from app.core.user.interactor import IUserRepository
from app.core.wallet.interactor import IWalletRepository
from app.infra.fastapi.api_main import setup_fastapi


# helper for representing IAdminRepository + ITransactionRepository
class IAdminAndTransactionRepository(IAdminRepository, ITransactionRepository, Protocol):
    pass

def setup_user_repository() -> IUserRepository:
    raise NotImplementedError()

def setup_wallet_repository() -> IWalletRepository:
    raise NotImplementedError()

def setup_admin_and_transaction_repository() -> IAdminAndTransactionRepository:
    raise NotImplementedError()

def setup() -> FastAPI:
    transaction_repository = setup_admin_and_transaction_repository()
    return setup_fastapi(WalletService.create(
            user_repository=setup_user_repository(),
            wallet_repository=setup_wallet_repository(),
            transaction_repository=transaction_repository,
            admin_repository=transaction_repository,
            ))


