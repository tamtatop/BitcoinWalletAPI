from typing import Protocol

import pytest
from _pytest.config.argparsing import Parser

from app.core.admin.interactor import (
    IAdminRepository,
    IAdminInteractor,
    AdminInteractor,
)
from app.core.currency_converter import ICurrencyConverter, RandomCurrencyConverter
from app.core.key_generator import (
    ApiKeyGenerator,
    generate_wallet_address,
    generate_new_user_key,
)
from app.core.transaction.fee_calculator import IFeeCalculator, FeeCalculator
from app.core.transaction.interactor import (
    ITransactionRepository,
    ITransactionInteractor,
    TransactionInteractor,
)
from app.core.user.interactor import (
    IUserRepository,
    UserInteractor,
    IUserInteractor,
)
from app.core.wallet.interactor import (
    IWalletRepository,
    IWalletInteractor,
    WalletInteractor,
)
from app.infra.inmemory.transaction import InMemoryTransactionRepository
from app.infra.inmemory.user import InMemoryUserRepository
from app.infra.inmemory.wallet import InMemoryWalletRepository
from app.infra.sqlite.transaction import SqlTransactionRepository
from app.infra.sqlite.user import SqlUserRepository
from app.infra.sqlite.wallet import SqlWalletRepository
from tests.test_wallet_interactor import FakeCurrencyConverter, wallet_address_creator


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
        return SqlUserRepository(":memory:")
    else:
        return InMemoryUserRepository()


@pytest.fixture(scope="function")
def wallet_repository(request: pytest.FixtureRequest) -> IWalletRepository:
    if use_sql_implementation(request):
        return SqlWalletRepository(":memory:")
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
        return SqlTransactionRepository(":memory:", wallet_repository)
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


@pytest.fixture(scope="function")
def currency_convertor(request: pytest.FixtureRequest) -> ICurrencyConverter:
    return FakeCurrencyConverter()


@pytest.fixture(scope="function")
def wallet_address_creator_fun(request: pytest.FixtureRequest) -> ApiKeyGenerator:
    return wallet_address_creator


@pytest.fixture(scope="function")
def wallet_address_creator_real_fun(request: pytest.FixtureRequest) -> ApiKeyGenerator:
    return generate_wallet_address


@pytest.fixture(scope="function")
def wallet_interactor(
    wallet_repository: IWalletRepository,
    user_repository: IUserRepository,
    currency_convertor: ICurrencyConverter,
    wallet_address_creator_fun: ApiKeyGenerator,
) -> IWalletInteractor:
    return WalletInteractor(
        wallet_repository,
        user_repository,
        currency_convertor,
        wallet_address_creator_fun,
    )


@pytest.fixture(scope="function")
def wallet_interactor_real_generator(
    wallet_repository: IWalletRepository,
    user_repository: IUserRepository,
    currency_convertor: ICurrencyConverter,
    wallet_address_creator_real_fun: ApiKeyGenerator,
) -> IWalletInteractor:
    return WalletInteractor(
        wallet_repository,
        user_repository,
        currency_convertor,
        wallet_address_creator_real_fun,
    )


@pytest.fixture(scope="function")
def api_key_creator(request: pytest.FixtureRequest) -> ApiKeyGenerator:
    return generate_new_user_key


@pytest.fixture(scope="function")
def user_interactor(
    user_repository: IUserRepository,
    api_key_creator: ApiKeyGenerator,
) -> IUserInteractor:
    return UserInteractor(user_repository, api_key_creator)


@pytest.fixture(scope="function")
def admin_interactor(admin_repository: IAdminRepository) -> IAdminInteractor:
    return AdminInteractor(admin_repository)


@pytest.fixture(scope="function")
def fee_calculator(request: pytest.FixtureRequest) -> ApiKeyGenerator:
    return FeeCalculator()


@pytest.fixture(scope="function")
def transaction_interactor(
    transaction_repository: ITransactionRepository,
    user_repository: IUserRepository,
    wallet_repository: IWalletRepository,
    fee_calculator: IFeeCalculator,
) -> ITransactionInteractor:
    return TransactionInteractor(
        transaction_repository, user_repository, wallet_repository, fee_calculator
    )
