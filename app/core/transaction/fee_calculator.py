from typing import Protocol

from app.core.wallet.interactor import Wallet


class IFeeCalculator(Protocol):
    def __call__(
        self, source_wallet: Wallet, destination_wallet: Wallet, transfer_amount: int
    ) -> int:
        raise NotImplementedError()


class FeeCalculator:
    INNER_API_TRANSACTION_RATE = 0
    OUTER_API_TRANSACTION_RATE = 1.5

    def __call__(
        self, source_wallet: Wallet, destination_wallet: Wallet, transfer_amount: int
    ) -> int:
        fee_rate: float
        if source_wallet.owner_key == destination_wallet.owner_key:
            fee_rate = FeeCalculator.INNER_API_TRANSACTION_RATE / 100
        else:
            fee_rate = FeeCalculator.OUTER_API_TRANSACTION_RATE / 100
        return round(transfer_amount * fee_rate)
