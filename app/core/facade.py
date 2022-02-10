from dataclasses import dataclass

from result import Result
from app.core.admin.interactor import AdminError, AdminInteractor, GetStatisticsRequest, GetStatisticsResponse, IAdminInteractor, IAdminRepository
from app.core.transaction.interactor import GetTransactionsRequest, GetTransactionsResponse, ITransactionInteractor, ITransactionRepository, MakeTransactionRequest, MakeTransactionResponse, TransactionError, TransactionInteractor

from app.core.user.interactor import IUserInteractor, IUserRepository, UserCreatedResponse, UserInteractor, generate_new_unique_key
from app.core.wallet.interactor import (
    CreateWalletRequest,
    GetWalletRequest,
    IWalletInteractor,
    IWalletRepository,
    RandomCurrencyConverter,
    WalletError,
    WalletInteractor,
    WalletResponse,
)


@dataclass
class WalletService:
    user_interactor: IUserInteractor
    wallet_interactor: IWalletInteractor
    transaction_interactor: ITransactionInteractor
    admin_interactor: IAdminInteractor

    def create_user(self) -> UserCreatedResponse:
        return self.user_interactor.create_user()

    def create_wallet(
        self, request: CreateWalletRequest
    ) -> Result[WalletResponse, WalletError]:
        return self.wallet_interactor.create_wallet(request)

    def get_wallet(
        self, request: GetWalletRequest
    ) -> Result[WalletResponse, WalletError]:
        return self.wallet_interactor.get_wallet(request)

    # TODO:
    def make_transaction(
        self, request: MakeTransactionRequest
    ) -> Result[MakeTransactionResponse, TransactionError]:
        return self.transaction_interactor.make_transaction(request)

    # Wallet[Optional], apikey, Optional[walletaddress]
    # TODO:
    def get_transactions(
        self, request: GetTransactionsRequest
    ) -> GetTransactionsResponse:
        raise NotImplementedError()

    # above function
    # def get_wallet_transactions(self, request: GetWalletTransactionsRequest) -> GetTransactionsResponse:
    #     pass

    def get_statistics(self, request: GetStatisticsRequest) -> Result[GetStatisticsResponse, AdminError]:
        return self.admin_interactor.get_statistics(request)

    
    @classmethod
    def create(cls, 
            user_repository: IUserRepository,
            wallet_repository: IWalletRepository,
            transaction_repository: ITransactionRepository,
            admin_repository: IAdminRepository,
            ) -> "WalletService":
        return cls(
                UserInteractor(user_repository, generate_new_unique_key),
                WalletInteractor(wallet_repository, user_repository, RandomCurrencyConverter(), generate_new_unique_key),
                TransactionInteractor(transaction_repository, user_repository, wallet_repository),
                AdminInteractor(admin_repository)
        )

