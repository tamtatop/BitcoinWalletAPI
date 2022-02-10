from unittest.mock import MagicMock

from result import Err, Ok

from app.core.admin.interactor import ADMIN_KEY, AdminError, AdminInteractor, GetStatisticsRequest
from app.core.transaction.entity import Transaction


def test_admin_interactor_one_transaction() -> None:
    fake_repository = MagicMock()
    fake_repository.get_all_transactions = MagicMock(
        return_value=[Transaction("a", "b", 1000, 10)]
    )

    admin_interactor = AdminInteractor(fake_repository)
    response = admin_interactor.get_statistics(GetStatisticsRequest(ADMIN_KEY))

    fake_repository.get_all_transactions.assert_called_once()
    assert isinstance(response, Ok)
    assert response.value.profit == 10
    assert response.value.number_of_transactions == 1


def test_admin_interactor_many_transactions() -> None:
    fake_repository = MagicMock()
    fake_repository.get_all_transactions = MagicMock(
        return_value=[
            Transaction("a", "b", 1000, 10),
            Transaction("a", "b", 1000, 0),
            Transaction("a", "b", 1000, 100),
        ]
    )

    admin_interactor = AdminInteractor(fake_repository)
    response = admin_interactor.get_statistics(GetStatisticsRequest(ADMIN_KEY))

    fake_repository.get_all_transactions.assert_called_once()
    assert isinstance(response, Ok)
    assert response.value.profit == 110
    assert response.value.number_of_transactions == 3


def test_wrong_admin_key() -> None:
    fake_repository = MagicMock()
    fake_repository.get_all_transactions = MagicMock(
        return_value=[Transaction("a", "b", 1000, 10)]
    )

    admin_interactor = AdminInteractor(fake_repository)
    response = admin_interactor.get_statistics(GetStatisticsRequest("ABC ABC"))
    fake_repository.get_all_transactions.assert_not_called()
    assert isinstance(response, Err)
    assert response.value == AdminError.INCORRECT_ADMIN_KEY
