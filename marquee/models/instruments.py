from __future__ import annotations
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Literal
from pydantic import BaseModel


class InstrumentType(StrEnum):
    STOCK = "Stock"
    ETF = "ETF"
    FCN = "FCN"
    BOND = "Bond"
    CASH = "Cash"


class Instrument(BaseModel):
    isin: str = ""
    currency: str = "USD"

    @property
    def instrument_type(self) -> InstrumentType:
        raise NotImplementedError


class Stock(Instrument):
    type: Literal[InstrumentType.STOCK] = InstrumentType.STOCK
    ticker: str
    name: str

    @property
    def instrument_type(self) -> InstrumentType:
        return self.type

    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.ticker})"


class ETF(Instrument):
    type: Literal[InstrumentType.ETF] = InstrumentType.ETF
    ticker: str
    name: str
    ter: Decimal = Decimal("0")

    @property
    def instrument_type(self) -> InstrumentType:
        return self.type

    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.ticker})"


class FCN(Instrument):
    type: Literal[InstrumentType.FCN] = InstrumentType.FCN
    name: str
    underlying_ticker: str
    coupon_rate: Decimal
    barrier_pct: Decimal
    maturity_date: date

    @property
    def instrument_type(self) -> InstrumentType:
        return self.type

    @property
    def display_name(self) -> str:
        return self.name


class Bond(Instrument):
    type: Literal[InstrumentType.BOND] = InstrumentType.BOND
    name: str
    coupon_rate: Decimal
    maturity_date: date

    @property
    def instrument_type(self) -> InstrumentType:
        return self.type

    @property
    def display_name(self) -> str:
        return self.name


class Cash(Instrument):
    type: Literal[InstrumentType.CASH] = InstrumentType.CASH

    @property
    def instrument_type(self) -> InstrumentType:
        return self.type

    @property
    def display_name(self) -> str:
        return f"Cash ({self.currency})"
