from app.core.admin.interactor import IAdminRepository
from app.core.transaction.entity import Transaction
from app.core.transaction.interactor import ITransactionRepository
from app.core.user.interactor import IUserRepository
from app.core.wallet.interactor import IWalletRepository


def test_create_transaction(
    user_repository: IUserRepository,
    wallet_repository: IWalletRepository,
    transaction_repository: ITransactionRepository,
) -> None:
    first_user = user_repository.create_user("newuser")
    wallet_repository.create_wallet(first_user.api_key, "aaa", 50)
    wallet_repository.create_wallet(first_user.api_key, "bbb", 100)

    second_user = user_repository.create_user("otheruser")
    wallet_repository.create_wallet(second_user.api_key, "ccc", 100)

    transaction_repository.create_transaction(Transaction("aaa", "bbb", 20, 0))
    first_address_transactions = transaction_repository.get_all_wallet_transactions(
        "aaa"
    )
    second_address_transactions = transaction_repository.get_all_wallet_transactions(
        "bbb"
    )

    assert len(first_address_transactions) == len(second_address_transactions)
    assert len(first_address_transactions) == 1

    assert first_address_transactions[0].source == "aaa"
    assert first_address_transactions[0].destination == "bbb"
    assert first_address_transactions[0].amount == 20
    assert first_address_transactions[0].fee == 0

    transaction_repository.create_transaction(Transaction("bbb", "ccc", 50, 10))
    third_address_transactions = transaction_repository.get_all_wallet_transactions(
        "ccc"
    )
    second_address_transactions = transaction_repository.get_all_wallet_transactions(
        "bbb"
    )

    assert len(first_address_transactions) != len(second_address_transactions)
    assert len(third_address_transactions) == 1
    assert len(second_address_transactions) == 2

    assert third_address_transactions[0].source == "bbb"
    assert third_address_transactions[0].destination == "ccc"
    assert third_address_transactions[0].amount == 50
    assert third_address_transactions[0].fee == 10


def test_get_all_user_transactions(
    user_repository: IUserRepository,
    wallet_repository: IWalletRepository,
    transaction_repository: ITransactionRepository,
) -> None:
    first_user = user_repository.create_user("newuser")
    wallet_repository.create_wallet(first_user.api_key, "aaa", 50)
    wallet_repository.create_wallet(first_user.api_key, "bbb", 100)

    second_user = user_repository.create_user("otheruser")
    wallet_repository.create_wallet(second_user.api_key, "ccc", 100)

    transaction_repository.create_transaction(Transaction("aaa", "bbb", 20, 0))
    first_user_transactions = transaction_repository.get_all_user_transactions(
        first_user.api_key
    )

    assert len(first_user_transactions) == 1

    transaction_repository.create_transaction(Transaction("bbb", "ccc", 50, 10))
    first_user_transactions = transaction_repository.get_all_user_transactions(
        "newuser"
    )
    second_user_transactions = transaction_repository.get_all_user_transactions(
        "otheruser"
    )

    assert len(first_user_transactions) != len(second_user_transactions)
    assert len(first_user_transactions) == 2
    assert len(second_user_transactions) == 1


def test_get_all_wallet_transactions(
    user_repository: IUserRepository,
    wallet_repository: IWalletRepository,
    transaction_repository: ITransactionRepository,
) -> None:
    first_user = user_repository.create_user("newuser")
    wallet_repository.create_wallet(first_user.api_key, "aaa", 50)
    wallet_repository.create_wallet(first_user.api_key, "bbb", 100)

    second_user = user_repository.create_user("otheruser")
    wallet_repository.create_wallet(second_user.api_key, "ccc", 100)

    transaction_repository.create_transaction(Transaction("aaa", "bbb", 20, 0))
    first_user_first_address_transactions = (
        transaction_repository.get_all_wallet_transactions("aaa")
    )
    first_user_second_address_transactions = (
        transaction_repository.get_all_wallet_transactions("bbb")
    )

    assert len(first_user_second_address_transactions) == len(
        first_user_first_address_transactions
    )
    assert len(first_user_first_address_transactions) == 1
    assert (
        first_user_first_address_transactions[0]
        == first_user_second_address_transactions[0]
    )

    transaction_repository.create_transaction(Transaction("bbb", "ccc", 50, 10))
    first_user_second_address_transactions = (
        transaction_repository.get_all_wallet_transactions("bbb")
    )
    second_user_transactions = transaction_repository.get_all_wallet_transactions("ccc")

    assert len(first_user_second_address_transactions) != len(second_user_transactions)
    assert len(first_user_second_address_transactions) == 2
    assert len(second_user_transactions) == 1


