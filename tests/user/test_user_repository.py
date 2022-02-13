from app.core.user.interactor import IUserRepository


def test_create_user(user_repository: IUserRepository) -> None:
    user_repository.create_user("abc")
    assert user_repository.get_user("abc") is not None

    user_repository.create_user("newuser")
    assert user_repository.get_user("newuser") is not None


def test_get_user(user_repository: IUserRepository) -> None:
    user_repository.create_user("newuser")
    user = user_repository.get_user("newuser")
    assert user is not None
    assert user.api_key == "newuser"

    assert user_repository.get_user("aaa") is None
    assert user_repository.get_user("abc") is None
