from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date
from marquee.models import BankAccount, Position, PortfolioSnapshot


class BankConnector(ABC):
    connector_type: str = "Bank API"   # override in subclasses

    def __init__(self, bank_name: str) -> None:
        self.bank_name = bank_name

    @abstractmethod
    async def get_accounts(self) -> list[BankAccount]: ...

    @abstractmethod
    async def get_positions(self, account_id: str) -> list[Position]: ...

    @abstractmethod
    async def get_historical_values(
        self, account_id: str, from_date: date, to_date: date
    ) -> list[PortfolioSnapshot]: ...
