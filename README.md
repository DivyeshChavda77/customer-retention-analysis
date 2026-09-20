# Customer Engagement & Product Utilization Analytics for Retention Strategy

## Project Overview

This project analyzes banking customer data to understand
historical customer churn and identify potential customer
retention opportunities.

The project focuses on customer engagement, product utilization,
financial value, relationship strength and retention risk.

An interactive Streamlit dashboard was developed to help users
explore customer segments and prioritize potential retention
actions.

---

## Business Problem

Banking institutions need to identify customers who may require
greater retention attention.

The main business question addressed by this project is:

> Which customers are more likely to represent higher retention
> risk, how are engagement and product utilization related to
> historical churn, and which high-value disengaged customers
> should receive greater retention attention?

---

## Objectives

- Analyze customer engagement and historical churn.
- Analyze product utilization and customer retention.
- Identify high-value disengaged customers.
- Develop customer retention KPIs.
- Develop a rule-based retention risk scoring framework.
- Analyze relationship strength.
- Build an interactive Streamlit dashboard.
- Recommend targeted retention strategies.

---

## Dataset

The dataset contains:

- 10,000 customer records
- 14 original attributes
- Customer demographic information
- Financial information
- Product information
- Customer engagement information
- Historical churn outcome

The target variable is `Exited`.

Where:

- `Exited = 0` → Retained customer
- `Exited = 1` → Churned customer

---

## Data Quality

During data validation:

- Missing values: 0
- Duplicate records: 0

The `Year` column contained a constant value and was excluded
from customer-level analytical interpretation.

---

## Key Features Created

The following analytical features were created:

- `EngagementStatus`
- `ProductCategory`
- `CreditCardStatus`
- `ChurnStatus`
- `BalanceSalaryRatio`
- `AgeGroup`
- `CreditScoreGroup`

---

## Key KPIs

The project developed the following KPIs:

### 1. Engagement Retention Ratio

Compares retention among active and inactive customers.

### 2. Product Depth Index

Compares retention among multi-product and single-product
customers.

### 3. High-Balance Disengagement Rate

Measures the percentage of high-balance customers who are inactive.

### 4. Credit Card Stickiness Score

Compares retention among credit-card and non-credit-card customers.

### 5. Relationship Strength Index

An analyst-developed composite score based on:

- Customer engagement
- Product depth
- Credit card ownership
- Tenure
- Balance

---

## Retention Risk Scoring

A rule-based Retention Risk Score was developed using observable
customer characteristics.

Scoring factors include:

- Inactive customer
- Single product
- High balance + inactive
- Age 45–64
- Germany geography

Risk categories:

- Low Risk
- Medium Risk
- High Risk

A separate retention priority classification identifies:

- Normal
- Medium
- High
- Critical

---

## Key Findings

- Overall historical churn rate: 20.37%
- Overall retention rate: 79.63%
- Active customer churn: 14.27%
- Inactive customer churn: 26.85%
- Germany churn: 32.44%
- One-product customer churn: 27.71%
- Two-product customer churn: 7.58%
- High-Balance Disengagement Rate: 49.88%

Customers aged 45–64 also showed substantially higher
historical churn rates.

---

## Dashboard

The Streamlit dashboard provides:

- Executive retention KPIs
- Interactive filters
- Engagement vs churn analysis
- Product utilization analysis
- Product + engagement heatmap
- High-value disengaged customer detector
- Retention risk distribution
- Relationship strength analysis
- Customer-level retention priority
- CSV download functionality

---

## Project Structure

```text
Customer-Retention-Analytics/
│
├── data/
│   ├── European_Bank.csv
│   └── cleaned_bank_customer.csv
│
├── notebooks/
│   └── customer_retention_eda.ipynb
│
├── src/
│   ├── data_cleaning.py
│   ├── analysis.py
│   ├── kpi.py
│   └── scoring.py
│
├── dashboard/
│   └── app.py
│   └── style.css
│
├── outputs/
│   ├── charts/
│   └── tables/
│
├── report/
│   ├── project_report.docx
│
├── .gitignore
├── requirements.txt
├── README.md
└── .venv/