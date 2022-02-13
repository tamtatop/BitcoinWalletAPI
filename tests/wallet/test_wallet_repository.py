from app.core.user.interactor import IUserRepository
from app.core.wallet.interactor import IWalletRepository


def test_create_and_get_wallet(
    user_repository: IUserRepository, wallet_repository: IWalletRepository
) -> None:
    user = user_repository.create_user("newuser")
    assert wallet_repository.create_wallet(user.api_key, "aaa", 50) is not None
    assert wallet_repository.create_wallet(user.api_key, "bbb", 100) is not None

    a_wallet = wallet_repository.get_wallet("aaa")
    b_wallet = wallet_repository.get_wallet("bbb")
    assert a_wallet is not None
    assert b_wallet is not None
    assert a_wallet.balance == 50
    assert b_wallet.owner_key == user.api_key
    assert b_wallet.balance == 100

    assert wallet_repository.get_wallet("ccc") is None


def test_get_user_wallets(
    user_repository: IUserRepository, wallet_repository: IWalletRepository
) -> None:
    user = user_repository.create_user("newuser")
    assert wallet_repository.create_wallet(user.api_key, "aaa", 50) is not None
    assert wallet_repository.create_wallet(user.api_key, "bbb", 100) is not None

    wallets = wallet_repository.get_user_wallets(user.api_key)
    for wallet in wallets:
        assert wallet.owner_key == "newuser"
        assert wallet.owner_key == user.api_key
        assert wallet.balance != 0

    assert wallets[0].address == "aaa"
    assert wallets[1].address == "bbb"


def test_get_user_wallets_amount(
    user_repository: IUserRepository, wallet_repository: IWalletRepository
) -> None:
    assert len(wallet_repository.get_user_wallets("nosuchuser")) == 0

    user = user_repository.create_user("newuser")
    assert len(wallet_repository.get_user_wallets(user.api_key)) == 0
    wallet_repository.create_wallet(user.api_key, "aaa", 50)
    assert len(wallet_repository.get_user_wallets(user.api_key)) == 1
    wallet_repository.create_wallet(user.api_key, "bbb", 100)
    assert len(wallet_repository.get_user_wallets(user.api_key)) == 2
    wallet_repository.create_wallet(user.api_key, "ccc", 100)
    assert len(wallet_repository.get_user_wallets(user.api_key)) == 3


def test_update_balance(
    user_repository: IUserRepository, wallet_repository: IWalletRepository
) -> None:
    user = user_repository.create_user("newuser")
    wallet_repository.create_wallet(user.api_key, "aaa", 50)
    wallet_repository.create_wallet(user.api_key, "bbb", 100)

    wallet_repository.update_balance("aaa", 0)
    wallet_repository.update_balance("bbb", 150)

    a_wallet = wallet_repository.get_wallet("aaa")
    b_wallet = wallet_repository.get_wallet("bbb")
    assert a_wallet is not None
    assert b_wallet is not None
    assert a_wallet.balance == 0
    assert b_wallet.balance == 150

    wallet_repository.update_balance("aaa", 1000)
    wallet_repository.update_balance("bbb", 1)

    a_wallet = wallet_repository.get_wallet("aaa")
    b_wallet = wallet_repository.get_wallet("bbb")
    assert a_wallet is not None
    assert b_wallet is not None
    assert a_wallet.balance == 1000
    assert b_wallet.balance == 1


def test_update_balance_additional(wallet_repository: IWalletRepository) -> None:
    test_user_api_key = "dummy key"
    test_wallet_address = "dummy address"
    test_init_balance = 1
    test_new_balance = 10000

    wallet_repository.create_wallet(
        test_user_api_key, test_wallet_address, test_init_balance
    )

    pre_check = wallet_repository.get_wallet(test_wallet_address)
    assert pre_check is not None
    assert pre_check.balance == test_init_balance

    wallet_repository.update_balance(test_wallet_address, test_new_balance)
    new_check = wallet_repository.get_wallet(test_wallet_address)
    assert new_check is not None
    assert new_check.balance == test_new_balance
