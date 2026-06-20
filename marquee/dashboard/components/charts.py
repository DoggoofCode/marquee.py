"""Plotly chart builders — all colours and fonts from theme.py."""
from __future__ import annotations
import plotly.graph_objects as go
from marquee.dashboard.theme import COLORS, FONTS, CHART_PALETTE


def allocation_donut(labels: list[str], values: list[float], title: str = "") -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.65,
            marker=dict(
                colors=CHART_PALETTE[:len(labels)],
                line=dict(color=COLORS["bg"], width=3),
            ),
            textinfo="percent",
            textfont=dict(size=11, family=FONTS["sans"], color=COLORS["bg"]),
            hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>",
            direction="clockwise",
        )
    )
    fig.update_layout(
        margin=dict(t=8, b=8, l=8, r=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            font=dict(size=12, color=COLORS["text_primary"], family=FONTS["sans"]),
            bgcolor="rgba(0,0,0,0)",
            itemclick=False,
            itemdoubleclick=False,
        ),
        showlegend=True,
    )
    return fig


def portfolio_history_line(
    dates: list, values: list[float], label: str = "Portfolio Value"
) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=dates,
            y=values,
            mode="lines",
            name=label,
            line=dict(color=COLORS["accent"], width=1.5),
            fill="tozeroy",
            fillcolor=COLORS["accent_fill"],
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>%{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        margin=dict(t=8, b=8, l=0, r=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor=COLORS["border"],
            linewidth=1,
            tickfont=dict(size=10, color=COLORS["text_muted"], family=FONTS["sans"]),
            tickformat="%b %Y",
            ticks="outside",
            ticklen=4,
            tickcolor=COLORS["border"],
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS["border_light"],
            gridwidth=1,
            tickfont=dict(size=10, color=COLORS["text_muted"], family=FONTS["sans"]),
            tickformat=",.0f",
            zeroline=False,
            showline=False,
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=COLORS["text_primary"],
            font=dict(size=12, color=COLORS["btn_active_text"], family=FONTS["sans"]),
            bordercolor=COLORS["text_primary"],
        ),
    )
    return fig
