from starlette.requests import Request

from app.core.facade import WalletService


def get_core(request: Request) -> WalletService:
    btc_wallet_service: WalletService = request.app.state.core
    return btc_wallet_service
