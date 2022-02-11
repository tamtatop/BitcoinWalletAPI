from dataclasses import dataclass


@dataclass
class Wallet:
    address: str
    owner_key: str
    balance: int
