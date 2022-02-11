import random
from enum import Enum
from typing import Protocol

import httpx
from result import Err, Ok, Result

from app.core.btc_constants import SATOSHI_IN_BTC


class FiatCurrency(Enum):
    GEL = 0
    USD = 1
    EUR = 2
    RUB = 3


class ConversionError(Enum):
    UNSUPPORTED_CURRENCY = 1


class ICurrencyConverter(Protocol):
    def convert_btc_to_fiat(
        self, satoshis: int, currency: FiatCurrency
    ) -> Result[float, ConversionError]:
        raise NotImplementedError()


class BlockChainTickerCurrencyConverter:
    API_URL = "https://blockchain.info/ticker"
    fiat_currency_str = {
        FiatCurrency.USD: "USD",
        FiatCurrency.EUR: "EUR",
        FiatCurrency.RUB: "RUB",
    }

    def convert_btc_to_fiat(
        self, satoshis: int, currency: FiatCurrency
    ) -> Result[float, ConversionError]:
        response = httpx.get(BlockChainTickerCurrencyConverter.API_URL)

        if currency not in BlockChainTickerCurrencyConverter.fiat_currency_str:
            return Err(ConversionError.UNSUPPORTED_CURRENCY)

        last_conversion_rate = response.json()[
            BlockChainTickerCurrencyConverter.fiat_currency_str[currency]
        ]["last"]

        return Ok((satoshis / SATOSHI_IN_BTC) * last_conversion_rate)


class RandomCurrencyConverter:
    def convert_btc_to_fiat(
        self, satoshis: int, currency: FiatCurrency
    ) -> Result[float, ConversionError]:
        return Ok(random.random())
