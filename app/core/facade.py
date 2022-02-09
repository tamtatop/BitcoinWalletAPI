from enum import Enum


class Errors(Enum):
    pass


class WalletCreatedRequest:
    pass


class GetWalletRequest:
    pass


class MakeTransactionRequest:
    pass


class GetTransactionsRequest:
    pass


class GetStatisticsRequst:
    pass


class WalletService:
    def create_user(self) -> UserCreatedResponse:
        pass

    def create_wallet(self, request: WalletCreatedRequest) -> WalletCreatedResponse:
        pass

    def get_wallet(self, request: GetWalletRequest) -> WalletResponse:
        pass

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
