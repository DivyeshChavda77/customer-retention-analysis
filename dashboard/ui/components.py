"""Reusable HTML/Streamlit components: icons, KPI cards, headers, callouts, cards."""

import math
import re
from contextlib import contextmanager
from html import escape
from urllib.parse import quote

import streamlit as st

# --------------------------------------------------------------------------
# Icons (Lucide-style paths, rendered through CSS masks so they inherit colour)
# --------------------------------------------------------------------------
ICONS = {
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "refresh": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
    "package": '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    "card": '<rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/>',
    "activity": '<path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "trend-down": '<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/>',
    "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "euro": '<path d="M4 10h12"/><path d="M4 14h9"/><path d="M19 6a7.7 7.7 0 0 0-5.2-2A7.9 7.9 0 0 0 6 12c0 4.4 3.5 8 7.8 8 2 0 3.8-.8 5.2-2"/>',
    "bars": '<line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/>',
    "layout": '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
    "pie": '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/>',
    "bulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
}

_ICON_BASE_CSS = (
    ".ic{display:inline-block;flex:none;width:1.15em;height:1.15em;background-color:currentColor;"
    "-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}"
)


def icon_css() -> str:
    """CSS defining every .ic-<name> class (inlined once per page render)."""
    rules = [_ICON_BASE_CSS]
    for name, body in ICONS.items():
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
            'stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f"{body}</svg>"
        )
        rules.append(f'.ic-{name}{{--ic:url("data:image/svg+xml,{quote(svg)}")}}')
    return "".join(rules)


def icon(name: str) -> str:
    return f'<i class="ic ic-{name}" aria-hidden="true"></i>'


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def render(html: str) -> None:
    """Render raw HTML. Newlines are stripped so Markdown never splits the block."""
    st.markdown(re.sub(r"\n\s*", "", html), unsafe_allow_html=True)


def plotly(fig, key: str | None = None) -> None:
    """Render a Plotly figure with our own theme (not Streamlit's) at full width."""
    config = {"displaylogo": False, "displayModeBar": "hover", "responsive": True}
    try:
        st.plotly_chart(fig, width="stretch", theme=None, config=config, key=key)
    except TypeError:  # older Streamlit versions
        st.plotly_chart(fig, use_container_width=True, theme=None, config=config, key=key)


def dataframe(data, **kwargs) -> None:
    """st.dataframe at full width (works across Streamlit versions)."""
    try:
        st.dataframe(data, width="stretch", **kwargs)
    except TypeError:  # older Streamlit versions
        st.dataframe(data, use_container_width=True, **kwargs)


# --------------------------------------------------------------------------
# Animated number (pure CSS - no JavaScript)
# --------------------------------------------------------------------------
def animated_number(value: float, decimals: int = 0, prefix: str = "", suffix: str = "") -> str:
    """Count-up number driven by CSS @property counters.

    The final value is passed in as integer groups (thousands / remainder /
    decimals); browsers without @property support simply show the final value.
    """
    if value is None or not math.isfinite(value):
        # e.g. a ratio that is undefined because the filter removed one of the groups
        return ('<span class="num"><span class="sr">Not available for this selection</span>'
                '<span class="num-fix" aria-hidden="true">—</span></span>')
    final = f"{prefix}{value:,.{decimals}f}{suffix}"
    scaled = int(round(abs(value) * 10**decimals))
    int_part, dec_part = divmod(scaled, 10**decimals) if decimals else (scaled, 0)
    if int_part >= 1000:
        a, b = divmod(int_part, 1000)
        grouping = "g"
    else:
        a, b, grouping = int_part, 0, "p"
    return (
        f'<span class="num"><span class="sr">{escape(final)}</span>'
        f'<span class="num-fix" aria-hidden="true">{escape(prefix)}</span>'
        f'<span class="num-v {grouping} d{decimals}" aria-hidden="true" '
        f'style="--ta:{a};--tb:{b};--td:{dec_part}"></span>'
        f'<span class="num-fix" aria-hidden="true">{escape(suffix)}</span></span>'
    )


