from unittest.mock import MagicMock

from app.core.key_generator import generate_new_user_key
from app.core.user.entity import User
from app.core.user.interactor import (
    IUserRepository,
    UserCreatedResponse,
    UserInteractor,
)


def test_unique_api_keys() -> None:
    keys = set()
    n = 1000
    for _ in range(n):
        keys.add(generate_new_user_key())
    assert len(keys) == n


def test_keys_unique_for_users() -> None:
    fake_repository = MagicMock()
    fake_repository.create_user = lambda api_key: User(api_key=api_key)
    user_interactor = UserInteractor(fake_repository, generate_new_user_key)

    keys = set()
    n = 1000
    for _ in range(n):
        keys.add(user_interactor.create_user().user.api_key)

    assert len(keys) == n


def test_create_user(user_repository: IUserRepository) -> None:
    interactor = UserInteractor(user_repository, generate_new_user_key)

    response = interactor.create_user()

    assert isinstance(response, UserCreatedResponse)
    assert user_repository.get_user(response.user.api_key) is not None
    assert user_repository.get_user("") is None


def test_create_many_user(user_repository: IUserRepository) -> None:
    interactor = UserInteractor(user_repository, generate_new_user_key)

    user_responses = [interactor.create_user() for _ in range(100)]

    for response in user_responses:
        assert isinstance(response, UserCreatedResponse)
        assert user_repository.get_user(response.user.api_key) is not None
