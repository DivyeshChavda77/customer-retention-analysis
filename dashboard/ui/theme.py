"""Theme tokens (dark / light) and CSS injection.

All colours live in one place. The same tokens feed three consumers:
  1. CSS custom properties (page, sidebar, cards, native Streamlit widgets)
  2. Plotly layouts (charts)
  3. Python-rendered HTML components (KPI cards, callouts)
so switching theme restyles the entire dashboard consistently.
"""

from pathlib import Path

import streamlit as st

from .components import icon_css

THEME_NAMES = ("dark", "light")

TOKENS = {
    "dark": {
        "bg": "#080D1C",
        "bg-image": (
            "radial-gradient(1100px 560px at 88% -12%, rgba(139,92,246,.18), transparent 60%),"
            "radial-gradient(900px 480px at -8% 8%, rgba(34,211,238,.10), transparent 55%)"
        ),
        "sidebar-bg": "linear-gradient(180deg,#0F1530 0%,#0A1022 100%)",
        "card": "linear-gradient(145deg, rgba(25,33,62,.80), rgba(15,21,42,.80))",
        "card-solid": "#121A33",
        "panel": "rgba(148,163,184,.07)",
        "border": "rgba(148,163,184,.16)",
        "text": "#F1F5F9",
        "muted": "#A5B2C6",
        "subtle": "#7384A0",
        "accent": "#8B5CF6",
        "accent-2": "#3B82F6",
        "accent-3": "#22D3EE",
        "pink": "#EC4899",
        "good": "#34D399",
        "warn": "#FBBF24",
        "bad": "#F87171",
        "input-bg": "rgba(11,17,38,.75)",
        "hover": "rgba(139,92,246,.14)",
        "row-alt": "rgba(148,163,184,.06)",
        "shadow": "0 10px 30px rgba(2,6,23,.45)",
        "shadow-hover": "0 0 0 1px rgba(139,92,246,.40), 0 14px 40px rgba(99,102,241,.25)",
        "blur": "blur(14px)",
        "btn-text": "#FFFFFF",
        "table-filter": "none",
    },
    "light": {
        "bg": "#FFFFFF",
        "bg-image": "radial-gradient(1000px 500px at 92% -10%, rgba(99,102,241,.08), transparent 60%)",
        "sidebar-bg": "linear-gradient(180deg,#F6F8FC 0%,#EEF2F9 100%)",
        "card": "#FFFFFF",
        "card-solid": "#FFFFFF",
        "panel": "#F4F6FB",
        "border": "#E3E8F2",
        "text": "#0F172A",
        "muted": "#475569",
        "subtle": "#64748B",
        "accent": "#6D4AFF",
        "accent-2": "#2563EB",
        "accent-3": "#0891B2",
        "pink": "#DB2777",
        "good": "#059669",
        "warn": "#B45309",
        "bad": "#DC2626",
        "input-bg": "#FFFFFF",
        "hover": "rgba(99,102,241,.09)",
        "row-alt": "#F6F8FC",
        "shadow": "0 1px 2px rgba(15,23,42,.05), 0 8px 24px rgba(15,23,42,.06)",
        "shadow-hover": "0 0 0 1px rgba(99,102,241,.35), 0 12px 32px rgba(99,102,241,.16)",
        "blur": "none",
        "btn-text": "#FFFFFF",
        # st.dataframe draws on a <canvas>, which CSS colours cannot reach; the app's dark
        # grid is inverted for light mode instead.
        "table-filter": "invert(1) hue-rotate(180deg)",
    },
}


def current_theme() -> str:
    """Active theme name (kept in session state so it survives navigation)."""
    name = st.session_state.get("theme", "dark")
    return name if name in THEME_NAMES else "dark"


def tokens(name: str | None = None) -> dict:
    return TOKENS[name or current_theme()]


def inject_css(name: str | None = None) -> None:
    """Inject theme variables + the static stylesheet (dashboard/style.css)."""
    name = name or current_theme()
    variables = ";".join(f"--{k}:{v}" for k, v in TOKENS[name].items())
    css_path = Path(__file__).resolve().parent.parent / "style.css"
    css = css_path.read_text(encoding="utf-8")
    st.markdown(
        f"<style>:root{{{variables};color-scheme:{name}}}{icon_css()}{css}</style>",
        unsafe_allow_html=True,
    )
