import pandas as pd


def engagement_retention_ratio(df):

    active_churn = (
        df.loc[df["IsActiveMember"] == 1, "Exited"]
        .mean()
    )

    inactive_churn = (
        df.loc[df["IsActiveMember"] == 0, "Exited"]
        .mean()
    )

    active_retention = 1 - active_churn
    inactive_retention = 1 - inactive_churn

    if inactive_retention == 0:
        return 0

    return active_retention / inactive_retention


def product_depth_index(df):

    single_product = df["NumOfProducts"] == 1
    multi_product = df["NumOfProducts"] >= 2

    single_churn = df.loc[single_product, "Exited"].mean()
    multi_churn = df.loc[multi_product, "Exited"].mean()

    single_retention = 1 - single_churn
    multi_retention = 1 - multi_churn

    if single_retention == 0:
        return 0

    return multi_retention / single_retention


def high_balance_disengagement_rate(df, percentile=75):

    threshold = df["Balance"].quantile(percentile / 100)

    high_balance = df["Balance"] >= threshold

    high_balance_customers = df.loc[high_balance]

    if len(high_balance_customers) == 0:
        return 0

    inactive_high_balance = (
        high_balance_customers["IsActiveMember"] == 0
    ).sum()

    return (
        inactive_high_balance /
        len(high_balance_customers)
    ) * 100


def credit_card_stickiness_score(df):

    card = df["HasCrCard"] == 1
    no_card = df["HasCrCard"] == 0

    card_churn = df.loc[card, "Exited"].mean()
    no_card_churn = df.loc[no_card, "Exited"].mean()

    card_retention = 1 - card_churn
    no_card_retention = 1 - no_card_churn

    if no_card_retention == 0:
        return 0

    return card_retention / no_card_retention


def relationship_strength_index(df):

    result = df.copy()

    result["RelationshipStrengthScore"] = 0

    # Active member = 2 points
    result["RelationshipStrengthScore"] += (
        result["IsActiveMember"] == 1
    ).astype(int) * 2

    # Multiple products = 2 points
    result["RelationshipStrengthScore"] += (
        result["NumOfProducts"] >= 2
    ).astype(int) * 2

    # Credit card = 1 point
    result["RelationshipStrengthScore"] += (
        result["HasCrCard"] == 1
    ).astype(int)

    # Tenure >= 5 years = 1 point
    result["RelationshipStrengthScore"] += (
        result["Tenure"] >= 5
    ).astype(int)

    # High balance = 1 point
    balance_threshold = result["Balance"].quantile(0.75)

    result["RelationshipStrengthScore"] += (
        result["Balance"] >= balance_threshold
    ).astype(int)

    # Category
    result["RelationshipStrengthCategory"] = pd.cut(
        result["RelationshipStrengthScore"],
        bins=[-1, 2, 4, 7],
        labels=[
            "Weak",
            "Moderate",
            "Strong"
        ]
    )

    return result