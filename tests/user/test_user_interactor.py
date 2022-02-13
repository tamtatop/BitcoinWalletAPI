from app.core.key_generator import ApiKeyGenerator
from app.core.user.interactor import (
    IUserRepository,
    UserCreatedResponse,
    UserInteractor,
)


def test_unique_api_keys(api_key_creator: ApiKeyGenerator) -> None:
    keys = set()
    n = 1000
    for _ in range(n):
        keys.add(api_key_creator())
    assert len(keys) == n


def test_keys_unique_for_users(
    user_repository: IUserRepository, api_key_creator: ApiKeyGenerator
) -> None:
    user_interactor = UserInteractor(user_repository, api_key_creator)

    keys = set()
    n = 1000
    for _ in range(n):
        keys.add(user_interactor.create_user().user.api_key)

    assert len(keys) == n


def test_create_user(
    user_repository: IUserRepository, api_key_creator: ApiKeyGenerator
) -> None:
    interactor = UserInteractor(user_repository, api_key_creator)

    response = interactor.create_user()

    assert isinstance(response, UserCreatedResponse)
    assert user_repository.get_user(response.user.api_key) is not None
    assert user_repository.get_user("") is None


def test_create_many_user(
    user_repository: IUserRepository, api_key_creator: ApiKeyGenerator
) -> None:
    interactor = UserInteractor(user_repository, api_key_creator)

    for _ in range(10000):
        user_response = interactor.create_user()
        assert isinstance(user_response, UserCreatedResponse)
        assert user_repository.get_user(user_response.user.api_key) is not None
