"""Live connector that fetches real prices and history from Yahoo Finance."""
from __future__ import annotations
import asyncio
from datetime import date
from decimal import Decimal

import pandas as pd

from marquee.models import BankAccount, Position, PortfolioSnapshot
from marquee.models.instruments import Stock, ETF, FCN
from .base import BankConnector

# ── Instrument definitions ────────────────────────────────────────────────────

_INSTRUMENTS: dict[str, Stock | ETF | FCN] = {
    "AAPL": Stock(ticker="AAPL", name="Apple Inc.",          currency="USD", isin="US0378331005"),
    "MSFT": Stock(ticker="MSFT", name="Microsoft Corp.",     currency="USD", isin="US5949181045"),
    "GOOGL": Stock(ticker="GOOGL", name="Alphabet Inc.",     currency="USD", isin="US02079K3059"),
    "AMZN": Stock(ticker="AMZN", name="Amazon.com Inc.",     currency="USD", isin="US0231351067"),
    "NVDA": Stock(ticker="NVDA", name="NVIDIA Corp.",        currency="USD", isin="US67066G1040"),
    "META": Stock(ticker="META", name="Meta Platforms Inc.", currency="USD", isin="US30303M1027"),
    "TSLA": Stock(ticker="TSLA", name="Tesla Inc.",          currency="USD", isin="US88160R1014"),
    "SPY":  ETF(ticker="SPY",  name="SPDR S&P 500 ETF",         currency="USD", ter=Decimal("0.0009")),
    "QQQ":  ETF(ticker="QQQ",  name="Invesco QQQ Trust",         currency="USD", ter=Decimal("0.0020")),
    "VTI":  ETF(ticker="VTI",  name="Vanguard Total Mkt ETF",    currency="USD", ter=Decimal("0.0003")),
    "IVV":  ETF(ticker="IVV",  name="iShares Core S&P 500 ETF",  currency="USD", ter=Decimal("0.0003")),
}

_FCN_NVDA = FCN(
    name="FCN on NVDA 9% p.a.",
    underlying_ticker="NVDA",
    coupon_rate=Decimal("0.09"),
    barrier_pct=Decimal("0.60"),
    strike_price=Decimal("135.00"),   # NVDA at issuance (Dec 2025)
    notional=Decimal("1000.00"),
    issue_date=date(2025, 12, 19),
    maturity_date=date(2026, 12, 19),
    currency="USD",
    isin="XS1000000001",
)

_FCN_REGISTRY: dict[str, FCN] = {
    "FCN_NVDA": _FCN_NVDA,
}

# ── Bank / account / holdings config ─────────────────────────────────────────

_BANKS = {
    "Meridian Wealth": {
        "accounts": [
            {"id": "mw-001", "name": "Growth Portfolio", "type": "custody"},
            {"id": "mw-002", "name": "Trading Desk",    "type": "trading"},
        ],
    },
    "Atlas Capital": {
        "accounts": [
            {"id": "ac-001", "name": "Core Holdings",      "type": "custody"},
            {"id": "ac-002", "name": "Structured Products", "type": "custody"},
        ],
    },
}

# (ticker_or_fcn_key, quantity, avg_cost_usd)
_HOLDINGS: dict[str, list[tuple]] = {
    "mw-001": [
        ("AAPL", 50, 145.00),
        ("MSFT", 30, 330.00),
        ("SPY",  40, 420.00),
        ("QQQ",  25, 350.00),
    ],
    "mw-002": [
        ("GOOGL", 20, 130.00),
        ("AMZN",  15, 158.00),
        ("NVDA",  35,  85.00),
    ],
    "ac-001": [
        ("META", 40, 320.00),
        ("IVV",  20, 415.00),
        ("VTI",  60, 208.00),
    ],
    "ac-002": [
        ("TSLA",     25, 215.00),
        ("AAPL",     20, 152.00),
        ("FCN_NVDA", 50, 1000.00),   # 50 units, $1000 notional each
    ],
}

# ── Module-level price + history cache (shared across all connector instances) ─

_price_cache: dict[str, Decimal] = {}
_hist_cache: dict[str, pd.Series] = {}   # ticker → daily close prices (plain date index)


