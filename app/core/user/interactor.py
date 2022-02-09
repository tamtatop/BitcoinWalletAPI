import uuid
from dataclasses import dataclass
from typing import Callable, Optional, Protocol


@dataclass
class User:
    api_key: str


@dataclass
class UserCreatedResponse:
    user: User


class IUserRepository(Protocol):
    def create_user(self, api_key: str) -> User:
        raise NotImplementedError()

    def get_user(self, user_api_key: str) -> Optional[User]:
        raise NotImplementedError()


UserApiKeyGenerator = Callable[[], str]


def generate_new_unique_key() -> str:
    return uuid.uuid1().hex


@dataclass
class UserInteractor:
    repository: IUserRepository
    key_generator: UserApiKeyGenerator

    def create_user(self) -> UserCreatedResponse:
        new_key = self.key_generator()
        return UserCreatedResponse(user=self.repository.create_user(new_key))
