
from result import Err

from app.core.admin.interactor import IAdminRepository
from app.core.transaction.entity import Transaction
from app.core.transaction.interactor import ITransactionRepository
from app.core.user.interactor import IUserRepository
from app.core.wallet.interactor import IWalletRepository


def test_create_user(user_repository: IUserRepository) -> None:
    user_repository.create_user('abc')
    assert user_repository.get_user('abc') is not None

    user_repository.create_user('newuser')
    assert user_repository.get_user('newuser') is not None


def test_get_user(user_repository: IUserRepository) -> None:
    user_repository.create_user('newuser')
    assert user_repository.get_user('newuser') is not None
    assert user_repository.get_user('newuser').api_key == 'newuser'

    assert user_repository.get_user('aaa') is None
    assert user_repository.get_user('abc') is None


def test_create_and_get_wallet(user_repository: IUserRepository, wallet_repository: IWalletRepository) -> None:
    user = user_repository.create_user('newuser')
    assert wallet_repository.create_wallet(user.api_key, 'aaa', 50) is not None
    assert wallet_repository.create_wallet(user.api_key, 'bbb', 100) is not None

    assert wallet_repository.get_wallet('aaa') is not None
    assert wallet_repository.get_wallet('bbb').owner_key == user.api_key
    assert wallet_repository.get_wallet('aaa').balance == 50
    assert wallet_repository.get_wallet('bbb').balance == 100

    assert wallet_repository.get_wallet('ccc') is None


def test_get_user_wallets(user_repository: IUserRepository, wallet_repository: IWalletRepository) -> None:
    user = user_repository.create_user('newuser')
    assert wallet_repository.create_wallet(user.api_key, 'aaa', 50) is not None
    assert wallet_repository.create_wallet(user.api_key, 'bbb', 100) is not None

    wallets = wallet_repository.get_user_wallets(user.api_key)
    for wallet in wallets:
        assert wallet.owner_key == 'newuser'
        assert wallet.owner_key == user.api_key
        assert wallet.balance != 0

    assert wallets[0].address == 'aaa'
    assert wallets[1].address == 'bbb'


def test_get_user_wallets_amount(user_repository: IUserRepository, wallet_repository: IWalletRepository) -> None:
    assert len(wallet_repository.get_user_wallets('nosuchuser')) is 0

    user = user_repository.create_user('newuser')
    assert len(wallet_repository.get_user_wallets(user.api_key)) is 0
    wallet_repository.create_wallet(user.api_key, 'aaa', 50)
    assert len(wallet_repository.get_user_wallets(user.api_key)) is 1
    wallet_repository.create_wallet(user.api_key, 'bbb', 100)
    assert len(wallet_repository.get_user_wallets(user.api_key)) is 2
    wallet_repository.create_wallet(user.api_key, 'ccc', 100)
    assert len(wallet_repository.get_user_wallets(user.api_key)) is 3


def test_update_balance(user_repository: IUserRepository, wallet_repository: IWalletRepository) -> None:
    user = user_repository.create_user('newuser')
    wallet_repository.create_wallet(user.api_key, 'aaa', 50)
    wallet_repository.create_wallet(user.api_key, 'bbb', 100)

    wallet_repository.update_balance('aaa', 0)
    wallet_repository.update_balance('bbb', 150)

    assert wallet_repository.get_wallet('aaa').balance == 0
    assert wallet_repository.get_wallet('bbb').balance == 150

    wallet_repository.update_balance('aaa', 1000)
    assert wallet_repository.get_wallet('aaa').balance == 1000
    wallet_repository.update_balance('bbb', 1)
    assert wallet_repository.get_wallet('bbb').balance == 1


