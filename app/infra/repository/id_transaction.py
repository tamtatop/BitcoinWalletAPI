from dataclasses import dataclass
from typing import Any, List

from app.core.transaction.entity import Transaction


@dataclass(eq=False)
class IdTransaction:
    id: int
    transaction: Transaction

    def is_related_to_addresses(self, addresses: List[str]) -> bool:
        return (
            self.transaction.source in addresses
            or self.transaction.destination in addresses
        )

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, IdTransaction) and self.id == other.id

    def __hash__(self) -> int:
        # use the hashcode of self.ssn since that is used
        # for equality checks as well
        return hash(self.id)

    @classmethod
    def from_row(cls, row: List[Any]) -> "IdTransaction":
        return cls(id=row[0], transaction=Transaction(*row[1:]))
