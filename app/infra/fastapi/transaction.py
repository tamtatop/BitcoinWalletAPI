from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from result import Ok

from app.core.facade import WalletService
from app.core.transaction.interactor import (
    GetTransactionsRequest,
    GetTransactionsResponse,
    MakeTransactionRequest,
    MakeTransactionResponse,
    TransactionError,
)
from app.infra.fastapi.dependables import get_core

error_message: Dict[TransactionError, str] = {
    TransactionError.USER_NOT_FOUND: "User not found",
    TransactionError.WALLET_NOT_FOUND: "Wallet not found",
    TransactionError.SOURCE_WALLET_NOT_FOUND: "Transactions's source wallet not found",
    TransactionError.DESTINATION_WALLET_NOT_FOUND: "Transactions's destination wallet not found",
    TransactionError.INCORRECT_API_KEY: "Incorrect Api Key",
    TransactionError.NOT_ENOUGH_AMOUNT_ON_SOURCE_ACCOUNT: "Not enough coins on source account to complete transaction",
}

transaction_api = APIRouter()


@transaction_api.post("/transactions")
def create_transaction(
    api_key: str,
    source: str,
    destination: str,
    amount: int,
    core: WalletService = Depends(get_core),
) -> MakeTransactionResponse:
    request = MakeTransactionRequest(
        user_api_key=api_key,
        source_address=source,
        destination_address=destination,
        amount=amount,
    )
    transaction_made_response = core.make_transaction(request)

    if isinstance(transaction_made_response, Ok):
        return transaction_made_response.value
    else:
        raise HTTPException(
            status_code=400, detail=error_message[transaction_made_response.value]
        )


@transaction_api.get("/transactions")
def get_transactions_for_user(
    api_key: str, core: WalletService = Depends(get_core)
) -> GetTransactionsResponse:
    request = GetTransactionsRequest(user_api_key=api_key, wallet_address=None)

    get_transactions_response = core.get_transactions(request)

    if isinstance(get_transactions_response, Ok):
        return get_transactions_response.value
    else:
        raise HTTPException(
            status_code=400, detail=error_message[get_transactions_response.value]
        )


@transaction_api.get("/wallets/{address}/transactions")
def get_transactions_for_wallet(
    api_key: str, address: str, core: WalletService = Depends(get_core)
) -> GetTransactionsResponse:
    request = GetTransactionsRequest(user_api_key=api_key, wallet_address=address)

    get_transactions_response = core.get_transactions(request)

    if isinstance(get_transactions_response, Ok):
        return get_transactions_response.value
    else:
        raise HTTPException(
            status_code=400, detail=error_message[get_transactions_response.value]
        )
