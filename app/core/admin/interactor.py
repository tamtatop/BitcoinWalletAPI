from dataclasses import dataclass
from enum import Enum
from typing import List, Protocol

from result import Err, Ok, Result

from app.core.transaction.entity import Transaction


class AdminError(Enum):
    INCORRECT_ADMIN_KEY = 0


@dataclass
class GetStatisticsRequest:
    admin_key: str


@dataclass
class GetStatisticsResponse:
    number_of_transactions: int
    profit: int




class IAdminRepository(Protocol):
    def get_all_transactions(self) -> List[Transaction]:
        raise NotImplementedError()

ADMIN_KEY = "sezam-gaighe"
class IAdminInteractor(Protocol):
    def get_statistics(
        self, request: GetStatisticsRequest
    ) -> Result[GetStatisticsResponse, AdminError]:
        raise NotImplementedError()

@dataclass
class AdminInteractor:
    admin_repository: IAdminRepository

    def get_statistics(
        self, request: GetStatisticsRequest
    ) -> Result[GetStatisticsResponse, AdminError]:
        admin_key = request.admin_key
        if admin_key != ADMIN_KEY:
            return Err(AdminError.INCORRECT_ADMIN_KEY)
        transactions = self.admin_repository.get_all_transactions()
        return Ok(
            GetStatisticsResponse(
                number_of_transactions=len(transactions),
                profit=sum([t.fee for t in transactions]),
            )
        )
