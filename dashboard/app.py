import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

# Use a light theme for all Plotly charts
pio.templates.default = "plotly_dark"

# --------------------------------------------------
# PROJECT PATH SETUP
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_PATH = BASE_DIR / "data" / "cleaned_bank_customer.csv"

sys.path.append(str(SRC_DIR))

# --------------------------------------------------
# IMPORT PROJECT FUNCTIONS
# --------------------------------------------------

from analysis import calculate_overall_churn

from kpi import (
    engagement_retention_ratio,
    product_depth_index,
    high_balance_disengagement_rate,
    credit_card_stickiness_score,
    relationship_strength_index
)

from scoring import calculate_retention_risk_score

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Customer Retention Analytics",
    page_icon="🏦",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM DARK DASHBOARD STYLING
# --------------------------------------------------
def load_css():
    css_path = Path(__file__).resolve().parent / "style.css"

    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css()

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

df = load_data()

# --------------------------------------------------
# PLOTLY CHART STYLING
# --------------------------------------------------

def style_chart(fig):

    fig.update_layout(
        template="plotly_dark",

        paper_bgcolor="#111827",
        plot_bgcolor="#111827",

        font=dict(
            family="Arial",
            color="#F8FAFC",
            size=12
        ),

        xaxis=dict(
            title_font=dict(
                size=12,
                color="#CBD5E1"
            ),
            tickfont=dict(
                size=11,
                color="#94A3B8"
            ),
            gridcolor="#273449",
            zeroline=False
        ),

        yaxis=dict(
            title_font=dict(
                size=12,
                color="#CBD5E1"
            ),
            tickfont=dict(
                size=11,
                color="#94A3B8"
            ),
            gridcolor="#273449",
            zeroline=False
        ),

        margin=dict(
            l=50,
            r=30,
            t=15,
            b=50
        ),

        height=400,

        hoverlabel=dict(
            bgcolor="#1F2937",
            font_size=12,
            font_color="#F8FAFC"
        )
    )

    return fig

