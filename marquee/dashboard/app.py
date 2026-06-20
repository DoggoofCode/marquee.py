"""NiceGUI application entrypoint."""
from __future__ import annotations
from datetime import date, datetime, timedelta
from nicegui import ui

from marquee.config import settings
from marquee.connectors import ConnectorRegistry, YFinanceConnector
from marquee.aggregator import PortfolioAggregator
from marquee.analytics import ytd_return
from marquee.storage import DataStore, SettingsStore
from marquee.dashboard import theme
from marquee.dashboard.pages.overview import overview_page
from marquee.dashboard.pages.positions import positions_page
from marquee.dashboard.pages.history import history_page
from marquee.dashboard.pages.settings import settings_page

# All registered connectors — add new banks here
_ALL_CONNECTORS = [
    YFinanceConnector("Meridian Wealth"),
    YFinanceConnector("Atlas Capital"),
]

_store = DataStore()
_settings_store = SettingsStore()


def _format_ytd(snapshots) -> str:
    val = ytd_return(snapshots)
    return f"{'+' if val >= 0 else ''}{float(val):.2f}%"


async def _sync_now():
    states = _settings_store.connector_states()
    registry = ConnectorRegistry()
    for c in _ALL_CONNECTORS:
        if states.get(c.bank_name, True):
            registry.register(c)

    agg = PortfolioAggregator(registry)
    portfolio = await agg.get_portfolio()
    to_date = date.today()
    snapshots = await agg.get_historical_snapshots(to_date - timedelta(days=365), to_date)
    _store.save(portfolio, snapshots)
    return portfolio, snapshots, _format_ytd(snapshots), datetime.utcnow()


async def _load_data():
    result = _store.load()
    if result is not None:
        portfolio, snapshots, synced_at = result
        return portfolio, snapshots, _format_ytd(snapshots), synced_at
    return await _sync_now()


@ui.page("/")
async def root():
    ui.navigate.to("/overview")


@ui.page("/overview")
async def page_overview():
    theme.apply()
    portfolio, _, ytd_str, synced_at = await _load_data()

    async def on_sync():
        await _sync_now()
        ui.navigate.to("/overview")

    overview_page(portfolio, ytd_str, synced_at=synced_at, on_sync=on_sync)


@ui.page("/positions")
async def page_positions():
    theme.apply()
    portfolio, _, _, synced_at = await _load_data()

    async def on_sync():
        await _sync_now()
        ui.navigate.to("/positions")

    positions_page(portfolio, synced_at=synced_at, on_sync=on_sync)


@ui.page("/history")
async def page_history():
    theme.apply()
    _, snapshots, _, synced_at = await _load_data()

    async def on_sync():
        await _sync_now()
        ui.navigate.to("/history")

    history_page(snapshots, synced_at=synced_at, on_sync=on_sync)


@ui.page("/settings")
async def page_settings():
    theme.apply()
    _, _, _, synced_at = await _load_data()
    states = _settings_store.connector_states()

    connector_data = [
        {
            "name": c.bank_name,
            "type": c.connector_type,
            "enabled": states.get(c.bank_name, True),
            "accounts": [
                a["name"]
                for a in c._cfg["accounts"]
            ],
        }
        for c in _ALL_CONNECTORS
    ]

    def on_toggle(name: str, enabled: bool) -> None:
        _settings_store.set_connector(name, enabled)

    async def on_sync():
        await _sync_now()
        ui.navigate.to("/settings")

    settings_page(connector_data, on_toggle, synced_at=synced_at, on_sync=on_sync)


def main() -> None:
    ui.run(
        host=settings.host,
        port=settings.port,
        title=settings.app_title,
        reload=settings.reload,
        favicon="📈",
        dark=False,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