def test_get_all_transactions(
    user_repository: IUserRepository,
    wallet_repository: IWalletRepository,
    admin_repository: IAdminRepository,
    transaction_repository: ITransactionRepository,
) -> None:
    first_user = user_repository.create_user("newuser")
    wallet_repository.create_wallet(first_user.api_key, "aaa", 50)
    wallet_repository.create_wallet(first_user.api_key, "bbb", 100)

    second_user = user_repository.create_user("otheruser")
    wallet_repository.create_wallet(second_user.api_key, "ccc", 100)

    transaction_repository.create_transaction(Transaction("aaa", "bbb", 20, 0))
    transactions = admin_repository.get_all_transactions()

    assert len(transactions) == 1

    transaction_repository.create_transaction(Transaction("bbb", "ccc", 50, 10))
    transactions = admin_repository.get_all_transactions()

    assert len(transactions) == 2


def test_transaction_to_self(
    user_repository: IUserRepository,
    wallet_repository: IWalletRepository,
    admin_repository: IAdminRepository,
    transaction_repository: ITransactionRepository,
) -> None:
    first_user = user_repository.create_user("newuser")
    wallet_repository.create_wallet(first_user.api_key, "aaa", 100)
    wallet_repository.create_wallet(first_user.api_key, "bbb", 100)

    transaction_repository.create_transaction(Transaction("aaa", "bbb", 20, 0))
    assert len(transaction_repository.get_all_user_transactions("newuser")) == 1
    assert len(transaction_repository.get_all_wallet_transactions("aaa")) == 1
    assert len(admin_repository.get_all_transactions()) == 1

    transaction_repository.create_transaction(Transaction("aaa", "bbb", 20, 0))
    assert len(transaction_repository.get_all_user_transactions("newuser")) == 2
    assert len(transaction_repository.get_all_wallet_transactions("aaa")) == 2
    assert len(admin_repository.get_all_transactions()) == 2


def test_transaction_two_identical(
    user_repository: IUserRepository,
    wallet_repository: IWalletRepository,
    admin_repository: IAdminRepository,
    transaction_repository: ITransactionRepository,
) -> None:
    tamta = user_repository.create_user("tamta")
    khokho = user_repository.create_user("khokho")

    wallet_repository.create_wallet(tamta.api_key, "my_rich_wallet", 100000000000)
    wallet_repository.create_wallet(khokho.api_key, "poor_boy", 0)

    transaction_repository.create_transaction(
        Transaction("my_rich_wallet", "poor_boy", 1, 0)
    )
    assert len(transaction_repository.get_all_user_transactions("tamta")) == 1
    assert len(transaction_repository.get_all_user_transactions("khokho")) == 1
    assert (
        len(transaction_repository.get_all_wallet_transactions("my_rich_wallet")) == 1
    )
    assert len(transaction_repository.get_all_wallet_transactions("poor_boy")) == 1
    assert len(admin_repository.get_all_transactions()) == 1

    transaction_repository.create_transaction(
        Transaction("my_rich_wallet", "poor_boy", 1, 0)
    )
    assert len(transaction_repository.get_all_user_transactions("tamta")) == 2
    assert len(transaction_repository.get_all_user_transactions("khokho")) == 2
    assert (
        len(transaction_repository.get_all_wallet_transactions("my_rich_wallet")) == 2
    )
    assert len(transaction_repository.get_all_wallet_transactions("poor_boy")) == 2
    assert len(admin_repository.get_all_transactions()) == 2
