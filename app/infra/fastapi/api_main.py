from fastapi.applications import FastAPI

from app.core.facade import WalletService
from app.infra.fastapi.admin import admin_api
from app.infra.fastapi.transaction import transaction_api

from app.infra.fastapi.user import user_api
from app.infra.fastapi.wallet import wallet_api


def setup_fastapi(wallet_service: WalletService) -> FastAPI:
    app = FastAPI()

    app.include_router(user_api)
    app.include_router(wallet_api)
    app.include_router(admin_api)
    app.include_router(transaction_api)

    app.state.core = wallet_service

    return app
