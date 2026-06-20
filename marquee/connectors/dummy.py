from __future__ import annotations
import hashlib
import random
from datetime import date, timedelta
from decimal import Decimal
from marquee.models import BankAccount, Position, PortfolioSnapshot
from marquee.models.instruments import Stock, ETF, FCN, Cash
from .base import BankConnector

_BANKS: dict[str, dict] = {
    "Alpen Bank": {
        "accounts": [
            {"id": "alpen-001", "name": "Investment Portfolio", "type": "custody"},
            {"id": "alpen-002", "name": "Trading Account", "type": "trading"},
        ],
        "seed": 42,
    },
    "Helvetia Capital": {
        "accounts": [
            {"id": "helv-001", "name": "Core Holdings", "type": "custody"},
            {"id": "helv-002", "name": "Structured Products", "type": "custody"},
        ],
        "seed": 99,
    },
}

_STOCKS = [
    Stock(ticker="AAPL", name="Apple Inc.", currency="USD", isin="US0378331005"),
    Stock(ticker="GOOGL", name="Alphabet Inc.", currency="USD", isin="US02079K3059"),
    Stock(ticker="NOVN.SW", name="Novartis AG", currency="CHF", isin="CH0012005267"),
    Stock(ticker="NESN.SW", name="Nestlé S.A.", currency="CHF", isin="CH0038863350"),
    Stock(ticker="MSFT", name="Microsoft Corp.", currency="USD", isin="US5949181045"),
]

_ETFS = [
    ETF(ticker="SPY", name="SPDR S&P 500 ETF", currency="USD", ter=Decimal("0.0009"), isin="US78462F1030"),
    ETF(ticker="VTI", name="Vanguard Total Market ETF", currency="USD", ter=Decimal("0.0003"), isin="US9229087690"),
    ETF(ticker="CHSPI.SW", name="iShares Core SPI ETF", currency="CHF", ter=Decimal("0.001"), isin="CH0237935652"),
]

_FCNS = [
    FCN(
        name="FCN on AAPL 8% p.a.",
        underlying_ticker="AAPL",
        coupon_rate=Decimal("0.08"),
        barrier_pct=Decimal("0.60"),
        maturity_date=date(2025, 12, 19),
        currency="USD",
        isin="XS0000000001",
    ),
    FCN(
        name="FCN on NESN 6% p.a.",
        underlying_ticker="NESN.SW",
        coupon_rate=Decimal("0.06"),
        barrier_pct=Decimal("0.65"),
        maturity_date=date(2026, 3, 20),
        currency="CHF",
        isin="XS0000000002",
    ),
]

_PRICES: dict[str, Decimal] = {
    "AAPL": Decimal("189.30"),
    "GOOGL": Decimal("175.50"),
    "NOVN.SW": Decimal("93.20"),
    "NESN.SW": Decimal("76.40"),
    "MSFT": Decimal("415.80"),
    "SPY": Decimal("543.20"),
    "VTI": Decimal("265.10"),
    "CHSPI.SW": Decimal("198.60"),
    "FCN on AAPL 8% p.a.": Decimal("1000.00"),
    "FCN on NESN 6% p.a.": Decimal("1000.00"),
}

_HOLDINGS: dict[str, list] = {
    "alpen-001": [_STOCKS[0], _STOCKS[2], _ETFS[0], _ETFS[2]],
    "alpen-002": [_STOCKS[1], _STOCKS[3], _ETFS[1]],
    "helv-001": [_STOCKS[4], _STOCKS[2], _ETFS[0], _ETFS[2]],
    "helv-002": [_FCNS[0], _FCNS[1]],
}


def _ticker(instrument) -> str:
    if hasattr(instrument, "ticker"):
        return instrument.ticker
    return instrument.name


def _price(instrument) -> Decimal:
    key = _ticker(instrument) if hasattr(instrument, "ticker") else instrument.name
    return _prices_with_noise(key)


def _prices_with_noise(key: str) -> Decimal:
    base = _PRICES.get(key, Decimal("100"))
    seed = int(hashlib.md5(key.encode()).hexdigest(), 16) % 20 - 10
    noise_pct = Decimal(str(seed / 100))
    return (base * (1 + noise_pct)).quantize(Decimal("0.01"))


class DummyConnector(BankConnector):
    def __init__(self, bank_name: str) -> None:
        super().__init__(bank_name)
        if bank_name not in _BANKS:
            raise ValueError(f"Unknown dummy bank: {bank_name}. Choose from {list(_BANKS)}")
        self._cfg = _BANKS[bank_name]
        self._rng = random.Random(self._cfg["seed"])

    async def get_accounts(self) -> list[BankAccount]:
        return [
            BankAccount(
                id=acc["id"],
                bank_name=self.bank_name,
                account_name=acc["name"],
                account_type=acc["type"],
            )
            for acc in self._cfg["accounts"]
        ]

    async def get_positions(self, account_id: str) -> list[Position]:
        instruments = _HOLDINGS.get(account_id, [])
        positions = []
        for inst in instruments:
            price = _price(inst)
            qty_seed = int(hashlib.md5(f"{account_id}-{_ticker(inst)}".encode()).hexdigest(), 16) % 90 + 10
            qty = Decimal(str(qty_seed))
            cost = (price * Decimal("0.88")).quantize(Decimal("0.01"))  # ~12% gain basis
            account_name = next(
                (a["name"] for a in self._cfg["accounts"] if a["id"] == account_id), ""
            )
            positions.append(
                Position(
                    instrument=inst,
                    quantity=qty,
                    avg_cost=cost,
                    current_price=price,
                    bank_name=self.bank_name,
                    account_id=account_id,
                    account_name=account_name,
                )
            )
        return positions

    async def get_historical_values(
        self, account_id: str, from_date: date, to_date: date
    ) -> list[PortfolioSnapshot]:
        snapshots = []
        positions = await self.get_positions(account_id)
        base_value = float(sum(p.market_value for p in positions))
        days = (to_date - from_date).days
        rng = random.Random(self._cfg["seed"] + hash(account_id))
        value = base_value * 0.82  # start ~18% below current
        for i in range(days + 1):
            day = from_date + timedelta(days=i)
            drift = rng.uniform(-0.008, 0.011)
            value = max(value * (1 + drift), base_value * 0.5)
            snapshots.append(
                PortfolioSnapshot(
                    date=day,
                    total_value=Decimal(str(round(value, 2))),
                    bank_name=self.bank_name,
                )
            )
        snapshots[-1] = PortfolioSnapshot(
            date=to_date,
            total_value=Decimal(str(round(base_value, 2))),
            bank_name=self.bank_name,
        )
        return snapshots
