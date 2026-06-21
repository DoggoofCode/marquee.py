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
    coupon_rate: Decimal        # annual rate, e.g. 0.09 = 9%
    barrier_pct: Decimal        # barrier as fraction of strike, e.g. 0.60
    strike_price: Decimal       # underlying price at issuance
    notional: Decimal           # face value per unit, e.g. 1000
    issue_date: date
    maturity_date: date

    @property
    def instrument_type(self) -> InstrumentType:
        return self.type

    @property
    def barrier_price(self) -> Decimal:
        return (self.strike_price * self.barrier_pct).quantize(Decimal("0.01"))

    @property
    def display_name(self) -> str:
        return self.name

    def mark_to_market(self, underlying_price: Decimal, pricing_date: date) -> Decimal:
        """Simplified FCN MTM: par+accrued above barrier, capital-at-risk below."""
        if underlying_price >= self.barrier_price:
            days = (pricing_date - self.issue_date).days
            accrued = self.coupon_rate * Decimal(str(days)) / Decimal("365")
            return (self.notional * (1 + accrued)).quantize(Decimal("0.01"))
        else:
            return (self.notional * underlying_price / self.strike_price).quantize(Decimal("0.01"))


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
