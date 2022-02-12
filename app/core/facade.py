from dataclasses import dataclass

from result import Result

from app.core.admin.interactor import (
    AdminError,
    AdminInteractor,
    GetStatisticsRequest,
    GetStatisticsResponse,
    IAdminInteractor,
    IAdminRepository,
)
from app.core.currency_converter import BlockChainTickerCurrencyConverter
from app.core.key_generator import generate_new_user_key, generate_wallet_address
from app.core.transaction.fee_calculator import FeeCalculator
from app.core.transaction.interactor import (
    GetTransactionsRequest,
    GetTransactionsResponse,
    ITransactionInteractor,
    ITransactionRepository,
    MakeTransactionRequest,
    MakeTransactionResponse,
    TransactionError,
    TransactionInteractor,
)
from app.core.user.interactor import (
    IUserInteractor,
    IUserRepository,
    UserCreatedResponse,
    UserInteractor,
)
from app.core.wallet.interactor import (
    CreateWalletRequest,
    GetWalletRequest,
    IWalletInteractor,
    IWalletRepository,
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

    def make_transaction(
        self, request: MakeTransactionRequest
    ) -> Result[MakeTransactionResponse, TransactionError]:
        return self.transaction_interactor.make_transaction(request)

    def get_transactions(
        self, request: GetTransactionsRequest
    ) -> Result[GetTransactionsResponse, TransactionError]:
        return self.transaction_interactor.get_transactions(request)

    def get_statistics(
        self, request: GetStatisticsRequest
    ) -> Result[GetStatisticsResponse, AdminError]:
        return self.admin_interactor.get_statistics(request)

    @classmethod
    def create(
        cls,
        user_repository: IUserRepository,
        wallet_repository: IWalletRepository,
        transaction_repository: ITransactionRepository,
        admin_repository: IAdminRepository,
    ) -> "WalletService":
        return cls(
            UserInteractor(user_repository, generate_new_user_key),
            WalletInteractor(
                wallet_repository,
                user_repository,
                BlockChainTickerCurrencyConverter(),
                generate_wallet_address,
            ),
            TransactionInteractor(
                transaction_repository,
                user_repository,
                wallet_repository,
                FeeCalculator(),
            ),
            AdminInteractor(admin_repository),
        )
