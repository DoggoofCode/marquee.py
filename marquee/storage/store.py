from __future__ import annotations
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

import numpy as np

from marquee.models import Portfolio, PortfolioSnapshot

_DATA_DIR = Path(__file__).parent.parent.parent / "data"
_PORTFOLIO_FILE = _DATA_DIR / "portfolio.json"
_HISTORY_FILE = _DATA_DIR / "history.npz"


class DataStore:
    def __init__(
        self,
        portfolio_path: Path = _PORTFOLIO_FILE,
        history_path: Path = _HISTORY_FILE,
    ):
        self.portfolio_path = portfolio_path
        self.history_path = history_path
        portfolio_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, portfolio: Portfolio, snapshots: list[PortfolioSnapshot]) -> None:
        # Positions → compact JSON (no snapshots)
        payload = {
            "synced_at": datetime.utcnow().isoformat(),
            "portfolio": portfolio.model_dump(mode="json"),
        }
        self.portfolio_path.write_text(json.dumps(payload, indent=2))

        # History → compressed NumPy archive
        dates = np.array([s.date.isoformat() for s in snapshots], dtype="U10")
        values = np.array([float(s.total_value) for s in snapshots], dtype=np.float64)
        np.savez_compressed(self.history_path, dates=dates, values=values)

    def load(self) -> Optional[tuple[Portfolio, list[PortfolioSnapshot], datetime]]:
        if not self.portfolio_path.exists() or not self.history_path.exists():
            return None
        try:
            raw = json.loads(self.portfolio_path.read_text())
            portfolio = Portfolio.model_validate(raw["portfolio"])
            synced_at = datetime.fromisoformat(raw["synced_at"])

            arch = np.load(self.history_path)
            snapshots = [
                PortfolioSnapshot(
                    date=date.fromisoformat(str(d)),
                    total_value=Decimal(str(round(float(v), 2))),
                    bank_name="all",
                )
                for d, v in zip(arch["dates"], arch["values"])
            ]
            return portfolio, snapshots, synced_at
        except Exception:
            return None

    @property
    def exists(self) -> bool:
        return self.portfolio_path.exists() and self.history_path.exists()
