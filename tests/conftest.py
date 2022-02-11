from typing import Protocol

import pytest
from _pytest.config.argparsing import Parser

from app.core.admin.interactor import IAdminRepository
from app.core.transaction.interactor import ITransactionRepository
from app.core.user.interactor import IUserRepository
from app.core.wallet.interactor import IWalletRepository
from app.infra.inmemory.transaction import InMemoryTransactionRepository
from app.infra.inmemory.user import InMemoryUserRepository
from app.infra.inmemory.wallet import InMemoryWalletRepository
from app.infra.sqlite.transaction import TransactionRepository
from app.infra.sqlite.user import UserRepository
from app.infra.sqlite.wallet import WalletRepository


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--sql",
        action="store_true",
        default=False,
        help="Nun integration tests with in memory Sqlite3Db",
    )


def use_sql_implementation(request: pytest.FixtureRequest) -> bool:
    return request.config.getoption("--sql")  # type: ignore


@pytest.fixture(scope="function")
def user_repository(request: pytest.FixtureRequest) -> IUserRepository:
    if use_sql_implementation(request):
        return UserRepository(":memory:")
    else:
        return InMemoryUserRepository()


@pytest.fixture(scope="function")
def wallet_repository(request: pytest.FixtureRequest) -> IWalletRepository:
    if use_sql_implementation(request):
        return WalletRepository(":memory:")
    else:
        return InMemoryWalletRepository()


class IAdminAndTransactionRepository(
    IAdminRepository, ITransactionRepository, Protocol
):
    pass


@pytest.fixture(scope="function")
def transaction_and_admin_repository(
    wallet_repository: IWalletRepository, request: pytest.FixtureRequest
) -> IAdminAndTransactionRepository:
    if use_sql_implementation(request):
        return TransactionRepository(":memory:", wallet_repository)
    else:
        return InMemoryTransactionRepository(wallet_repository)


@pytest.fixture(scope="function")
def transaction_repository(
    transaction_and_admin_repository: IAdminAndTransactionRepository,
) -> ITransactionRepository:
    return transaction_and_admin_repository


@pytest.fixture(scope="function")
def admin_repository(
    transaction_and_admin_repository: IAdminAndTransactionRepository,
) -> IAdminRepository:
    return transaction_and_admin_repository
