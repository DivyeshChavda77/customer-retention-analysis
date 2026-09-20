import pandas as pd


def calculate_retention_risk_score(df, balance_percentile=75):

    result = df.copy()

    # Initialize score
    result["RetentionRiskScore"] = 0

    # ---------------------------------
    # 1. Inactive customer = +3
    # ---------------------------------
    result["RetentionRiskScore"] += (
        result["IsActiveMember"] == 0
    ).astype(int) * 3

    # ---------------------------------
    # 2. Single product = +2
    # ---------------------------------
    result["RetentionRiskScore"] += (
        result["NumOfProducts"] == 1
    ).astype(int) * 2

    # ---------------------------------
    # 3. High balance + inactive = +2
    # ---------------------------------
    balance_threshold = result["Balance"].quantile(
        balance_percentile / 100
    )

    high_balance_inactive = (
        (result["Balance"] >= balance_threshold) &
        (result["IsActiveMember"] == 0)
    )

    result["RetentionRiskScore"] += (
        high_balance_inactive
    ).astype(int) * 2

    # ---------------------------------
    # 4. Age 45-64 = +1
    # ---------------------------------
    age_risk = (
        (result["Age"] >= 45) &
        (result["Age"] < 65)
    )

    result["RetentionRiskScore"] += (
        age_risk
    ).astype(int)

    # ---------------------------------
    # 5. Germany = +1
    # ---------------------------------
    result["RetentionRiskScore"] += (
        result["Geography"] == "Germany"
    ).astype(int)

    # ---------------------------------
    # Risk Category
    # ---------------------------------
    result["RiskCategory"] = pd.cut(
        result["RetentionRiskScore"],
        bins=[-1, 2, 5, 9],
        labels=[
            "Low Risk",
            "Medium Risk",
            "High Risk"
        ]
    )

    # ---------------------------------
    # High-value customer flag
    # ---------------------------------
    result["HighValueCustomer"] = (
        result["Balance"] >= balance_threshold
    )

    # ---------------------------------
    # Priority Segment
    # ---------------------------------

    result["RetentionPriority"] = "Normal"


    # Critical:
    # High-value + inactive + additional risk factor
    critical_condition = (
        (result["HighValueCustomer"] == True) &
        (result["IsActiveMember"] == 0) &
        (
            (result["Age"].between(45, 64)) |
            (result["Geography"] == "Germany")
        )
    )

    result.loc[
        critical_condition,
        "RetentionPriority"
    ] = "Critical"


    # High:
    # High-value + inactive customers
    high_condition = (
        (result["HighValueCustomer"] == True) &
        (result["IsActiveMember"] == 0) &
        (~critical_condition)
    )

    result.loc[
        high_condition,
        "RetentionPriority"
    ] = "High"


    # Medium:
    # Medium risk customers
    medium_condition = (
        (result["RiskCategory"] == "Medium Risk") &
        (result["RetentionPriority"] == "Normal")
    )

    result.loc[
        medium_condition,
        "RetentionPriority"
    ] = "Medium"
    
    return result