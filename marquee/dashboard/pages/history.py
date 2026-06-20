from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import Callable, Optional
from nicegui import ui
from marquee.models import PortfolioSnapshot
from marquee.dashboard.theme import COLORS
from marquee.dashboard.components.charts import portfolio_history_line
from marquee.dashboard.components.sidebar import sidebar

_RANGES = {"1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365, "All": None}


def history_page(
    snapshots: list[PortfolioSnapshot],
    synced_at: Optional[datetime] = None,
    on_sync: Optional[Callable] = None,
) -> None:
    with ui.element("div").classes("app-shell"):
        sidebar("history", synced_at=synced_at, on_sync=on_sync)

        with ui.element("div").classes("content-area"):

            # ── Page header ────────────────────────────────────
            with ui.element("div").style("margin-bottom:36px"):
                ui.label("History").classes("page-title")
                ui.label("Portfolio net value over time").classes("page-subtitle")

            selected_range = {"value": "1Y"}
            plot_ref = {"plot": None}
            btn_refs: dict = {}

            def filtered_snapshots(key: str):
                days = _RANGES.get(key)
                if days is None or not snapshots:
                    return snapshots
                cutoff = date.today() - timedelta(days=days)
                return [s for s in snapshots if s.date >= cutoff]

            def build_fig(key: str):
                snaps = filtered_snapshots(key)
                return portfolio_history_line(
                    dates=[s.date for s in snaps],
                    values=[float(s.total_value) for s in snaps],
                )

            def set_range(lbl: str):
                selected_range["value"] = lbl
                for k, b in btn_refs.items():
                    active = k == lbl
                    b.style(
                        f"font-size:11px; font-weight:{'600' if active else '400'}; "
                        f"border-radius:0; border-right:1px solid {COLORS['border']}; "
                        f"background:{COLORS['btn_active_bg'] if active else COLORS['bg']} !important; "
                        f"color:{COLORS['btn_active_text'] if active else COLORS['text_secondary']} !important; "
                        f"min-height:0; height:30px; padding:0 14px; letter-spacing:0.04em"
                    )
                plot_ref["plot"].figure = build_fig(lbl)
                plot_ref["plot"].update()

            # ── Chart card ─────────────────────────────────────
            with ui.element("div").style(
                f"border:1px solid {COLORS['border']}; padding:28px; margin-bottom:1px"
            ):
                with ui.element("div").style(
                    "display:flex; align-items:flex-start; "
                    "justify-content:space-between; margin-bottom:24px"
                ):
                    with ui.element("div"):
                        ui.label("TOTAL PORTFOLIO VALUE").style(
                            f"font-size:10px; font-weight:700; letter-spacing:0.1em; "
                            f"color:{COLORS['text_muted']}"
                        )
                        if snapshots:
                            ui.label(f"USD {float(snapshots[-1].total_value):,.0f}").style(
                                f"font-size:28px; font-weight:300; color:{COLORS['text_primary']}; "
                                f"letter-spacing:-0.8px; margin-top:6px; font-variant-numeric:tabular-nums"
                            )

                    with ui.element("div").style(
                        f"display:flex; border:1px solid {COLORS['border']}; overflow:hidden; align-self:flex-start"
                    ):
                        for i, label in enumerate(_RANGES):
                            is_active = label == selected_range["value"]
                            is_last = i == len(_RANGES) - 1
                            btn = (
                                ui.button(label)
                                .props("unelevated flat dense")
                                .style(
                                    f"font-size:11px; font-weight:{'600' if is_active else '400'}; "
                                    f"border-radius:0; "
                                    f"border-right:{'none' if is_last else '1px solid ' + COLORS['border']}; "
                                    f"background:{COLORS['btn_active_bg'] if is_active else COLORS['bg']} !important; "
                                    f"color:{COLORS['btn_active_text'] if is_active else COLORS['text_secondary']} !important; "
                                    f"min-height:0; height:30px; padding:0 14px; letter-spacing:0.04em"
                                )
                                .on("click", lambda lbl=label: set_range(lbl))
                            )
                            btn_refs[label] = btn

                plot = ui.plotly(build_fig(selected_range["value"])).style("height:320px; width:100%")
                plot_ref["plot"] = plot

            # ── Stats grid ─────────────────────────────────────
            if snapshots:
                first, last = snapshots[0], snapshots[-1]
                delta = float(last.total_value) - float(first.total_value)
                pct = (delta / float(first.total_value) * 100) if first.total_value else 0
                pos = delta >= 0
                sign = "+" if pos else ""

                with ui.element("div").style(
                    f"display:grid; grid-template-columns:repeat(4,1fr); gap:1px; "
                    f"border:1px solid {COLORS['border']}"
                ):
                    for lbl, val, is_pos in [
                        ("Starting Value", f"USD {float(first.total_value):,.0f}", None),
                        ("Current Value",  f"USD {float(last.total_value):,.0f}",  None),
                        ("Total Change",   f"{sign}USD {delta:,.0f}",              pos),
                        ("Total Return",   f"{sign}{pct:.2f}%",                    pos),
                    ]:
                        with ui.element("div").style(
                            f"padding:20px 24px; background:{COLORS['bg']}"
                        ):
                            ui.label(lbl).style(
                                f"font-size:10px; font-weight:700; letter-spacing:0.1em; "
                                f"text-transform:uppercase; color:{COLORS['text_muted']}; display:block"
                            )
                            color = (
                                COLORS["positive"] if is_pos
                                else COLORS["negative"] if is_pos is False
                                else COLORS["text_primary"]
                            )
                            ui.label(val).style(
                                f"font-size:22px; font-weight:300; color:{color}; margin-top:8px; "
                                f"display:block; letter-spacing:-0.4px; font-variant-numeric:tabular-nums"
                            )
