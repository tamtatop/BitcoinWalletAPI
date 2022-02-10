from _pytest.config.argparsing import Parser
import pytest
from result import Err

from app.core.user.interactor import IUserRepository
from app.core.wallet.interactor import IWalletRepository
from app.infra.sqlite.transaction_repository import TransactionRepository
from app.infra.sqlite.user_repository import UserRepository
from app.infra.sqlite.wallet_repository import WalletRepository


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--sql",
        action="store_true",
        default=False,
        help="Nun integration tests with in memory Sqlite3Db",
    )


@pytest.fixture(scope="function")
def db_users(request: pytest.FixtureRequest) -> IUserRepository:
    db = UserRepository(":memory:")
    return db


@pytest.fixture(scope="function")
def db_wallet(request: pytest.FixtureRequest) -> IUserRepository:
    db = WalletRepository(":memory:")
    return db


@pytest.fixture(scope="function")
def db_transaction(request: pytest.FixtureRequest) -> IUserRepository:
    db = TransactionRepository(":memory:")
    return db


def test_create_user(db_users: IUserRepository) -> None:
    db_users.create_user('abc')
    assert db_users.get_user('abc') is not None


def test_get_user(db_users: IUserRepository) -> None:
    db_users.create_user('newuser')
    assert db_users.get_user('newuser') is not None
    assert db_users.get_user('newuser').api_key == 'newuser'


def test_create_wallet(db_wallet: IWalletRepository) -> None:
    user = db_users.create_user('newuser')
    assert db_wallet.create_wallet(user.api_key, 'aaa', 50) is not None
    assert db_wallet.create_wallet(user.api_key, 'bbb', 100) is not None

    assert db_wallet.get_wallet('aaa') is not None
    assert db_wallet.get_wallet('aaa').owner_key == 'newuser'
    assert db_wallet.get_wallet('ccc') is None


def test_create_fourth_wallet(db_wallet: IWalletRepository) -> None:
    user = db_users.create_user('newuser')
    assert db_wallet.create_wallet(user.api_key, 'aaa', 50) is not None
    assert db_wallet.create_wallet(user.api_key, 'bbb', 100) is not None
    assert db_wallet.create_wallet(user.api_key, 'ccc', 100) is not None

    response = db_wallet.create_wallet(user.api_key, '123', 100)
    assert isinstance(response, Err)
    assert response.value


def test_get_user_wallets(db_users: IUserRepository, db_wallet: IWalletRepository) -> None:
    user = db_users.create_user('newuser')
    db_wallet.create_wallet(user.api_key, 'aaa', 50)
    db_wallet.create_wallet(user.api_key, 'bbb', 100)
    assert len(db_wallet.get_user_wallets(user.api_key)) is 2
    db_wallet.create_wallet(user.api_key, 'bbb', 100)
    assert len(db_wallet.get_user_wallets(user.api_key)) is 2
    db_wallet.create_wallet(user.api_key, 'ccc', 100)
    assert len(db_wallet.get_user_wallets(user.api_key)) is 3
    db_wallet.create_wallet(user.api_key, 'ddd', 100)
    assert len(db_wallet.get_user_wallets(user.api_key)) is 3


