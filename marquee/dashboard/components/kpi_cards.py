from nicegui import ui
from marquee.dashboard.theme import COLORS


def kpi_card(label: str, value: str, delta: str = "", positive: bool | None = None) -> None:
    with ui.element("div").classes("kpi-card"):
        ui.label(label).style(
            f"font-size:10px; font-weight:700; letter-spacing:0.1em; "
            f"text-transform:uppercase; color:{COLORS['text_muted']}; "
            f"margin-bottom:10px; display:block"
        )
        ui.label(value).style(
            f"font-size:26px; font-weight:300; color:{COLORS['text_primary']}; "
            f"letter-spacing:-0.6px; line-height:1.1; "
            f"font-variant-numeric:tabular-nums; display:block"
        )
        if delta:
            color = (
                COLORS["positive"] if positive
                else COLORS["negative"] if positive is False
                else COLORS["text_secondary"]
            )
            ui.label(delta).style(
                f"font-size:12px; font-weight:500; color:{color}; margin-top:6px; "
                f"display:block; font-variant-numeric:tabular-nums"
            )
