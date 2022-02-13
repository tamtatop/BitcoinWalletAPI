from typing import Callable, Dict, Protocol

import pytest
from _pytest.config.argparsing import Parser
from fastapi.testclient import TestClient
from result import Ok, Result

from app.core.admin.interactor import (
    AdminInteractor,
    IAdminInteractor,
    IAdminRepository,
)
from app.core.currency_converter import (
    ConversionError,
    FiatCurrency,
    ICurrencyConverter,
)
from app.core.facade import WalletService
from app.core.key_generator import (
    ApiKeyGenerator,
    generate_new_user_key,
    generate_wallet_address,
)
from app.core.transaction.fee_calculator import FeeCalculator, IFeeCalculator
from app.core.transaction.interactor import (
    ITransactionInteractor,
    ITransactionRepository,
    TransactionInteractor,
)
from app.core.user.interactor import IUserInteractor, IUserRepository, UserInteractor
from app.core.wallet.interactor import (
    IWalletInteractor,
    IWalletRepository,
    WalletInteractor,
)
from app.infra.fastapi.api_main import setup_fastapi
from app.infra.inmemory.transaction import InMemoryTransactionRepository
from app.infra.inmemory.user import InMemoryUserRepository
from app.infra.inmemory.wallet import InMemoryWalletRepository
from app.infra.sqlite.transaction import SqlTransactionRepository
from app.infra.sqlite.user import SqlUserRepository
from app.infra.sqlite.wallet import SqlWalletRepository


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


class FakeCurrencyConverter:
    scale = 2

    def convert_btc_to_fiat(
        self, satoshis: int, currency: FiatCurrency
    ) -> Result[float, ConversionError]:
        return Ok(satoshis * self.scale)


@pytest.fixture(scope="function")
def currency_convertor() -> ICurrencyConverter:
    return FakeCurrencyConverter()


@pytest.fixture(scope="function")
def wallet_address_creator_fun() -> ApiKeyGenerator:
    def f() -> str:
        return "wallet address"

    return f


@pytest.fixture(scope="function")
def wallet_address_creator_real_fun() -> ApiKeyGenerator:
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
def api_key_creator() -> ApiKeyGenerator:
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
def fee_calculator() -> IFeeCalculator:
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


@pytest.fixture(scope="function")
def api_client() -> TestClient:
    user_repository = InMemoryUserRepository()
    wallet_repository = InMemoryWalletRepository()
    transaction_and_admin_repository = InMemoryTransactionRepository(wallet_repository)
    wallet_service = WalletService.create(
        user_repository=user_repository,
        wallet_repository=wallet_repository,
        transaction_repository=transaction_and_admin_repository,
        admin_repository=transaction_and_admin_repository,
    )
    return TestClient(setup_fastapi(wallet_service))


@pytest.fixture(scope="module")
def from_msg() -> Callable[[str], Dict[str, str]]:
    def f(_msg: str) -> Dict[str, str]:
        return {"detail": _msg}

    return f