async def _ensure_tickers(tickers: list[str]) -> None:
    """Download and cache price history for any not-yet-fetched tickers."""
    new = [t for t in tickers if t not in _price_cache]
    if not new:
        return

    import yfinance as yf

    def _download() -> pd.DataFrame:
        return yf.download(new, period="1y", auto_adjust=True, progress=False)

    raw = await asyncio.to_thread(_download)

    if raw.empty:
        for t in new:
            _hist_cache[t] = pd.Series(dtype=float)
            _price_cache[t] = Decimal("100")
        return

    # raw.columns is a MultiIndex (Price, Ticker) for multiple tickers
    # accessing raw["Close"] gives a DataFrame with ticker columns
    if len(new) == 1:
        closes_df = raw[["Close"]].rename(columns={"Close": new[0]})
    else:
        closes_df = raw["Close"]

    for ticker in new:
        if ticker not in closes_df.columns:
            _hist_cache[ticker] = pd.Series(dtype=float)
            _price_cache[ticker] = Decimal("100")
            continue

        series = closes_df[ticker].dropna()
        # Normalize timezone-aware timestamps to plain-date index
        series = pd.Series(
            series.values,
            index=pd.to_datetime(series.index).normalize().tz_localize(None),
        )
        _hist_cache[ticker] = series
        _price_cache[ticker] = Decimal(str(round(float(series.iloc[-1]), 4))) if len(series) else Decimal("100")


# ── Connector ─────────────────────────────────────────────────────────────────

class YFinanceConnector(BankConnector):
    connector_type = "Yahoo Finance"

    def __init__(self, bank_name: str) -> None:
        super().__init__(bank_name)
        if bank_name not in _BANKS:
            raise ValueError(f"Unknown bank: {bank_name}. Choose from {list(_BANKS)}")
        self._cfg = _BANKS[bank_name]

    async def get_accounts(self) -> list[BankAccount]:
        return [
            BankAccount(
                id=a["id"],
                bank_name=self.bank_name,
                account_name=a["name"],
                account_type=a["type"],
            )
            for a in self._cfg["accounts"]
        ]

    async def get_positions(self, account_id: str) -> list[Position]:
        raw_holdings = _HOLDINGS.get(account_id, [])
        yf_tickers = [t for t, _, _ in raw_holdings if t in _INSTRUMENTS]
        # Also fetch underlyings for any FCNs in this account
        fcn_underlyings = [
            _FCN_REGISTRY[k].underlying_ticker
            for k, _, _ in raw_holdings
            if k in _FCN_REGISTRY
        ]
        await _ensure_tickers(yf_tickers + fcn_underlyings)

        today = date.today()
        account_name = next(
            (a["name"] for a in self._cfg["accounts"] if a["id"] == account_id), ""
        )
        positions = []
        for key, qty, avg_cost in raw_holdings:
            if key in _FCN_REGISTRY:
                fcn = _FCN_REGISTRY[key]
                underlying_price = _price_cache.get(fcn.underlying_ticker, fcn.strike_price)
                current_price = fcn.mark_to_market(underlying_price, today)
                instrument = fcn
            else:
                instrument = _INSTRUMENTS[key]
                current_price = _price_cache.get(key, Decimal("100"))

            positions.append(Position(
                instrument=instrument,
                quantity=Decimal(str(qty)),
                avg_cost=Decimal(str(avg_cost)),
                current_price=current_price,
                bank_name=self.bank_name,
                account_id=account_id,
                account_name=account_name,
            ))
        return positions

    async def get_historical_values(
        self, account_id: str, from_date: date, to_date: date
    ) -> list[PortfolioSnapshot]:
        raw_holdings = _HOLDINGS.get(account_id, [])
        yf_tickers = [t for t, _, _ in raw_holdings if t in _INSTRUMENTS]
        fcn_underlyings = [
            _FCN_REGISTRY[k].underlying_ticker
            for k, _, _ in raw_holdings
            if k in _FCN_REGISTRY
        ]
        await _ensure_tickers(yf_tickers + fcn_underlyings)

        date_index = pd.date_range(from_date, to_date, freq="D")
        portfolio_series = pd.Series(0.0, index=date_index)

        for key, qty, avg_cost in raw_holdings:
            if key in _FCN_REGISTRY:
                fcn = _FCN_REGISTRY[key]
                ul_series = _hist_cache.get(fcn.underlying_ticker)
                if ul_series is not None and len(ul_series) > 0:
                    reindexed = ul_series.reindex(date_index, method="ffill").bfill()
                    for ts in date_index:
                        ul_price = Decimal(str(round(float(reindexed.loc[ts]), 4)))
                        fcn_price = fcn.mark_to_market(ul_price, ts.date())
                        portfolio_series.loc[ts] += float(fcn_price) * float(qty)
                else:
                    portfolio_series += float(qty) * float(fcn.notional)
                continue

            series = _hist_cache.get(key)
            if series is None or len(series) == 0:
                continue

            reindexed = series.reindex(date_index, method="ffill").bfill()
            portfolio_series += reindexed * float(qty)

        snapshots = [
            PortfolioSnapshot(
                date=ts.date(),
                total_value=Decimal(str(round(val, 2))),
                bank_name=self.bank_name,
            )
            for ts, val in portfolio_series.items()
            if pd.notna(val) and val > 0
        ]
        return snapshots
