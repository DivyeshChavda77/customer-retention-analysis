import pandas as pd


def calculate_overall_churn(df):
    """
    Calculate overall customer churn statistics.
    """

    total_customers = len(df)
    churned_customers = df["Exited"].sum()
    retained_customers = total_customers - churned_customers

    churn_rate = (churned_customers / total_customers) * 100
    retention_rate = (retained_customers / total_customers) * 100

    return {
        "total_customers": total_customers,
        "churned_customers": int(churned_customers),
        "retained_customers": int(retained_customers),
        "churn_rate": churn_rate,
        "retention_rate": retention_rate
    }


def churn_by_category(df, column):
    """
    Calculate customer count and churn rate for a categorical column.
    """

    result = (
        df.groupby(column)["Exited"]
        .agg(["count", "sum", "mean"])
        .reset_index()
    )

    result.rename(
        columns={
            "count": "CustomerCount",
            "sum": "ChurnedCustomers",
            "mean": "ChurnRate"
        },
        inplace=True
    )

    result["ChurnRate"] = result["ChurnRate"] * 100

    return result


def churn_by_geography(df):
    """
    Calculate churn statistics by geography.
    """

    return churn_by_category(df, "Geography")


def churn_by_gender(df):
    """
    Calculate churn statistics by gender.
    """

    return churn_by_category(df, "Gender")


def churn_by_engagement(df):
    """
    Calculate churn statistics by customer engagement.
    """

    return churn_by_category(df, "EngagementStatus")


def churn_by_product_count(df):
    """
    Calculate churn statistics by number of products.
    """

    return churn_by_category(df, "NumOfProducts")


def churn_by_product_category(df):
    """
    Calculate churn statistics for single-product
    versus multi-product customers.
    """

    return churn_by_category(df, "ProductCategory")


def churn_by_credit_card(df):
    """
    Calculate churn statistics by credit-card ownership.
    """

    return churn_by_category(df, "CreditCardStatus")


def churn_by_age_group(df):
    """
    Calculate churn statistics by age group.
    """

    return churn_by_category(df, "AgeGroup")


def churn_by_credit_score_group(df):
    """
    Calculate churn statistics by credit-score group.
    """

    return churn_by_category(df, "CreditScoreGroup")


def churn_by_tenure(df):
    """
    Calculate churn statistics by customer tenure.
    """

    return churn_by_category(df, "Tenure")


def high_value_disengaged_customers(df, percentile=75):
    """
    Identify high-balance and inactive customers.
    High balance is defined using the specified percentile.
    """

    balance_threshold = df["Balance"].quantile(percentile / 100)

    customers = df[
        (df["Balance"] >= balance_threshold) &
        (df["IsActiveMember"] == 0)
    ].copy()

    return customers, balance_threshold


def high_value_disengaged_summary(df, percentile=75):
    """
    Summarize high-value disengaged customers.
    """

    customers, threshold = high_value_disengaged_customers(
        df,
        percentile
    )

    customer_count = len(customers)

    if customer_count > 0:
        churn_rate = customers["Exited"].mean() * 100
    else:
        churn_rate = 0

    return {
        "balance_threshold": threshold,
        "customer_count": customer_count,
        "churn_rate": churn_rate
    }


def product_engagement_churn(df):
    """
    Calculate churn rate by product category and engagement status.
    """

    result = pd.crosstab(
        df["ProductCategory"],
        df["EngagementStatus"],
        values=df["Exited"],
        aggfunc="mean"
    ) * 100

    return result


def balance_summary_by_churn(df):
    """
    Compare balance statistics between retained and churned customers.
    """

    return (
        df.groupby("ChurnStatus")["Balance"]
        .agg(["count", "mean", "median", "min", "max"])
        .round(2)
    )


def salary_summary_by_churn(df):
    """
    Compare salary statistics between retained and churned customers.
    """

    return (
        df.groupby("ChurnStatus")["EstimatedSalary"]
        .agg(["count", "mean", "median", "min", "max"])
        .round(2)
    )