def test_create_transaction(user_repository: IUserRepository, wallet_repository: IWalletRepository, transaction_repository: ITransactionRepository) -> None:
    first_user = user_repository.create_user('newuser')
    wallet_repository.create_wallet(first_user.api_key, 'aaa', 50)
    wallet_repository.create_wallet(first_user.api_key, 'bbb', 100)

    second_user = user_repository.create_user('otheruser')
    wallet_repository.create_wallet(second_user.api_key, 'ccc', 100)

    transaction_repository.create_transaction(Transaction('aaa', 'bbb', 20, 0))
    first_address_transactions = transaction_repository.get_all_wallet_transactions('aaa')
    second_address_transactions = transaction_repository.get_all_wallet_transactions('bbb')

    assert len(first_address_transactions) == len(second_address_transactions)
    assert len(first_address_transactions) == 1

    assert first_address_transactions[0].source == 'aaa'
    assert first_address_transactions[0].destination == 'bbb'
    assert first_address_transactions[0].amount == 20
    assert first_address_transactions[0].fee == 0

    transaction_repository.create_transaction(Transaction('bbb', 'ccc', 50, 10))
    third_address_transactions = transaction_repository.get_all_wallet_transactions('ccc')
    second_address_transactions = transaction_repository.get_all_wallet_transactions('bbb')

    assert len(first_address_transactions) != len(second_address_transactions)
    assert len(third_address_transactions) == 1
    assert len(second_address_transactions) == 2

    assert third_address_transactions[0].source == 'bbb'
    assert third_address_transactions[0].destination == 'ccc'
    assert third_address_transactions[0].amount == 50
    assert third_address_transactions[0].fee == 10


def test_get_all_user_transactions(user_repository: IUserRepository, wallet_repository: IWalletRepository, transaction_repository: ITransactionRepository) -> None:
    first_user = user_repository.create_user('newuser')
    wallet_repository.create_wallet(first_user.api_key, 'aaa', 50)
    wallet_repository.create_wallet(first_user.api_key, 'bbb', 100)

    second_user = user_repository.create_user('otheruser')
    wallet_repository.create_wallet(second_user.api_key, 'ccc', 100)

    transaction_repository.create_transaction(Transaction('aaa', 'bbb', 20, 0))
    first_user_transactions = transaction_repository.get_all_user_transactions(first_user.api_key)

    assert len(first_user_transactions) == 1

    transaction_repository.create_transaction(Transaction('bbb', 'ccc', 50, 10))
    first_user_transactions = transaction_repository.get_all_user_transactions('newuser')
    second_user_transactions = transaction_repository.get_all_user_transactions('otheruser')

    assert len(first_user_transactions) != len(second_user_transactions)
    assert len(first_user_transactions) == 2
    assert len(second_user_transactions) == 1


def test_get_all_wallet_transactions(user_repository: IUserRepository, wallet_repository: IWalletRepository, transaction_repository: ITransactionRepository) -> None:
    first_user = user_repository.create_user('newuser')
    wallet_repository.create_wallet(first_user.api_key, 'aaa', 50)
    wallet_repository.create_wallet(first_user.api_key, 'bbb', 100)

    second_user = user_repository.create_user('otheruser')
    wallet_repository.create_wallet(second_user.api_key, 'ccc', 100)

    transaction_repository.create_transaction(Transaction('aaa', 'bbb', 20, 0))
    first_user_first_address_transactions = transaction_repository.get_all_wallet_transactions('aaa')
    first_user_second_address_transactions = transaction_repository.get_all_wallet_transactions('bbb')

    assert len(first_user_second_address_transactions) == len(first_user_first_address_transactions)
    assert len(first_user_first_address_transactions) == 1
    assert first_user_first_address_transactions[0] == first_user_second_address_transactions[0]

    transaction_repository.create_transaction(Transaction('bbb', 'ccc', 50, 10))
    first_user_second_address_transactions = transaction_repository.get_all_wallet_transactions('bbb')
    second_user_transactions = transaction_repository.get_all_wallet_transactions('ccc')

    assert len(first_user_second_address_transactions) != len(second_user_transactions)
    assert len(first_user_second_address_transactions) == 2
    assert len(second_user_transactions) == 1


def test_get_all_transactions(user_repository: IUserRepository, wallet_repository: IWalletRepository,
                                         admin_repository: IAdminRepository, transaction_repository: ITransactionRepository) -> None:
    first_user = user_repository.create_user('newuser')
    wallet_repository.create_wallet(first_user.api_key, 'aaa', 50)
    wallet_repository.create_wallet(first_user.api_key, 'bbb', 100)

    second_user = user_repository.create_user('otheruser')
    wallet_repository.create_wallet(second_user.api_key, 'ccc', 100)

    transaction_repository.create_transaction(Transaction('aaa', 'bbb', 20, 0))
    transactions = admin_repository.get_all_transactions()

    assert len(transactions) == 1

    transaction_repository.create_transaction(Transaction('bbb', 'ccc', 50, 10))
    transactions = admin_repository.get_all_transactions()

    assert len(transactions) == 2











