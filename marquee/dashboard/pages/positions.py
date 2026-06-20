from __future__ import annotations
from datetime import datetime
from typing import Callable, Optional
from nicegui import ui
from marquee.models import Portfolio
from marquee.dashboard.theme import COLORS
from marquee.dashboard.components.sidebar import sidebar


def _filter_label(text: str) -> None:
    ui.label(text).style(
        f"font-size:10px; font-weight:700; letter-spacing:0.1em; "
        f"text-transform:uppercase; color:{COLORS['text_muted']}; margin-bottom:6px; display:block"
    )


def positions_page(
    portfolio: Portfolio,
    synced_at: Optional[datetime] = None,
    on_sync: Optional[Callable] = None,
) -> None:
    with ui.element("div").classes("app-shell"):
        sidebar("positions", synced_at=synced_at, on_sync=on_sync)

        with ui.element("div").classes("content-area"):

            # ── Page header ────────────────────────────────────
            with ui.element("div").style("margin-bottom:36px"):
                ui.label("Positions").classes("page-title")
                ui.label(
                    f"{len(portfolio.positions)} holdings · 2 banks · 4 accounts"
                ).classes("page-subtitle")

            # ── Filters ────────────────────────────────────────
            filter_bank = {"value": "All"}
            filter_type = {"value": "All"}

            banks = ["All"] + sorted({p.bank_name for p in portfolio.positions})
            types = ["All"] + sorted({p.instrument.instrument_type.value for p in portfolio.positions})

            def get_filtered():
                return [
                    p for p in portfolio.positions
                    if (filter_bank["value"] == "All" or p.bank_name == filter_bank["value"])
                    and (filter_type["value"] == "All" or p.instrument.instrument_type.value == filter_type["value"])
                ]

            columns = [
                {"name": "name",     "label": "Name",         "field": "name",     "align": "left",  "sortable": True},
                {"name": "type",     "label": "Type",         "field": "type",     "align": "left"},
                {"name": "bank",     "label": "Bank",         "field": "bank",     "align": "left"},
                {"name": "account",  "label": "Account",      "field": "account",  "align": "left"},
                {"name": "qty",      "label": "Qty",          "field": "qty",      "align": "right", "sortable": True},
                {"name": "avg_cost", "label": "Avg Cost",     "field": "avg_cost", "align": "right"},
                {"name": "price",    "label": "Price",        "field": "price",    "align": "right"},
                {"name": "value",    "label": "Market Value", "field": "value",    "align": "right", "sortable": True},
                {"name": "pnl",      "label": "P&L",          "field": "pnl",      "align": "right", "sortable": True},
                {"name": "pnl_pct",  "label": "P&L %",        "field": "pnl_pct",  "align": "right", "sortable": True},
            ]

            table_ref = {"table": None}

            def build_rows():
                rows = []
                for pos in get_filtered():
                    pnl_val = float(pos.unrealized_pnl)
                    sign = "+" if pnl_val >= 0 else ""
                    rows.append({
                        "name":     pos.instrument.display_name,
                        "type":     pos.instrument.instrument_type.value,
                        "bank":     pos.bank_name,
                        "account":  pos.account_name,
                        "qty":      f"{float(pos.quantity):,.4g}",
                        "avg_cost": f"{float(pos.avg_cost):,.2f}",
                        "price":    f"{float(pos.current_price):,.2f}",
                        "value":    f"USD {float(pos.market_value):,.0f}",
                        "pnl":      f"{sign}{pnl_val:,.0f}",
                        "pnl_pct":  f"{sign}{float(pos.pnl_pct):.2f}%",
                    })
                return rows

            with ui.element("div").style("display:flex; gap:24px; margin-bottom:24px"):
                with ui.element("div"):
                    _filter_label("Bank")
                    bank_select = ui.select(options=banks, value="All").style("min-width:180px")
                with ui.element("div"):
                    _filter_label("Instrument Type")
                    type_select = ui.select(options=types, value="All").style("min-width:180px")

            table = ui.table(columns=columns, rows=build_rows()).style("width:100%")
            table_ref["table"] = table

            def on_bank_change(e):
                filter_bank["value"] = e.value
                table_ref["table"].rows = build_rows()
                table_ref["table"].update()

            def on_type_change(e):
                filter_type["value"] = e.value
                table_ref["table"].rows = build_rows()
                table_ref["table"].update()

            bank_select.on_value_change(on_bank_change)
            type_select.on_value_change(on_type_change)
