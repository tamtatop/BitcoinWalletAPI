from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from result.result import Ok

from app.core.facade import WalletService
from app.core.wallet.interactor import (
    MAX_WALLETS_PER_PERSON,
    CreateWalletRequest,
    GetWalletRequest,
    WalletError,
    WalletResponse,
)
from app.infra.fastapi.dependables import get_core

# TODO: fancy builder error handling
error_message: Dict[WalletError, str] = {
    WalletError.USER_NOT_FOUND: "User not found",
    WalletError.WALLET_NOT_FOUND: "Wallet not found",
    WalletError.WALLET_LIMIT_REACHED: f"Cannot create more than {MAX_WALLETS_PER_PERSON} wallets",
    WalletError.UNSUPPORTED_CURRENCY: "Unsupported Currency",
    WalletError.NOT_THIS_USERS_WALLET: "Provided wallet doesn't belong to provided user",
}

wallet_api = APIRouter()


@wallet_api.post("/wallets")
def create_wallet(
    api_key: str, core: WalletService = Depends(get_core)
) -> WalletResponse:
    request = CreateWalletRequest(user_api_key=api_key)
    wallet_created_response = core.create_wallet(request)

    if isinstance(wallet_created_response, Ok):
        return wallet_created_response.value
    else:
        raise HTTPException(
            status_code=400, detail=error_message[wallet_created_response.value]
        )


@wallet_api.get("/wallets/{address}")
def get_wallet(
    api_key: str, address: str, core: WalletService = Depends(get_core)
) -> WalletResponse:
    request = GetWalletRequest(api_key, address)

    get_wallet_response = core.get_wallet(request)

    if isinstance(get_wallet_response, Ok):
        return get_wallet_response.value
    else:
        raise HTTPException(
            status_code=400, detail=error_message[get_wallet_response.value]
        )
