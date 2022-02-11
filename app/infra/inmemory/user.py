from dataclasses import dataclass, field
from typing import Dict, Optional

from app.core.user.entity import User


@dataclass
class InMemoryUserRepository:
    data: Dict[str, User] = field(default_factory=dict)

    def create_user(self, api_key: str) -> User:
        user = User(api_key)
        self.data[api_key] = user
        return user

    def get_user(self, user_api_key: str) -> Optional[User]:
        if user_api_key in self.data.keys():
            return self.data[user_api_key]
        return None
