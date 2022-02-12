import uuid
from typing import Callable

ApiKeyGenerator = Callable[[], str]


def generate_wallet_address() -> str:
    return "wallet-" + uuid.uuid1().hex


def generate_new_user_key() -> str:
    return "user-" + uuid.uuid1().hex
