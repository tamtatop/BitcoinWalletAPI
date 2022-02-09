from unittest.mock import MagicMock

from app.core.user.interactor import User, UserInteractor, generate_new_unique_key


def test_unique_api_keys() -> None:
    keys = set()
    n = 1000
    for _ in range(n):
        keys.add(generate_new_unique_key())
    assert len(keys) == n


def test_keys_unique_for_users() -> None:
    fake_repository = MagicMock()
    fake_repository.create_user = lambda api_key: User(api_key=api_key)
    user_interactor = UserInteractor(fake_repository, generate_new_unique_key)

    keys = set()
    n = 1000
    for _ in range(n):
        keys.add(user_interactor.create_user().user.api_key)

    assert len(keys) == n
