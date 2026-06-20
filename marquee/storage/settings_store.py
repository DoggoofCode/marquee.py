from __future__ import annotations
import json
from pathlib import Path

_SETTINGS_FILE = Path(__file__).parent.parent.parent / "data" / "settings.json"


class SettingsStore:
    def __init__(self, path: Path = _SETTINGS_FILE):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load_raw(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text())
        except Exception:
            return {}

    def connector_states(self) -> dict[str, bool]:
        """Returns {bank_name: enabled}. Absent keys default to True."""
        return self._load_raw().get("connectors", {})

    def is_enabled(self, bank_name: str) -> bool:
        return self.connector_states().get(bank_name, True)

    def set_connector(self, bank_name: str, enabled: bool) -> None:
        raw = self._load_raw()
        raw.setdefault("connectors", {})[bank_name] = enabled
        self.path.write_text(json.dumps(raw, indent=2))