# --------------------------------------------------
# DASHBOARD TITLE
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🏦 Customer Retention Analytics Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Analyze customer engagement, product utilization,
    churn behavior, relationship strength and retention risk.
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.markdown(
    """
    <div style="
        font-size: 22px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
    ">
        🏦 Retention Analytics
    </div>

    <div style="
        font-size: 12px;
        color: #98a2b3;
        margin-bottom: 24px;
    ">
        Customer Intelligence & Risk
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    """
    <div style="
        font-size: 14px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    ">
        Dashboard Filters
    </div>
    """,
    unsafe_allow_html=True
)

# Geography Filter

geography_options = sorted(
    df["Geography"].dropna().unique()
)

selected_geography = st.sidebar.multiselect(
    "🌍 Geography",
    options=geography_options,
    default=geography_options
)

# Gender Filter

gender_options = sorted(
    df["Gender"].dropna().unique()
)

selected_gender = st.sidebar.multiselect(
    "👤 Gender",
    options=gender_options,
    default=gender_options
)

# Engagement Filter

engagement_options = sorted(
    df["EngagementStatus"].dropna().unique()
)

selected_engagement = st.sidebar.multiselect(
    "📊 Engagement Status",
    options=engagement_options,
    default=engagement_options
)

# Product Filter

product_options = sorted(
    df["NumOfProducts"].dropna().unique()
)

selected_products = st.sidebar.multiselect(
    "📦 Number of Products",
    options=product_options,
    default=product_options
)

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df[
    (df["Geography"].isin(selected_geography)) &
    (df["Gender"].isin(selected_gender)) &
    (df["EngagementStatus"].isin(selected_engagement)) &
    (df["NumOfProducts"].isin(selected_products))
].copy()

# --------------------------------------------------
# HANDLE EMPTY FILTER RESULT
# --------------------------------------------------

if filtered_df.empty:

    st.warning(
        "No customers match the selected filters."
    )

    st.stop()

# --------------------------------------------------
# OVERALL METRICS
# --------------------------------------------------

overall = calculate_overall_churn(filtered_df)

total_customers = overall["total_customers"]
churn_rate = overall["churn_rate"]
retention_rate = overall["retention_rate"]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

err = engagement_retention_ratio(filtered_df)

pdi = product_depth_index(filtered_df)

hbdr = high_balance_disengagement_rate(
    filtered_df
)

ccs = credit_card_stickiness_score(
    filtered_df
)

# --------------------------------------------------
# TOP METRIC CARDS
# --------------------------------------------------

st.markdown(
    '<div class="section-title">📊 Executive Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "👥 Total Customers",
    f"{total_customers:,}"
)

col2.metric(
    "⚠️ Churn Rate",
    f"{churn_rate:.2f}%"
)

col3.metric(
    "🔄 Retention Rate",
    f"{retention_rate:.2f}%"
)


st.divider()

# --------------------------------------------------
# BUSINESS KPI CARDS
# --------------------------------------------------

st.markdown(
    '<div class="section-title">🎯 Retention Performance KPIs</div>',
    unsafe_allow_html=True
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric(
    "📊 Engagement Retention Ratio",
    f"{err:.2f}"
)

kpi2.metric(
    "📦 Product Depth Index",
    f"{pdi:.2f}"
)

kpi3.metric(
    "💰 High-Balance Disengagement",
    f"{hbdr:.2f}%"
)

kpi4.metric(
    "💳 Credit Card Stickiness",
    f"{ccs:.2f}"
)

st.caption(
    "These KPIs update dynamically based on the customers "
    "selected through the sidebar filters."
)

# --------------------------------------------------
# FILTER INFORMATION
# --------------------------------------------------

st.markdown(
    f"""
    <div style="
        background-color: #111827;
        border: 1px solid #273449;
        border-radius: 10px;
        padding: 10px 16px;
        margin-top: 8px;
        margin-bottom: 22px;
        color: #CBD5E1;
        font-size: 13px;
    ">
        🔎 Currently analyzing
        <strong>{len(filtered_df):,}</strong>
        customers based on the selected filters.
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# ENGAGEMENT VS CHURN
# --------------------------------------------------

st.markdown(
    '<div class="section-title">📊 Engagement & Product Analysis</div>',
    unsafe_allow_html=True
)

chart_col1, chart_col2 = st.columns(2)

engagement_analysis = (
    filtered_df
    .groupby("EngagementStatus")["Exited"]
    .agg(
        CustomerCount="count",
        ChurnRate="mean"
    )
    .reset_index()
)

engagement_analysis["ChurnRate"] = (
    engagement_analysis["ChurnRate"] * 100
)

fig_engagement = px.bar(
    engagement_analysis,
    x="EngagementStatus",
    y="ChurnRate",
    text="ChurnRate",
    labels={
        "EngagementStatus": "Engagement Status",
        "ChurnRate": "Churn Rate (%)"
    }
)

fig_engagement.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig_engagement.update_layout(
    yaxis_title="Churn Rate (%)",
    xaxis_title="Engagement Status",
    yaxis_range=[
        0,
        max(engagement_analysis["ChurnRate"]) * 1.25
    ]
)

fig_engagement = style_chart(fig_engagement)

fig_engagement.update_traces(
    marker_color="#3b82f6"
)

with chart_col1:

    st.markdown(
        """
        <div class="chart-card-title">
            📈 Engagement vs Churn
        </div>
        """,
        unsafe_allow_html=True
    )

    st.plotly_chart(
        fig_engagement,
        use_container_width=True
    )

# --------------------------------------------------
# PRODUCT UTILIZATION VS CHURN
# --------------------------------------------------

# st.subheader("2. Product Utilization Impact")

product_analysis = (
    filtered_df
    .groupby("NumOfProducts")["Exited"]
    .agg(
        CustomerCount="count",
        ChurnRate="mean"
    )
    .reset_index()
)

product_analysis["ChurnRate"] = (
    product_analysis["ChurnRate"] * 100
)

fig_product = px.bar(
    product_analysis,
    x="NumOfProducts",
    y="ChurnRate",
    text="ChurnRate",
    labels={
        "NumOfProducts": "Number of Products",
        "ChurnRate": "Churn Rate (%)"
    }
)

fig_product.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig_product.update_layout(
    yaxis_title="Churn Rate (%)",
    xaxis_title="Number of Products"
)

fig_product = style_chart(fig_product)

fig_product.update_traces(
    marker_color="#3b82f6"
)

with chart_col2:

    st.markdown(
        """
        <div class="chart-card-title">
            📦 Product Utilization Impact
        </div>
        """,
        unsafe_allow_html=True
    )

    st.plotly_chart(
        fig_product,
        use_container_width=True
    )

# --------------------------------------------------
# PRODUCT + ENGAGEMENT HEATMAP
# --------------------------------------------------

st.markdown(
    '<div class="section-title">🔥 Product Utilization & Engagement</div>',
    unsafe_allow_html=True
)

heatmap_data = (
    filtered_df
    .groupby(
        ["ProductCategory", "EngagementStatus"]
    )["Exited"]
    .mean()
    .reset_index()
)

heatmap_data["ChurnRate"] = (
    heatmap_data["Exited"] * 100
)

heatmap_pivot = heatmap_data.pivot(
    index="ProductCategory",
    columns="EngagementStatus",
    values="ChurnRate"
)

fig_heatmap = px.imshow(
    heatmap_pivot,
    text_auto=".2f",
    aspect="auto",
    labels={
        "x": "Engagement Status",
        "y": "Product Category",
        "color": "Churn Rate (%)"
    }
)

fig_heatmap = style_chart(fig_heatmap)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)