def delta_chip(current: float, baseline: float, unit: str = "", decimals: int = 2,
               good_when: str | None = None, label: str = "vs all customers") -> str:
    """Trend chip comparing a filtered value with the full-portfolio value.

    Only real, computed differences are shown; nothing is invented.
    """
    if not (math.isfinite(current) and math.isfinite(baseline)):
        return ""
    diff = current - baseline
    if abs(diff) < 0.5 * 10**-decimals:
        return f'<span class="chip flat">● In line {escape(label)}</span>'
    arrow = "▲" if diff > 0 else "▼"
    if good_when is None:
        tone = "info"
    else:
        tone = "good" if (diff > 0) == (good_when == "up") else "bad"
    return f'<span class="chip {tone}">{arrow} {abs(diff):.{decimals}f}{unit} {escape(label)}</span>'


# --------------------------------------------------------------------------
# KPI cards
# --------------------------------------------------------------------------
def kpi_card(label: str, value_html: str, icon_name: str, tone: str = "violet",
             chip: str = "", hint: str = "") -> str:
    hint_html = f'<div class="kpi-hint">{escape(hint)}</div>' if hint else ""
    foot_html = f'<div class="kpi-foot">{chip}</div>' if chip else ""
    return (
        f'<div class="kpi tone-{tone}">'
        f'<div class="kpi-top"><span class="kpi-icon">{icon(icon_name)}</span>'
        f'<span class="kpi-label">{escape(label)}</span></div>'
        f'<div class="kpi-value">{value_html}</div>'
        f'{foot_html}{hint_html}</div>'
    )


def kpi_grid(cards: list[str]) -> None:
    render(f'<div class="kpi-grid fade-in">{"".join(cards)}</div>')


# --------------------------------------------------------------------------
# Layout pieces
# --------------------------------------------------------------------------
def page_header(title: str, subtitle: str, crumb: str) -> None:
    render(
        f'<div class="page-head fade-in"><div class="crumb">Dashboard <span>/</span> {escape(crumb)}</div>'
        f'<h1 class="page-title">{escape(title)}</h1>'
        f'<div class="page-sub">{escape(subtitle)}</div></div>'
    )


def section(title: str, subtitle: str = "", icon_name: str = "bars") -> None:
    sub = f'<div class="section-sub">{escape(subtitle)}</div>' if subtitle else ""
    render(
        f'<div class="section-head fade-in"><span class="section-ic">{icon(icon_name)}</span>'
        f'<div><div class="section-title">{escape(title)}</div>{sub}</div></div>'
    )


def callout(body_html: str, kind: str = "info", icon_name: str = "bulb") -> None:
    render(
        f'<div class="callout {kind} fade-in"><span class="callout-ic">{icon(icon_name)}</span>'
        f'<div class="callout-body">{body_html}</div></div>'
    )


@contextmanager
def chart_card(key: str, title: str, subtitle: str = ""):
    """A themed card (Streamlit bordered container) with a title row."""
    with st.container(border=True, key=f"card_{key}"):
        sub = f'<div class="card-sub">{escape(subtitle)}</div>' if subtitle else ""
        render(f'<div class="card-head"><div class="card-title">{escape(title)}</div>{sub}</div>')
        yield


# --------------------------------------------------------------------------
# Sidebar blocks
# --------------------------------------------------------------------------
def brand_block() -> None:
    render(
        '<div class="brand"><div class="brand-logo">'
        f'{icon("shield")}</div><div><div class="brand-name">Retention Analytics</div>'
        '<div class="brand-tag">Customer Intelligence &amp; Risk</div></div></div>'
    )


def sidebar_label(text: str) -> None:
    render(f'<div class="side-label">{escape(text)}</div>')


def project_info_block(rows: list[tuple[str, str]]) -> None:
    items = "".join(
        f'<div class="info-row"><span>{escape(k)}</span><strong>{escape(v)}</strong></div>' for k, v in rows
    )
    render(f'<div class="project-info"><div class="info-title">Project</div>{items}</div>')
