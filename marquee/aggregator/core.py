from __future__ import annotations
import asyncio
from datetime import date, timedelta
from marquee.connectors.registry import ConnectorRegistry
from marquee.models import Portfolio, PortfolioSnapshot, Position


class PortfolioAggregator:
    def __init__(self, registry: ConnectorRegistry) -> None:
        self._registry = registry

    async def get_portfolio(self) -> Portfolio:
        tasks = []
        for connector in self._registry.connectors:
            accounts = await connector.get_accounts()
            for account in accounts:
                tasks.append(connector.get_positions(account.id))

        results = await asyncio.gather(*tasks)
        positions: list[Position] = []
        for pos_list in results:
            positions.extend(pos_list)

        return Portfolio(positions=positions)

    async def get_historical_snapshots(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[PortfolioSnapshot]:
        to_date = to_date or date.today()
        from_date = from_date or (to_date - timedelta(days=365))

        tasks = []
        for connector in self._registry.connectors:
            accounts = await connector.get_accounts()
            for account in accounts:
                tasks.append(
                    connector.get_historical_values(account.id, from_date, to_date)
                )

        results = await asyncio.gather(*tasks)

        by_date: dict[date, float] = {}
        for snapshot_list in results:
            for snap in snapshot_list:
                by_date[snap.date] = by_date.get(snap.date, 0.0) + float(snap.total_value)

        from decimal import Decimal
        return [
            PortfolioSnapshot(date=d, total_value=Decimal(str(round(v, 2))), bank_name="all")
            for d, v in sorted(by_date.items())
        ]