# --------------------------------------------------
# HIGH-VALUE DISENGAGED CUSTOMER DETECTOR
# --------------------------------------------------

st.markdown(
    '<div class="section-title">⚠️ High-Value Disengaged Customers</div>',
    unsafe_allow_html=True
)

# Calculate risk score on filtered customers
risk_df = calculate_retention_risk_score(
    filtered_df
)

# High-value threshold from complete
balance_threshold = risk_df["Balance"].quantile(0.75)

# Identify high-value disengaged customers
high_value_disengaged = risk_df[
    (risk_df["Balance"] >= balance_threshold) &
    (risk_df["IsActiveMember"] == 0)
].copy()


# --------------------------------------------------
# SUMMARY METRICS
# --------------------------------------------------

hv_col1, hv_col2, hv_col3 = st.columns(3)

hv_col1.metric(
    "👥 High-Value Disengaged Customers",
    f"{len(high_value_disengaged):,}"
)

hv_col2.metric(
    "💰 High-Balance Threshold",
    f"€{balance_threshold:,.0f}"
)

if len(high_value_disengaged) > 0:

    hv_churn_rate = (
        high_value_disengaged["Exited"].mean() * 100
    )

else:

    hv_churn_rate = 0


hv_col3.metric(
    "📉 Historical Churn Rate",
    f"{hv_churn_rate:.2f}%"
)

