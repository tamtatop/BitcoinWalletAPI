from dataclasses import dataclass
from enum import Enum

from result import Result

from app.core.user.interactor import IUserInteractor, UserCreatedResponse
from app.core.wallet.interactor import (
    CreateWalletRequest,
    GetWalletRequest,
    GetWalletResponse,
    IWalletInteractor,
    WalletCreatedResponse,
    WalletError,
)


@dataclass
class WalletService:
    user_interactor: IUserInteractor
    wallet_interactor: IWalletInteractor
    # transaction_interactor:

    def create_user(self) -> UserCreatedResponse:
        return self.user_interactor.create_user()

    def create_wallet(
        self, request: CreateWalletRequest
    ) -> Result[WalletCreatedResponse, WalletError]:
        return self.wallet_interactor.create_wallet(request)

    def get_wallet(
        self, request: GetWalletRequest
    ) -> Result[GetWalletResponse, WalletError]:
        return self.wallet_interactor.get_wallet(request)

    def make_transaction(
        self, request: MakeTransactionRequest
    ) -> MakeTransactionResponse:
        pass

    # Wallet[Optional], apikey, Optional[walletaddress]
    def get_transactions(
        self, request: GetTransactionsRequest
    ) -> GetTransactionsResponse:
        pass

    # def get_wallet_transactions(self, request: GetWalletTransactionsRequest) -> GetTransactionsResponse:
    #     pass

    def get_statistics(self, request: GetStatisticsRequst) -> GetStatisticsResponse:
        pass
