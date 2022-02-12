import uuid
from dataclasses import dataclass
from typing import Callable, Optional, Protocol

from app.core.key_generator import ApiKeyGenerator
from app.core.user.entity import User


@dataclass
class UserCreatedResponse:
    user: User


class IUserRepository(Protocol):
    def create_user(self, api_key: str) -> User:
        raise NotImplementedError()

    def get_user(self, user_api_key: str) -> Optional[User]:
        raise NotImplementedError()


class IUserInteractor(Protocol):
    def create_user(self) -> UserCreatedResponse:
        raise NotImplementedError()


@dataclass
class UserInteractor:
    repository: IUserRepository
    key_generator: ApiKeyGenerator

    def create_user(self) -> UserCreatedResponse:
        new_key = self.key_generator()
        return UserCreatedResponse(user=self.repository.create_user(new_key))
