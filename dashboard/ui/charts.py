"""Plotly chart builders. Every chart takes already-computed data and a theme.

No analytics happen here - only presentation. Numbers come from the project's
own calculations (src/ modules and the groupby tables in app.py).
"""

import plotly.graph_objects as go
import plotly.express as px

from .theme import tokens

FONT = "Inter, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def churn_scale(t: dict) -> list:
    """Cool -> hot gradient used wherever colour encodes churn intensity."""
    return [[0.0, t["accent-3"]], [0.45, t["accent-2"]], [0.75, t["accent"]], [1.0, t["pink"]]]


def apply_theme(fig: go.Figure, name: str, height: int = 360, legend: bool = False) -> go.Figure:
    """Shared look: transparent background, subtle axes, themed tooltip."""
    t = tokens(name)
    grid = _rgba(t["subtle"], 0.18)
    fig.update_layout(
        template="plotly_dark" if name == "dark" else "plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=t["muted"], size=12),
        height=height,
        margin=dict(l=8, r=8, t=18, b=8),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5,
                    font=dict(color=t["muted"], size=12), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=t["card-solid"], bordercolor=_rgba(t["accent"], 0.6),
                        font=dict(family=FONT, size=13, color=t["text"])),
        transition=dict(duration=450, easing="cubic-in-out"),
        bargap=0.38,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showline=True, linecolor=grid,
                     tickfont=dict(color=t["muted"], size=12), title_font=dict(color=t["subtle"], size=12),
                     automargin=True, ticks="")
    fig.update_yaxes(showgrid=True, gridcolor=grid, gridwidth=1, griddash="dot", zeroline=False,
                     showline=False, tickfont=dict(color=t["subtle"], size=11),
                     title_font=dict(color=t["subtle"], size=12), automargin=True, ticks="")
    return fig


def churn_bar(data, x: str, x_label: str, name: str, category_axis: bool = True,
              y: str = "ChurnRate", y_label: str = "Churn Rate (%)", height: int = 360) -> go.Figure:
    """Churn-rate bars, coloured by intensity, with customer count in the tooltip."""
    t = tokens(name)
    has_counts = "CustomerCount" in data.columns
    fig = go.Figure(go.Bar(
        x=data[x].astype(str) if category_axis else data[x],
        y=data[y],
        text=data[y],
        texttemplate="%{text:.2f}%",
        textposition="outside",
        textfont=dict(color=t["text"], size=12, family=FONT),
        cliponaxis=False,
        marker=dict(color=data[y], colorscale=churn_scale(t), cmin=0,
                    cmax=max(float(data[y].max()), 1.0) * 1.15,
                    cornerradius=10, line=dict(width=0)),
        customdata=data[["CustomerCount"]] if has_counts else None,
        hovertemplate=(
            f"<b>%{{x}}</b><br>{y_label}: <b>%{{y:.2f}}%</b>"
            + ("<br>Customers: <b>%{customdata[0]:,}</b>" if has_counts else "")
            + "<extra></extra>"
        ),
    ))
    apply_theme(fig, name, height)
    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label,
                      yaxis_range=[0, float(data[y].max()) * 1.25])
    fig.update_xaxes(type="category")
    return fig


def count_bar(data, x: str, y: str, x_label: str, name: str, colors: dict,
              order: list | None = None, height: int = 380) -> go.Figure:
    """Customer-count bars with a fixed semantic colour per category."""
    t = tokens(name)
    d = data.set_index(x)
    cats = [c for c in (order or list(d.index)) if c in d.index]
    values = [int(d.loc[c, y]) for c in cats]
    total = sum(values) or 1
    fig = go.Figure(go.Bar(
        x=cats, y=values, text=values,
        texttemplate="%{text:,}", textposition="outside",
        textfont=dict(color=t["text"], size=12, family=FONT), cliponaxis=False,
        marker=dict(color=[colors.get(c, t["accent"]) for c in cats], cornerradius=10, line=dict(width=0)),
        customdata=[[v / total * 100] for v in values],
        hovertemplate="<b>%{x}</b><br>Customers: <b>%{y:,}</b><br>Share: <b>%{customdata[0]:.1f}%</b><extra></extra>",
    ))
    apply_theme(fig, name, height)
    fig.update_layout(xaxis_title=x_label, yaxis_title="Number of Customers",
                      yaxis_range=[0, max(values) * 1.2])
    fig.update_xaxes(type="category")
    return fig


def heatmap(pivot, name: str, height: int = 340) -> go.Figure:
    """Churn-rate heatmap (Product Category x Engagement Status)."""
    t = tokens(name)
    fig = px.imshow(
        pivot, text_auto=".2f", aspect="auto",
        labels={"x": "Engagement Status", "y": "Product Category", "color": "Churn Rate (%)"},
    )
    fig.update_traces(
        colorscale=churn_scale(t), xgap=5, ygap=5,
        texttemplate="%{z:.2f}%", textfont=dict(size=16, family=FONT, color="#FFFFFF"),
        hovertemplate="<b>%{y}</b> · %{x}<br>Churn rate: <b>%{z:.2f}%</b><extra></extra>",
        colorbar=dict(title=dict(text="Churn %", font=dict(color=t["muted"], size=11)),
                      thickness=10, len=0.85, outlinewidth=0, ticksuffix="%",
                      tickfont=dict(color=t["muted"], size=11)),
    )
    apply_theme(fig, name, height)
    fig.update_xaxes(showline=False, side="bottom", title_text="Engagement Status")
    fig.update_yaxes(showgrid=False, title_text="Product Category")
    return fig


def donut(retained: int, churned: int, churn_rate: float, name: str, height: int = 340) -> go.Figure:
    """Retained vs churned customers with the churn rate in the centre."""
    t = tokens(name)
    fig = go.Figure(go.Pie(
        labels=["Retained", "Churned"], values=[retained, churned], hole=0.74, sort=False,
        marker=dict(colors=[t["accent-3"], t["pink"]], line=dict(color=t["card-solid"], width=3)),
        textinfo="none", direction="clockwise",
        hovertemplate="<b>%{label}</b><br>Customers: <b>%{value:,}</b><br>Share: <b>%{percent}</b><extra></extra>",
    ))
    apply_theme(fig, name, height, legend=True)
    fig.update_layout(
        margin=dict(l=8, r=8, t=8, b=30),
        annotations=[
            dict(text=f"<b>{churn_rate:.2f}%</b>", x=0.5, y=0.54, showarrow=False,
                 font=dict(size=30, color=t["text"], family=FONT)),
            dict(text="HISTORICAL CHURN", x=0.5, y=0.42, showarrow=False,
                 font=dict(size=11, color=t["subtle"], family=FONT)),
        ],
    )
    return fig
