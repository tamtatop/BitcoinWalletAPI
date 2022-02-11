from dataclasses import dataclass


@dataclass
class Transaction:
    source: str
    destination: str
    amount: int
    fee: int
