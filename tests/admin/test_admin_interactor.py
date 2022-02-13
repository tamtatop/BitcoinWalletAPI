from result import Err, Ok

from app.core.admin.interactor import (
    ADMIN_KEY,
    AdminError,
    AdminInteractor,
    GetStatisticsRequest,
)
from app.core.transaction.entity import Transaction
from tests.conftest import IAdminAndTransactionRepository


def test_admin_interactor_one_transaction(
    transaction_and_admin_repository: IAdminAndTransactionRepository,
) -> None:
    transaction_and_admin_repository.create_transaction(Transaction("a", "b", 1000, 10))

    admin_interactor = AdminInteractor(transaction_and_admin_repository)
    response = admin_interactor.get_statistics(GetStatisticsRequest(ADMIN_KEY))

    assert isinstance(response, Ok)
    assert response.value.profit == 10
    assert response.value.number_of_transactions == 1


def test_admin_interactor_many_transactions(
    transaction_and_admin_repository: IAdminAndTransactionRepository,
) -> None:
    transactions = [
        Transaction("a", "b", 1000, 10),
        Transaction("a", "b", 1000, 0),
        Transaction("a", "b", 1000, 100),
        Transaction("b", "a", 2000, 200),
        Transaction("b", "a", 2000, 0),
    ]

    for transaction in transactions:
        transaction_and_admin_repository.create_transaction(transaction)

    admin_interactor = AdminInteractor(transaction_and_admin_repository)
    response = admin_interactor.get_statistics(GetStatisticsRequest(ADMIN_KEY))

    assert isinstance(response, Ok)
    assert response.value.profit == sum(t.fee for t in transactions)
    assert response.value.number_of_transactions == len(transactions)


def test_wrong_admin_key(
    transaction_and_admin_repository: IAdminAndTransactionRepository,
) -> None:
    transaction_and_admin_repository.create_transaction(Transaction("a", "b", 1000, 10))

    admin_interactor = AdminInteractor(transaction_and_admin_repository)
    response = admin_interactor.get_statistics(GetStatisticsRequest("ABC ABC"))

    assert isinstance(response, Err)
    assert response.value == AdminError.INCORRECT_ADMIN_KEY
