from __future__ import annotations
from datetime import datetime
from typing import Callable, Optional
from nicegui import ui
from marquee.models import Portfolio
from marquee.analytics import allocation_by_type, allocation_by_bank, top_movers
from marquee.dashboard.theme import COLORS
from marquee.dashboard.components.kpi_cards import kpi_card
from marquee.dashboard.components.charts import allocation_donut
from marquee.dashboard.components.sidebar import sidebar


def _section_label(text: str) -> None:
    ui.label(text).style(
        f"font-size:10px; font-weight:700; letter-spacing:0.1em; "
        f"text-transform:uppercase; color:{COLORS['text_muted']}; "
        f"margin-bottom:16px; display:block"
    )


def overview_page(
    portfolio: Portfolio,
    ytd: str,
    synced_at: Optional[datetime] = None,
    on_sync: Optional[Callable] = None,
) -> None:
    with ui.element("div").classes("app-shell"):
        sidebar("overview", synced_at=synced_at, on_sync=on_sync)

        with ui.element("div").classes("content-area"):

            # ── Page header ────────────────────────────────────
            with ui.element("div").style("margin-bottom:36px"):
                ui.label("Overview").classes("page-title")
                ui.label("Aggregated across all connected banks").classes("page-subtitle")

            # ── KPI row ────────────────────────────────────────
            total_val = float(portfolio.total_value)
            total_pnl = float(portfolio.total_pnl)
            pnl_pct = float(portfolio.total_pnl_pct)
            pnl_positive = total_pnl >= 0
            ytd_positive = not ytd.startswith("-")

            with ui.element("div").style(
                "display:grid; grid-template-columns:repeat(4,1fr); gap:1px; "
                f"margin-bottom:40px; border:1px solid {COLORS['border']}"
            ):
                for args in [
                    ("Total Value", f"USD {total_val:,.0f}", None, None),
                    ("Unrealised P&L",
                     f"{'+'if pnl_positive else ''}{total_pnl:,.0f}",
                     f"{'+'if pnl_positive else ''}{pnl_pct:.2f}%", pnl_positive),
                    ("YTD Return", ytd, None, ytd_positive),
                    ("Positions", str(len(portfolio.positions)), None, None),
                ]:
                    kpi_card(*args)

            # ── Allocation charts ──────────────────────────────
            _section_label("Allocation")
            with ui.element("div").style(
                f"display:grid; grid-template-columns:1fr 1fr; gap:1px; "
                f"margin-bottom:40px; border:1px solid {COLORS['border']}"
            ):
                with ui.element("div").style(f"padding:24px; background:{COLORS['bg']}"):
                    ui.label("By Instrument Type").style(
                        f"font-size:10px; font-weight:700; letter-spacing:0.08em; "
                        f"text-transform:uppercase; color:{COLORS['text_muted']}; margin-bottom:8px"
                    )
                    by_type = allocation_by_type(portfolio)
                    ui.plotly(allocation_donut(
                        labels=list(by_type.keys()),
                        values=[float(v) for v in by_type.values()],
                    )).style("height:220px")

                with ui.element("div").style(
                    f"padding:24px; background:{COLORS['bg']}; "
                    f"border-left:1px solid {COLORS['border']}"
                ):
                    ui.label("By Bank").style(
                        f"font-size:10px; font-weight:700; letter-spacing:0.08em; "
                        f"text-transform:uppercase; color:{COLORS['text_muted']}; margin-bottom:8px"
                    )
                    by_bank = allocation_by_bank(portfolio)
                    ui.plotly(allocation_donut(
                        labels=list(by_bank.keys()),
                        values=[float(v) for v in by_bank.values()],
                    )).style("height:220px")

            # ── Top movers ─────────────────────────────────────
            _section_label("Top Positions by P&L")
            movers = top_movers(portfolio, n=8)
            columns = [
                {"name": "name",    "label": "Name",         "field": "name",    "align": "left"},
                {"name": "type",    "label": "Type",         "field": "type",    "align": "left"},
                {"name": "bank",    "label": "Bank",         "field": "bank",    "align": "left"},
                {"name": "value",   "label": "Market Value", "field": "value",   "align": "right"},
                {"name": "pnl",     "label": "P&L",          "field": "pnl",     "align": "right"},
                {"name": "pnl_pct", "label": "P&L %",        "field": "pnl_pct", "align": "right"},
            ]
            rows = []
            for pos in movers:
                pnl_val = float(pos.unrealized_pnl)
                sign = "+" if pnl_val >= 0 else ""
                rows.append({
                    "name":    pos.instrument.display_name,
                    "type":    pos.instrument.instrument_type.value,
                    "bank":    pos.bank_name,
                    "value":   f"USD {float(pos.market_value):,.0f}",
                    "pnl":     f"{sign}{pnl_val:,.0f}",
                    "pnl_pct": f"{sign}{float(pos.pnl_pct):.2f}%",
                })
            ui.table(columns=columns, rows=rows).style("width:100%")
