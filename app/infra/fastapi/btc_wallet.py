from typing import Dict, Optional, Union
from app.core.facade import WalletService
from app.core.wallet.interactor import MAX_WALLETS_PER_PERSON, GetWalletRequest, Wallet, WalletError, WalletResponse
from app.core.user.interactor import User, UserCreatedResponse
from app.core.wallet.interactor import CreateWalletRequest
from app.infra.fastapi.dependables import get_core
from fastapi import APIRouter, Depends, Response, HTTPException


# app = FastAPI()

# app.include_router(cashier_api)
# app.include_router(customer_api)
# app.include_router(manager_api)

# app.state.core = StoreService.create(store_repository=setup_book_repository())

# TODO: fancy builder error handling
error_message: Dict[WalletError, str] = {
    WalletError.USER_NOT_FOUND: "User not found",
    WalletError.WALLET_NOT_FOUND: "Wallet not found",
    WalletError.WALLET_LIMIT_REACHED: f"Cannot create more than {MAX_WALLETS_PER_PERSON} wallets",
}


btc_wallet_api = APIRouter()

@btc_wallet_api.post("/users")
def create_user(
	core: WalletService = Depends(get_core)
) -> User:
	user_created_response = core.create_user()

	return user_created_response.user

@btc_wallet_api.post("/wallets")
def create_wallet(
	api_key: str,
	core: WalletService = Depends(get_core)
) -> WalletResponse:
	request = CreateWalletRequest(user_api_key=api_key)
	wallet_created_response = core.create_wallet(request)

	if wallet_created_response.is_ok():
		return wallet_created_response.value
	else:
		raise HTTPException(status_code=400, detail=error_message[wallet_created_response.value])


@btc_wallet_api.get("/wallets/{address}")
def get_wallet(
	api_key: str,
	address: str,
	core: WalletService = Depends(get_core)
) -> WalletResponse:
	request = GetWalletRequest(api_key, address)

	get_wallet_response = core.get_wallet(request)

	if get_wallet_response.is_ok():
		return get_wallet_response.value
	else:
		raise HTTPException(status_code=400, detail=error_message[get_wallet_response.value])

















