import pydantic
from fastapi import APIRouter, Depends
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
from app.infra.fastapi.error_formatter import ErrorFormatterBuilder

error_formatter = (
    ErrorFormatterBuilder()
    .add_error_with_status_code(WalletError.USER_NOT_FOUND, "User not found", 410)
    .add_error_with_status_code(WalletError.WALLET_NOT_FOUND, "Wallet not found", 411)
    .add_error_with_status_code(
        WalletError.WALLET_LIMIT_REACHED,
        f"Cannot create more than {MAX_WALLETS_PER_PERSON} wallets",
        412,
    )
    .add_error_with_status_code(
        WalletError.UNSUPPORTED_CURRENCY, "Unsupported Currency", 413
    )
    .add_error_with_status_code(
        WalletError.NOT_THIS_USERS_WALLET,
        "Provided wallet doesn't belong to provided user",
        414,
    )
    .build()
)

wallet_api = APIRouter()


# fastapi is supposed to work with normal dataclasses but I guess it still does not work fully :shrug:
@pydantic.dataclasses.dataclass
class WalletResponsePydantic(WalletResponse):
    pass


@wallet_api.post(
    "/wallets",
    response_model=WalletResponsePydantic,
    responses=error_formatter.responses(),
)
def create_wallet(
    api_key: str, core: WalletService = Depends(get_core)
) -> WalletResponse:
    request = CreateWalletRequest(user_api_key=api_key)
    wallet_created_response = core.create_wallet(request)

    if isinstance(wallet_created_response, Ok):
        return wallet_created_response.value
    else:
        error_formatter.raise_http_exception(wallet_created_response.value)


@wallet_api.get(
    "/wallets/{address}",
    response_model=WalletResponsePydantic,
    responses=error_formatter.responses(),
)
def get_wallet(
    api_key: str, address: str, core: WalletService = Depends(get_core)
) -> WalletResponse:
    request = GetWalletRequest(api_key, address)

    get_wallet_response = core.get_wallet(request)

    if isinstance(get_wallet_response, Ok):
        return get_wallet_response.value
    else:
        error_formatter.raise_http_exception(get_wallet_response.value)
