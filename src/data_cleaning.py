import pandas as pd
import numpy as np

def clean_customer_data(df):
    """
    Clean and prepare the bank customer dataset.
    """
    # Create a copy so the original dataframe is not modified
    df_clean = df.copy()

    # Create engagement status
    df_clean["EngagementStatus"] = df_clean["IsActiveMember"].map({
        1: "Active",
        0: "Inactive"
    })

    # Create product category
    df_clean["ProductCategory"] = np.where(
        df_clean["NumOfProducts"] == 1,
        "Single Product",
        "Multi Product"
    )

    # Create credit card status
    df_clean["CreditCardStatus"] = df_clean["HasCrCard"].map({
        1: "Has Credit Card",
        0: "No Credit Card"
    })

    # Create churn status
    df_clean["ChurnStatus"] = df_clean["Exited"].map({
        1: "Churned",
        0: "Retained"
    })

    # Create balance-to-salary ratio
    df_clean["BalanceSalaryRatio"] = np.where(
        df_clean["EstimatedSalary"] > 0,
        df_clean["Balance"] / df_clean["EstimatedSalary"],
        np.nan
    )

    # Create age groups
    age_bins = [18, 25, 35, 45, 55, 65, 101]

    age_labels = [
        "18-24",
        "25-34",
        "35-44",
        "45-54",
        "55-64",
        "65+"
    ]

    df_clean["AgeGroup"] = pd.cut(
        df_clean["Age"],
        bins=age_bins,
        labels=age_labels,
        right=False
    )

    # Create credit score groups
    credit_bins = [0, 500, 600, 700, 800, 1001]

    credit_labels = [
        "<500",
        "500-599",
        "600-699",
        "700-799",
        "800+"
    ]

    df_clean["CreditScoreGroup"] = pd.cut(
        df_clean["CreditScore"],
        bins=credit_bins,
        labels=credit_labels,
        right=False
    )
    return df_clean