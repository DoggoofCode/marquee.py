from __future__ import annotations
from datetime import date
from decimal import Decimal
from marquee.models import Portfolio, PortfolioSnapshot, Position


def allocation_by_type(portfolio: Portfolio) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for pos in portfolio.positions:
        key = pos.instrument.instrument_type.value
        totals[key] = totals.get(key, Decimal("0")) + pos.market_value
    return totals


def allocation_by_bank(portfolio: Portfolio) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for pos in portfolio.positions:
        totals[pos.bank_name] = totals.get(pos.bank_name, Decimal("0")) + pos.market_value
    return totals


def total_pnl(portfolio: Portfolio) -> Decimal:
    return portfolio.total_pnl


def ytd_return(snapshots: list[PortfolioSnapshot]) -> Decimal:
    if not snapshots:
        return Decimal("0")
    today = date.today()
    year_start = date(today.year, 1, 1)
    start_snap = next(
        (s for s in sorted(snapshots, key=lambda x: x.date) if s.date >= year_start),
        None,
    )
    end_snap = snapshots[-1] if snapshots else None
    if not start_snap or not end_snap or start_snap.total_value == 0:
        return Decimal("0")
    return (
        ((end_snap.total_value - start_snap.total_value) / start_snap.total_value) * 100
    ).quantize(Decimal("0.01"))


def top_movers(portfolio: Portfolio, n: int = 5) -> list[Position]:
    return sorted(portfolio.positions, key=lambda p: abs(p.unrealized_pnl), reverse=True)[:n]
