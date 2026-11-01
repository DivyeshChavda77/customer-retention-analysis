"""Customer Retention Analytics - premium Streamlit dashboard.

Business logic is unchanged and still comes from ../src (analysis, kpi,
scoring, data_cleaning). This file only organises the pages, filters and
presentation; the look lives in style.css and the ui/ package.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# --------------------------------------------------
# PROJECT PATH SETUP
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_PATH = BASE_DIR / "data" / "cleaned_bank_customer.csv"

sys.path.append(str(SRC_DIR))

# --------------------------------------------------
# PAGE CONFIGURATION (must be the first Streamlit call)
# --------------------------------------------------
st.set_page_config(
    page_title="Customer Retention Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="auto",
)

# --------------------------------------------------
# IMPORT PROJECT FUNCTIONS (unchanged business logic)
# --------------------------------------------------
from analysis import (  # noqa: E402
    calculate_overall_churn,
    churn_by_age_group,
    churn_by_credit_card,
    churn_by_credit_score_group,
    churn_by_gender,
    churn_by_geography,
    churn_by_tenure,
)
from data_cleaning import clean_customer_data  # noqa: E402
from kpi import (  # noqa: E402
    credit_card_stickiness_score,
    engagement_retention_ratio,
    high_balance_disengagement_rate,
    product_depth_index,
    relationship_strength_index,
)
from scoring import calculate_retention_risk_score  # noqa: E402

# --------------------------------------------------
# UI LAYER
# --------------------------------------------------
from ui import charts  # noqa: E402
from ui.components import (  # noqa: E402
    animated_number,
    brand_block,
    callout,
    chart_card,
    dataframe,
    delta_chip,
    kpi_card,
    kpi_grid,
    page_header,
    plotly,
    project_info_block,
    render,
    section,
    sidebar_label,
)
from ui.theme import THEME_NAMES, current_theme, inject_css  # noqa: E402

# --------------------------------------------------
# NAVIGATION + THEME STATE
# --------------------------------------------------
PAGES = {
    "overview": (":material/dashboard:", "Overview"),
    "engagement": (":material/monitoring:", "Engagement & Products"),
    "highvalue": (":material/diamond:", "High-Value Customers"),
    "risk": (":material/shield:", "Risk Analysis"),
    "relationship": (":material/handshake:", "Relationship Strength"),
    "segments": (":material/pie_chart:", "Customer Segments"),
}
NAV_LABEL = {key: f"{ic} {name}" for key, (ic, name) in PAGES.items()}
LABEL_TO_PAGE = {label: key for key, label in NAV_LABEL.items()}
THEME_LABEL = {"dark": ":material/dark_mode: Dark", "light": ":material/light_mode: Light"}
LABEL_TO_THEME = {label: name for name, label in THEME_LABEL.items()}


def _init_state() -> None:
    params = st.query_params
    if "theme" not in st.session_state:
        wanted = params.get("theme", "dark")
        st.session_state.theme = wanted if wanted in THEME_NAMES else "dark"
    st.session_state.setdefault("theme_sb", THEME_LABEL[st.session_state.theme])
    st.session_state.setdefault("theme_main", THEME_LABEL[st.session_state.theme])
    if "nav_page" not in st.session_state:
        wanted = params.get("page", "overview")
        st.session_state.nav_page = NAV_LABEL.get(wanted, NAV_LABEL["overview"])


def _on_theme_change(source: str) -> None:
    name = LABEL_TO_THEME[st.session_state[source]]
    st.session_state.theme = name
    st.session_state.theme_sb = THEME_LABEL[name]
    st.session_state.theme_main = THEME_LABEL[name]
    st.query_params["theme"] = name


def _on_nav_change() -> None:
    st.query_params["page"] = LABEL_TO_PAGE[st.session_state.nav_page]


_init_state()
THEME = current_theme()
inject_css(THEME)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


df = load_data()

# --------------------------------------------------
# CACHED COMPUTATION (same functions, just memoised)
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def compute_risk(data):
    return calculate_retention_risk_score(data)


@st.cache_data(show_spinner=False)
def compute_rsi(data):
    return relationship_strength_index(data)


def compute_metrics(data) -> dict:
    overall = calculate_overall_churn(data)
    return {
        "overall": overall,
        "err": engagement_retention_ratio(data),
        "pdi": product_depth_index(data),
        "hbdr": high_balance_disengagement_rate(data),
        "ccs": credit_card_stickiness_score(data),
    }


@st.cache_data(show_spinner=False)
def portfolio_baseline(_data) -> dict:
    """Metrics for ALL customers - the reference for trend chips."""
    return compute_metrics(_data)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
FILTERS = {
    "f_geo": ("Geography", "Geography"),
    "f_gender": ("Gender", "Gender"),
    "f_eng": ("EngagementStatus", "Engagement Status"),
    "f_prod": ("NumOfProducts", "Number of Products"),
}
FILTER_OPTIONS = {key: sorted(df[col].dropna().unique()) for key, (col, _) in FILTERS.items()}
for _key, _options in FILTER_OPTIONS.items():
    if _key not in st.session_state:
        st.session_state[_key] = list(_options)


def _reset_filters() -> None:
    for key, options in FILTER_OPTIONS.items():
        st.session_state[key] = list(options)


with st.sidebar:
    brand_block()

    sidebar_label("Navigation")
    st.radio(
        "Navigation",
        options=list(NAV_LABEL.values()),
        key="nav_page",
        label_visibility="collapsed",
        on_change=_on_nav_change,
    )

    sidebar_label("Dashboard Filters")
    for key, (_col, label) in FILTERS.items():
        st.multiselect(label, options=FILTER_OPTIONS[key], key=key)
    try:
        st.button("Reset filters", key="reset_filters", on_click=_reset_filters, width="stretch")
    except TypeError:  # older Streamlit versions
        st.button("Reset filters", key="reset_filters", on_click=_reset_filters, use_container_width=True)

    project_info_block(
        [
            ("Dataset", "European Bank"),
            ("Records", f"{len(df):,}"),
            ("Target", "Exited (churn)"),
            ("Stack", "Streamlit · Plotly"),
        ]
    )

# --------------------------------------------------
# APPLY FILTERS (unchanged logic)
# --------------------------------------------------
selected_geography = st.session_state["f_geo"]
selected_gender = st.session_state["f_gender"]
selected_engagement = st.session_state["f_eng"]
selected_products = st.session_state["f_prod"]

filtered_df = df[
    (df["Geography"].isin(selected_geography))
    & (df["Gender"].isin(selected_gender))
    & (df["EngagementStatus"].isin(selected_engagement))
    & (df["NumOfProducts"].isin(selected_products))
].copy()

is_filtered = len(filtered_df) != len(df)
PAGE = LABEL_TO_PAGE[st.session_state.nav_page]

# --------------------------------------------------
# PAGE HEADER + THEME TOGGLE
# --------------------------------------------------
head_left, head_right = st.columns([3, 1.4])
with head_left:
    page_header(
        "Customer Retention Analytics Dashboard" if PAGE == "overview" else PAGES[PAGE][1],
        "Analyze customer engagement, product utilization, churn behavior, "
        "relationship strength and retention risk.",
        PAGES[PAGE][1],
    )
with head_right:
    st.radio(
        "Theme",
        options=list(THEME_LABEL.values()),
        key="theme_main",
        horizontal=True,
        label_visibility="collapsed",
        on_change=_on_theme_change,
        args=("theme_main",),
    )

# --------------------------------------------------
# HANDLE EMPTY FILTER RESULT
# --------------------------------------------------
if filtered_df.empty:
    callout("<strong>No customers match the selected filters.</strong> "
            "Adjust or reset the filters in the sidebar.", kind="warn", icon_name="alert")
    st.stop()

# --------------------------------------------------
# SHARED METRICS
# --------------------------------------------------
metrics = compute_metrics(filtered_df)
base = portfolio_baseline(df)
overall = metrics["overall"]
total_customers = overall["total_customers"]
churn_rate = overall["churn_rate"]
retention_rate = overall["retention_rate"]
err, pdi, hbdr, ccs = metrics["err"], metrics["pdi"], metrics["hbdr"], metrics["ccs"]


def num(value: float) -> str:
    """Two-decimal text for insight sentences; 'n/a' when a ratio is undefined."""
    return f"{value:.2f}" if pd.notna(value) else "n/a"


def chip_for(key: str, current: float, unit: str = "", good_when=None, decimals: int = 2) -> str:
    """Trend chip vs the full portfolio - only shown when filters narrow the data."""
    if not is_filtered:
        return ""
    reference = base["overall"][key] if key in base["overall"] else base[key]
    return delta_chip(current, reference, unit=unit, decimals=decimals, good_when=good_when)


def filter_banner() -> None:
    pills = []
    for key, (_col, label) in FILTERS.items():
        selected, options = st.session_state[key], FILTER_OPTIONS[key]
        if len(selected) != len(options):
            pills.append(f'<span class="pill">{label}: {", ".join(str(v) for v in selected)}</span>')
    share = len(filtered_df) / len(df) * 100
    extra = "".join(pills) if pills else '<span class="pill">All customers</span>'
    render(
        f'<div class="filter-banner fade-in">🔎 Currently analyzing <strong>{len(filtered_df):,}</strong> '
        f'customers ({share:.1f}% of portfolio) based on the selected filters. {extra}</div>'
    )


def high_value_disengaged_of(risk_df):
    """High-value disengaged customers (same definition as the original dashboard)."""
    threshold = risk_df["Balance"].quantile(0.75)
    subset = risk_df[(risk_df["Balance"] >= threshold) & (risk_df["IsActiveMember"] == 0)].copy()
    return subset, threshold


# ==================================================
# PAGES
# ==================================================
def page_overview() -> None:
    section("Executive Overview", "Headline churn and retention for the selected customers", "layout")
    kpi_grid([
        kpi_card("Total Customers", animated_number(total_customers), "users", "blue",
                 chip=('<span class="chip info">'
                       f'{total_customers / len(df) * 100:.1f}% of all customers</span>')
                 if is_filtered else "",
                 hint="Customers in the current selection"),
        kpi_card("Churn Rate", animated_number(churn_rate, 2, suffix="%"), "alert", "pink",
                 chip=chip_for("churn_rate", churn_rate, " pp", "down"),
                 hint="Share of customers who exited"),
        kpi_card("Retention Rate", animated_number(retention_rate, 2, suffix="%"), "refresh", "green",
                 chip=chip_for("retention_rate", retention_rate, " pp", "up"),
                 hint="Share of customers retained"),
    ])

    section("Retention Performance KPIs", "Analyst-developed indices - they update with the sidebar filters", "target")
    kpi_grid([
        kpi_card("Engagement Retention Ratio", animated_number(err, 2), "activity", "violet",
                 chip=chip_for("err", err), hint="Retention of active vs inactive customers"),
        kpi_card("Product Depth Index", animated_number(pdi, 2), "package", "blue",
                 chip=chip_for("pdi", pdi), hint="Retention of multi- vs single-product customers"),
        kpi_card("High-Balance Disengagement", animated_number(hbdr, 2, suffix="%"), "wallet", "amber",
                 chip=chip_for("hbdr", hbdr, " pp", "down"), hint="High-balance customers who are inactive"),
        kpi_card("Credit Card Stickiness", animated_number(ccs, 2), "card", "cyan",
                 chip=chip_for("ccs", ccs), hint="Retention of card vs no-card customers"),
    ])
    st.caption("These KPIs update dynamically based on the customers selected through the sidebar filters.")
    filter_banner()

    section("Executive Insights", "What the selected customers tell us", "bulb")
    risk_df = compute_risk(filtered_df)
    high_value_disengaged, _ = high_value_disengaged_of(risk_df)

    left, right = st.columns([1, 1.15])
    with left:
        with chart_card("donut", "Churn vs Retention", "Retained and churned customers in the current selection"):
            plotly(charts.donut(overall["retained_customers"], overall["churned_customers"],
                                churn_rate, THEME, height=400), key="chart_donut")
    with right:
        with chart_card("findings", "Key Findings", "Calculated live from the filtered data"):
            render(
                '<ul class="finding-list">'
                f'<li><span>The current filtered customer population contains <strong>{len(filtered_df):,} customers</strong>.</span></li>'
                f'<li><span>The historical churn rate for the selected population is <strong>{churn_rate:.2f}%</strong>.</span></li>'
                f'<li><span>The retention rate is <strong>{retention_rate:.2f}%</strong>.</span></li>'
                f'<li><span>The Engagement Retention Ratio is <strong>{num(err)}</strong>, comparing retention among active and inactive customers.</span></li>'
                f'<li><span>The Product Depth Index is <strong>{num(pdi)}</strong>, comparing multi-product and single-product retention.</span></li>'
                f'<li><span><strong>{len(high_value_disengaged):,}</strong> high-value disengaged customers are currently identified under the selected filters.</span></li>'
                '</ul>'
            )
    render(
        '<div class="focus-box"><div class="t">Recommended Focus</div><div class="b">'
        'Prioritize customers who combine high financial value with low engagement, '
        'especially those classified into higher retention-priority segments.</div></div>'
    )


def page_engagement() -> None:
    section("Engagement & Product Analysis", "How engagement and product depth relate to historical churn", "bars")

    # --- same groupby logic as the original dashboard ---
    engagement_analysis = (
        filtered_df.groupby("EngagementStatus")["Exited"]
        .agg(CustomerCount="count", ChurnRate="mean").reset_index()
    )
    engagement_analysis["ChurnRate"] = engagement_analysis["ChurnRate"] * 100

    product_analysis = (
        filtered_df.groupby("NumOfProducts")["Exited"]
        .agg(CustomerCount="count", ChurnRate="mean").reset_index()
    )
    product_analysis["ChurnRate"] = product_analysis["ChurnRate"] * 100

    col1, col2 = st.columns(2)
    with col1:
        with chart_card("eng", "Engagement vs Churn", "Churn rate of active vs inactive customers"):
            plotly(charts.churn_bar(engagement_analysis, "EngagementStatus", "Engagement Status", THEME),
                   key="chart_engagement")
    with col2:
        with chart_card("prod", "Product Utilization Impact", "Churn rate by number of products held"):
            plotly(charts.churn_bar(product_analysis, "NumOfProducts", "Number of Products", THEME),
                   key="chart_products")

    section("Product Utilization & Engagement", "Churn rate across product category and engagement status", "activity")
    heatmap_data = (
        filtered_df.groupby(["ProductCategory", "EngagementStatus"])["Exited"].mean().reset_index()
    )
    heatmap_data["ChurnRate"] = heatmap_data["Exited"] * 100
    heatmap_pivot = heatmap_data.pivot(index="ProductCategory", columns="EngagementStatus", values="ChurnRate")
    with chart_card("heat", "Product + Engagement Heatmap", "Darker / hotter cells mean higher historical churn"):
        plotly(charts.heatmap(heatmap_pivot, THEME), key="chart_heatmap")


def page_highvalue() -> None:
    risk_df = compute_risk(filtered_df)
    high_value_disengaged, balance_threshold = high_value_disengaged_of(risk_df)

    section("High-Value Disengaged Customers", "Customers with relatively high balances who are currently inactive", "wallet")
    hv_churn_rate = high_value_disengaged["Exited"].mean() * 100 if len(high_value_disengaged) > 0 else 0

    kpi_grid([
        kpi_card("High-Value Disengaged Customers", animated_number(len(high_value_disengaged)), "users", "amber",
                 hint="High balance and inactive"),
        kpi_card("High-Balance Threshold", animated_number(balance_threshold, 0, prefix="€"), "euro", "blue",
                 hint="75th percentile of balance in the selection"),
        kpi_card("Historical Churn Rate", animated_number(hv_churn_rate, 2, suffix="%"), "trend-down", "pink",
                 hint="Churn among high-value disengaged customers"),
    ])
    callout("<strong>Business Focus:</strong> These customers have relatively high account balances "
            "but are currently inactive. They may represent important retention opportunities.",
            kind="warn")

    # --- priority filter (same options as the original) ---
    if "priority_sel" in st.session_state:  # keep the choice while navigating between pages
        st.session_state["priority_sel"] = st.session_state["priority_sel"]
    selected_priority = st.selectbox("Retention Priority", ["All", "Critical", "High", "Medium"], key="priority_sel")

    priority_filtered_df = risk_df[risk_df["RetentionPriority"].notna()].copy()
    if selected_priority != "All":
        priority_filtered_df = priority_filtered_df[priority_filtered_df["RetentionPriority"] == selected_priority]

    if len(priority_filtered_df) > 0:
        display_columns = ["CustomerId", "Surname", "Geography", "Age", "Balance", "NumOfProducts",
                           "RetentionRiskScore", "RiskCategory", "RetentionPriority"]
        customer_table = priority_filtered_df[display_columns].sort_values(
            by=["RetentionPriority", "RetentionRiskScore", "Balance"], ascending=[True, False, False]
        )
        render('<div class="table-title">Customers Requiring Retention Attention</div>'
               '<div class="table-sub">High-balance customers who are currently inactive, '
               'ranked by retention priority and risk score.</div>')
        dataframe(
            customer_table, hide_index=True, height=440,
            column_config={
                "CustomerId": st.column_config.NumberColumn("Customer ID", format="%d"),
                "Balance": st.column_config.NumberColumn("Balance", format="€%.2f"),
                "NumOfProducts": st.column_config.NumberColumn("Products", format="%d"),
                "RetentionRiskScore": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=9, format="%d"),
                "RiskCategory": "Risk Category",
                "RetentionPriority": "Priority",
            },
        )
    else:
        st.info(f"No customers with '{selected_priority}' retention priority match the current filters.")

    st.download_button(
        label="Download High-Value Customer List",
        data=priority_filtered_df.to_csv(index=False),
        file_name="priority_filtered_customers.csv",
        mime="text/csv",
        icon=":material/download:",
        key="dl_priority",
    )

    section("Retention Action Recommendation", "Suggested response by priority level", "target")
    render(
        '<div class="action-grid fade-in">'
        '<div class="action" style="--c:var(--bad)"><div class="lvl">Critical</div><div class="txt">'
        'Immediate relationship-manager intervention, personalized outreach and product engagement review.</div></div>'
        '<div class="action" style="--c:var(--warn)"><div class="lvl">High</div><div class="txt">'
        'Targeted retention campaign and engagement follow-up.</div></div>'
        '<div class="action" style="--c:var(--accent-2)"><div class="lvl">Medium</div><div class="txt">'
        'Digital engagement campaign and product education.</div></div>'
        '<div class="action" style="--c:var(--good)"><div class="lvl">Normal</div><div class="txt">'
        'Continue regular customer engagement programs.</div></div></div>'
    )


def page_risk() -> None:
    risk_df = compute_risk(filtered_df)
    section("Retention Risk Analysis", "Rule-based retention risk score across the selected customers", "shield")

    risk_distribution = risk_df["RiskCategory"].value_counts().reset_index()
    risk_distribution.columns = ["RiskCategory", "CustomerCount"]

    low_count = risk_df["RiskCategory"].eq("Low Risk").sum()
    medium_count = risk_df["RiskCategory"].eq("Medium Risk").sum()
    high_count = risk_df["RiskCategory"].eq("High Risk").sum()
    n = len(risk_df)

    kpi_grid([
        kpi_card("Low Risk", animated_number(low_count), "shield", "green",
                 hint=f"{low_count / n * 100:.1f}% of selected customers"),
        kpi_card("Medium Risk", animated_number(medium_count), "alert", "amber",
                 hint=f"{medium_count / n * 100:.1f}% of selected customers"),
        kpi_card("High Risk", animated_number(high_count), "alert", "red",
                 hint=f"{high_count / n * 100:.1f}% of selected customers"),
    ])
    st.caption("Risk categories are based on the retention risk score calculated by the project scoring model.")

    t = charts.tokens(THEME)
    with chart_card("risk", "Customer Distribution by Risk Category",
                    "Distribution of customers across retention risk levels."):
        plotly(charts.count_bar(
            risk_distribution, "RiskCategory", "CustomerCount", "Risk Category", THEME,
            colors={"Low Risk": t["good"], "Medium Risk": t["warn"], "High Risk": t["bad"]},
            order=["Low Risk", "Medium Risk", "High Risk"], height=420), key="chart_risk")

    risk_download = risk_df[[
        "CustomerId", "Surname", "Geography", "Age", "Balance", "NumOfProducts", "IsActiveMember",
        "RetentionRiskScore", "RiskCategory", "HighValueCustomer", "RetentionPriority", "Exited",
    ]].copy()
    st.download_button(
        label="Download Customer Risk Analysis",
        data=risk_download.to_csv(index=False),
        file_name="customer_retention_risk_analysis.csv",
        mime="text/csv",
        icon=":material/download:",
        key="dl_risk",
    )


def page_relationship() -> None:
    section("Customer Relationship Strength", "Composite score of engagement, product depth, card, tenure and balance", "heart")
    rsi_df = compute_rsi(filtered_df)
    n = len(rsi_df)

    strong_count = (rsi_df["RelationshipStrengthCategory"] == "Strong").sum()
    moderate_count = (rsi_df["RelationshipStrengthCategory"] == "Moderate").sum()
    weak_count = (rsi_df["RelationshipStrengthCategory"] == "Weak").sum()
    kpi_grid([
        kpi_card("Strong Relationships", animated_number(strong_count), "heart", "green",
                 hint=f"{strong_count / n * 100:.1f}% of selected customers"),
        kpi_card("Moderate Relationships", animated_number(moderate_count), "heart", "amber",
                 hint=f"{moderate_count / n * 100:.1f}% of selected customers"),
        kpi_card("Weak Relationships", animated_number(weak_count), "heart", "red",
                 hint=f"{weak_count / n * 100:.1f}% of selected customers"),
    ])

    relationship_distribution = rsi_df["RelationshipStrengthCategory"].value_counts().reset_index()
    relationship_distribution.columns = ["RelationshipStrengthCategory", "CustomerCount"]

    relationship_churn = (
        rsi_df.groupby("RelationshipStrengthCategory", observed=True)["Exited"]
        .agg(CustomerCount="count", ChurnRate="mean").reset_index()
    )
    relationship_churn["ChurnRate"] = relationship_churn["ChurnRate"] * 100

    t = charts.tokens(THEME)
    col1, col2 = st.columns(2)
    with col1:
        with chart_card("rsi", "Relationship Distribution", "Customers by relationship-strength category"):
            plotly(charts.count_bar(
                relationship_distribution, "RelationshipStrengthCategory", "CustomerCount",
                "Relationship Strength", THEME,
                colors={"Weak": t["bad"], "Moderate": t["warn"], "Strong": t["good"]},
                order=["Weak", "Moderate", "Strong"]), key="chart_rsi")
    with col2:
        with chart_card("rsichurn", "Churn by Relationship Strength", "Historical churn rate per category"):
            plotly(charts.churn_bar(
                relationship_churn, "RelationshipStrengthCategory", "Relationship Strength", THEME,
                y_label="Historical Churn Rate (%)"), key="chart_rsi_churn")

    callout("<strong>Business Interpretation:</strong> The Relationship Strength Index combines customer "
            "engagement, product depth, credit card ownership, tenure and balance into an analyst-developed "
            "relationship score. Higher scores indicate stronger observable relationships with the bank and "
            "can help prioritize retention and engagement strategies.")


def page_segments() -> None:
    section("Customer Segments", "Churn by demographic and product segment - from the project's analysis module", "pie")
    seg_df = clean_customer_data(filtered_df)

    specs = [
        ("seg_geo", "Churn by Geography", churn_by_geography(seg_df), "Geography", "Geography"),
        ("seg_gender", "Churn by Gender", churn_by_gender(seg_df), "Gender", "Gender"),
        ("seg_age", "Churn by Age Group", churn_by_age_group(seg_df), "AgeGroup", "Age Group"),
        ("seg_credit", "Churn by Credit Score Group", churn_by_credit_score_group(seg_df), "CreditScoreGroup", "Credit Score"),
        ("seg_tenure", "Churn by Tenure", churn_by_tenure(seg_df), "Tenure", "Tenure (years)"),
        ("seg_card", "Churn by Credit Card Ownership", churn_by_credit_card(seg_df), "CreditCardStatus", "Credit Card"),
    ]
    for i in range(0, len(specs), 2):
        cols = st.columns(2)
        for col, (key, title, data, x, label) in zip(cols, specs[i:i + 2]):
            data = data.dropna(subset=["ChurnRate"])
            with col:
                with chart_card(key, title, "Historical churn rate (%) - hover for customer counts"):
                    plotly(charts.churn_bar(data, x, label, THEME, height=330), key=f"chart_{key}")


PAGE_RENDERERS = {
    "overview": page_overview,
    "engagement": page_engagement,
    "highvalue": page_highvalue,
    "risk": page_risk,
    "relationship": page_relationship,
    "segments": page_segments,
}
PAGE_RENDERERS[PAGE]()

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption("Customer Retention Analytics | Banking Customer Engagement & Retention Project")
st.caption(
    "Analytical indices and retention scores are analyst-developed "
    "for project-based customer segmentation and prioritization."
)
