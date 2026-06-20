from __future__ import annotations
from decimal import Decimal
from typing import Annotated, Union
from pydantic import BaseModel, Field, computed_field
from .instruments import Stock, ETF, FCN, Bond, Cash

AnyInstrument = Annotated[
    Union[Stock, ETF, FCN, Bond, Cash],
    Field(discriminator="type")
]


class Position(BaseModel):
    instrument: AnyInstrument
    quantity: Decimal
    avg_cost: Decimal       # cost per unit in instrument's currency
    current_price: Decimal  # current price per unit in instrument's currency
    bank_name: str
    account_id: str
    account_name: str = ""

    @computed_field
    @property
    def market_value(self) -> Decimal:
        return (self.quantity * self.current_price).quantize(Decimal("0.01"))

    @computed_field
    @property
    def cost_basis(self) -> Decimal:
        return (self.quantity * self.avg_cost).quantize(Decimal("0.01"))

    @computed_field
    @property
    def unrealized_pnl(self) -> Decimal:
        return (self.market_value - self.cost_basis).quantize(Decimal("0.01"))

    @computed_field
    @property
    def pnl_pct(self) -> Decimal:
        if self.cost_basis == 0:
            return Decimal("0")
        return ((self.unrealized_pnl / self.cost_basis) * 100).quantize(Decimal("0.01"))
