from __future__ import annotations
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, computed_field
from .position import Position


class PortfolioSnapshot(BaseModel):
    date: date
    total_value: Decimal
    bank_name: str


class Portfolio(BaseModel):
    positions: list[Position] = []
    snapshots: list[PortfolioSnapshot] = []

    model_config = {"arbitrary_types_allowed": True}

    @computed_field
    @property
    def total_value(self) -> Decimal:
        return sum((p.market_value for p in self.positions), Decimal("0")).quantize(Decimal("0.01"))

    @computed_field
    @property
    def total_cost(self) -> Decimal:
        return sum((p.cost_basis for p in self.positions), Decimal("0")).quantize(Decimal("0.01"))

    @computed_field
    @property
    def total_pnl(self) -> Decimal:
        return (self.total_value - self.total_cost).quantize(Decimal("0.01"))

    @computed_field
    @property
    def total_pnl_pct(self) -> Decimal:
        if self.total_cost == 0:
            return Decimal("0")
        return ((self.total_pnl / self.total_cost) * 100).quantize(Decimal("0.01"))