st.markdown(
    """
    <div style="
        background-color: #1F2937;
        border: 1px solid #92400E;
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 12px;
        margin-bottom: 18px;
        color: #FCD34D;
        font-size: 13px;
    ">
        💡 <strong>Business Focus:</strong>
        These customers have relatively high account balances
        but are currently inactive. They may represent important
        retention opportunities.
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# PRIORITY FILTER
# --------------------------------------------------

priority_options = [
    "All",
    "Critical",
    "High",
    "Medium"
]

selected_priority = st.selectbox(
    "🎯 Retention Priority",
    priority_options
)

# Keep the original high-value disengaged data unchanged
priority_filtered_df = risk_df[
    risk_df["RetentionPriority"].notna()
].copy()

if selected_priority != "All":

    priority_filtered_df = priority_filtered_df[
        priority_filtered_df["RetentionPriority"]
        == selected_priority
    ]

# --------------------------------------------------
# CUSTOMER TABLE
# --------------------------------------------------

if len(priority_filtered_df) > 0:

    display_columns = [
        "CustomerId",
        "Surname",
        "Geography",
        "Age",
        "Balance",
        "NumOfProducts",
        "RetentionRiskScore",
        "RiskCategory",
        "RetentionPriority"
    ]

    customer_table = (
        priority_filtered_df[
            display_columns
        ]
        .sort_values(
            by=[
                "RetentionPriority",
                "RetentionRiskScore",
                "Balance"
            ],
            ascending=[
                True,
                False,
                False
            ]
        )
    )

    st.markdown(
        """
        <div style="
            font-size: 15px;
            font-weight: 700;
            color: #F8FAFC;
            margin-top: 18px;
            margin-bottom: 8px;
        ">
            👤 Customers Requiring Retention Attention
        </div>

        <div style="
            font-size: 12px;
            color: #667085;
            margin-bottom: 12px;
        ">
            High-balance customers who are currently inactive,
            ranked by retention priority and risk score.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(
        customer_table,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        f"No customers with '{selected_priority}' "
        "retention priority match the current filters."
    )

st.download_button(
    label="📥 Download High-Value Customer List",
    data=priority_filtered_df.to_csv(index=False),
    file_name="priority_filtered_customers.csv",
    mime="text/csv"
)

# --------------------------------------------------
# RETENTION ACTION RECOMMENDATION
# --------------------------------------------------

st.subheader("Retention Action Recommendation")


st.write(
    """
    **Critical:** Immediate relationship-manager intervention,
    personalized outreach and product engagement review.

    **High:** Targeted retention campaign and engagement follow-up.

    **Medium:** Digital engagement campaign and product education.

    **Normal:** Continue regular customer engagement programs.
    """
)

# --------------------------------------------------
# RISK DISTRIBUTION
# --------------------------------------------------

# st.subheader("5. Retention Risk Distribution")

st.markdown(
    '<div class="section-title">⚠️ Retention Risk Analysis</div>',
    unsafe_allow_html=True
)

risk_distribution = (
    risk_df["RiskCategory"]
    .value_counts()
    .reset_index()
)

risk_distribution.columns = [
    "RiskCategory",
    "CustomerCount"
]

# --------------------------------------------------
# RISK SUMMARY CARDS
# --------------------------------------------------

# --------------------------------------------------
# RISK SUMMARY CARDS
# --------------------------------------------------

low_count = (
    risk_df["RiskCategory"]
    .eq("Low Risk")
    .sum()
)

medium_count = (
    risk_df["RiskCategory"]
    .eq("Medium Risk")
    .sum()
)

high_count = (
    risk_df["RiskCategory"]
    .eq("High Risk")
    .sum()
)

risk_col1, risk_col2, risk_col3 = st.columns(3)

risk_col1.metric(
    "🟢 Low Risk",
    f"{low_count:,}"
)

risk_col2.metric(
    "🟡 Medium Risk",
    f"{medium_count:,}"
)

risk_col3.metric(
    "🔴 High Risk",
    f"{high_count:,}"
)

st.caption(
    "Risk categories are based on the retention risk score "
    "calculated by the project scoring model."
)

fig_risk = px.bar(
    risk_distribution,
    x="RiskCategory",
    y="CustomerCount",
    text="CustomerCount",
    labels={
        "RiskCategory": "Risk Category",
        "CustomerCount": "Number of Customers"
    }
)

fig_risk.update_traces(
    textposition="outside"
)

fig_risk = style_chart(fig_risk)

fig_risk.update_layout(
    height=420
)

fig_risk.update_traces(
    marker_color="#3b82f6"
)

st.markdown(
    """
    <div style="
        font-size: 15px;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 20px;
        margin-bottom: 4px;
    ">
        📊 Customer Distribution by Risk Category
    </div>

    <div style="
        font-size: 12px;
        color: #667085;
        margin-bottom: 8px;
    ">
        Distribution of customers across retention risk levels.
    </div>
    """,
    unsafe_allow_html=True
)

st.plotly_chart(
    fig_risk,
    use_container_width=True
)

# --------------------------------------------------
# DOWNLOAD RISK DATA
# --------------------------------------------------

risk_download = risk_df[
    [
        "CustomerId",
        "Surname",
        "Geography",
        "Age",
        "Balance",
        "NumOfProducts",
        "IsActiveMember",
        "RetentionRiskScore",
        "RiskCategory",
        "HighValueCustomer",
        "RetentionPriority",
        "Exited"
    ]
].copy()

st.download_button(
    label="📥 Download Customer Risk Analysis",
    data=risk_download.to_csv(index=False),
    file_name="customer_retention_risk_analysis.csv",
    mime="text/csv"
)

# --------------------------------------------------
# RELATIONSHIP STRENGTH ANALYSIS
# --------------------------------------------------


st.markdown(
    '<div class="section-title">🤝 Customer Relationship Strength</div>',
    unsafe_allow_html=True
)


# Calculate Relationship Strength Score
rsi_df = relationship_strength_index(
    filtered_df
)

# --------------------------------------------------
# RELATIONSHIP STRENGTH SUMMARY
# --------------------------------------------------

strong_count = (
    rsi_df["RelationshipStrengthCategory"]
    == "Strong"
).sum()

moderate_count = (
    rsi_df["RelationshipStrengthCategory"]
    == "Moderate"
).sum()

weak_count = (
    rsi_df["RelationshipStrengthCategory"]
    == "Weak"
).sum()


r1, r2, r3 = st.columns(3)

r1.metric(
    "🟢 Strong Relationships",
    f"{strong_count:,}"
)

r2.metric(
    "🟡 Moderate Relationships",
    f"{moderate_count:,}"
)

r3.metric(
    "🔴 Weak Relationships",
    f"{weak_count:,}"
)

# --------------------------------------------------
# RSI DISTRIBUTION
# --------------------------------------------------
relationship_col1, relationship_col2 = st.columns(2)

relationship_distribution = (
    rsi_df["RelationshipStrengthCategory"]
    .value_counts()
    .reset_index()
)

relationship_distribution.columns = [
    "RelationshipStrengthCategory",
    "CustomerCount"
]


fig_relationship = px.bar(
    relationship_distribution,
    x="RelationshipStrengthCategory",
    y="CustomerCount",
    text="CustomerCount",

    labels={
        "RelationshipStrengthCategory":
            "Relationship Strength",
        "CustomerCount":
            "Number of Customers"
    }
)

fig_relationship.update_traces(
    textposition="outside"
)

fig_relationship = style_chart(fig_relationship)

fig_relationship.update_traces(
    marker_color="#3b82f6"
)

with relationship_col1:

    st.markdown(
        """
        <div class="chart-card-title">
            👥 Relationship Distribution
        </div>
        """,
        unsafe_allow_html=True
    )

    st.plotly_chart(
        fig_relationship,
        use_container_width=True
    )

# --------------------------------------------------
# RELATIONSHIP STRENGTH VS CHURN
# --------------------------------------------------

relationship_churn = (
    rsi_df
    .groupby(
        "RelationshipStrengthCategory",
        observed=True
    )["Exited"]
    .agg(
        CustomerCount="count",
        ChurnRate="mean"
    )
    .reset_index()
)

relationship_churn["ChurnRate"] = (
    relationship_churn["ChurnRate"] * 100
)


fig_relationship_churn = px.bar(
    relationship_churn,
    x="RelationshipStrengthCategory",
    y="ChurnRate",
    text="ChurnRate",
    labels={
        "RelationshipStrengthCategory":
            "Relationship Strength",
        "ChurnRate":
            "Historical Churn Rate (%)"
    }
)

fig_relationship_churn.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig_relationship_churn = style_chart(
    fig_relationship_churn
)

fig_relationship_churn.update_traces(
    marker_color="#3b82f6"
)

with relationship_col2:

    st.markdown(
        """
        <div class="chart-card-title">
            📉 Churn by Relationship Strength
        </div>
        """,
        unsafe_allow_html=True
    )

    st.plotly_chart(
        fig_relationship_churn,
        use_container_width=True
    )

st.info(
    """
    **💡 Business Interpretation:**

    The Relationship Strength Index combines customer
    engagement, product depth, credit card ownership,
    tenure and balance into an analyst-developed
    relationship score.

    Higher scores indicate stronger observable
    relationships with the bank and can help prioritize
    retention and engagement strategies.
    """
)

# --------------------------------------------------
# EXECUTIVE INSIGHTS
# --------------------------------------------------

st.markdown(
    '<div class="section-title">💡 Executive Insights</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    ### 📊 Key Findings

    - 👥 The current filtered customer population contains
      **{len(filtered_df):,} customers**.

    - 📉 The historical churn rate for the selected population
      is **{churn_rate:.2f}%**.

    - 🔄 The retention rate is **{retention_rate:.2f}%**.

    - 📊 The Engagement Retention Ratio is **{err:.2f}**,
      comparing retention among active and inactive customers.

    - 📦 The Product Depth Index is **{pdi:.2f}**,
      comparing multi-product and single-product retention.

    - ⚠️ **{len(high_value_disengaged):,}** high-value disengaged
      customers are currently identified under the selected filters.

    ### 🎯 Recommended Focus

    Prioritize customers who combine high financial value
    with low engagement, especially those classified into
    higher retention-priority segments.
    """
)

st.divider()

st.caption(
    "Customer Retention Analytics | Banking Customer Engagement & Retention Project"
)

st.caption(
    "Analytical indices and retention scores are analyst-developed "
    "for project-based customer segmentation and prioritization."
)