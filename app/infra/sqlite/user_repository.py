import sqlite3
from dataclasses import dataclass
from typing import Optional

from app.core.user.interactor import IUserRepository, User


@dataclass
class UserRepository:
    def __init__(self) -> None:
        self.conn = sqlite3.connect("db.db", check_same_thread=False)
        self.conn.executescript(
            """
            create table if not exists Users (
                api_key text primary key
            );
            """
        )
        self.conn.commit()

    def create_user(self, api_key: str) -> User:
        self.conn.execute(
            " INSERT INTO Users VALUES (?)", (api_key, )
        )
        self.conn.commit()
        return User(api_key)

    def get_user(self, user_api_key: str) -> Optional[User]:
        for row in self.conn.execute(
                " SELECT * FROM Users WHERE api_key = ?", (user_api_key, )
        ):
            return User(*row)

        return None


repo = UserRepository()
user = repo.create_user("1234567")
curr_user_incorrect = repo.get_user("777")
curr_user_correct = repo.get_user("1234567")
curr_user_correct = repo.get_user("123456")
print(curr_user_correct)