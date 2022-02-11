import uuid
from typing import Callable

ApiKeyGenerator = Callable[[], str]


def generate_wallet_address() -> str:
    return uuid.uuid1().hex
