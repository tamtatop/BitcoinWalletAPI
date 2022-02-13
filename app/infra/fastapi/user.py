from fastapi import APIRouter, Depends

from app.core.facade import WalletService
from app.core.user.entity import User
from app.infra.fastapi.dependables import get_core

user_api = APIRouter()


@user_api.post("/users", response_model=User)
def create_user(core: WalletService = Depends(get_core)) -> User:
    user_created_response = core.create_user()
    return user_created_response.user
