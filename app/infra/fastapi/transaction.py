from typing import List

import pydantic
from fastapi import APIRouter, Depends
from result import Ok

from app.core.facade import WalletService
from app.core.transaction.entity import Transaction
from app.core.transaction.interactor import (
    GetTransactionsRequest,
    GetTransactionsResponse,
    MakeTransactionRequest,
    MakeTransactionResponse,
    TransactionError,
)
from app.infra.fastapi.dependables import get_core
from app.infra.fastapi.error_formatter import ErrorFormatterBuilder

error_formatter = (
    ErrorFormatterBuilder()
    .add_error_with_status_code(TransactionError.USER_NOT_FOUND, "User not found", 410)
    .add_error_with_status_code(
        TransactionError.WALLET_NOT_FOUND, "Wallet not found", 411
    )
    .add_error_with_status_code(
        TransactionError.SOURCE_WALLET_NOT_FOUND,
        "Transactions's source wallet not found",
        412,
    )
    .add_error_with_status_code(
        TransactionError.DESTINATION_WALLET_NOT_FOUND,
        "Transaction's destination wallet not found",
        413,
    )
    .add_error_with_status_code(
        TransactionError.INCORRECT_API_KEY, "Provided api key does now own source wallet", 414
    )
    .add_error_with_status_code(
        TransactionError.NOT_ENOUGH_AMOUNT_ON_SOURCE_ACCOUNT,
        "Not enough coins on source wallet to complete transaction",
        415,
    )
    .build()
)

transaction_api = APIRouter()


# fastapi is supposed to work with normal dataclasses but I guess it still does not work fully :shrug:
@pydantic.dataclasses.dataclass
class MakeTransactionResponsePydantic(MakeTransactionResponse):
    pass


@transaction_api.post(
    "/transactions",
    response_model=MakeTransactionResponsePydantic,
    responses=error_formatter.responses(),
)
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
        error_formatter.raise_http_exception(transaction_made_response.value)


# Couldn't make it work directly with fastapi :')
@pydantic.dataclasses.dataclass
class TransactionPydantic(Transaction):
    pass


@pydantic.dataclasses.dataclass
class GetTransactionsResponsePydantic:
    transactions: List[TransactionPydantic]


@transaction_api.get(
    "/transactions",
    response_model=GetTransactionsResponsePydantic,
    responses=error_formatter.responses(),
)
def get_transactions_for_user(
    api_key: str, core: WalletService = Depends(get_core)
) -> GetTransactionsResponse:
    request = GetTransactionsRequest(user_api_key=api_key, wallet_address=None)

    get_transactions_response = core.get_transactions(request)

    if isinstance(get_transactions_response, Ok):
        return get_transactions_response.value
    else:
        error_formatter.raise_http_exception(get_transactions_response.value)


@transaction_api.get(
    "/wallets/{address}/transactions",
    response_model=GetTransactionsResponsePydantic,
    responses=error_formatter.responses(),
)
def get_transactions_for_wallet(
    api_key: str, address: str, core: WalletService = Depends(get_core)
) -> GetTransactionsResponse:
    request = GetTransactionsRequest(user_api_key=api_key, wallet_address=address)

    get_transactions_response = core.get_transactions(request)

    if isinstance(get_transactions_response, Ok):
        return get_transactions_response.value
    else:
        error_formatter.raise_http_exception(get_transactions_response.value)
