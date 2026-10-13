# Data dictionary — Telco churn (teaching copy)

**Source.** Based on the public IBM "Telco Customer Churn" sample dataset. This teaching copy was prepared by Evolution.inc for the Infinity Labs pre-training. It contains a few deliberate data problems for you to find.

**What a row is.** One row per customer account, taken from a single snapshot of the customer base. The file has no dates.

**The label.** `Churn`: whether the customer left within the month before the snapshot (`Yes` / `No`).

| Column | Meaning | Values |
|---|---|---|
| `customerID` | Customer account identifier | text |
| `gender` | Customer's gender | Female, Male |
| `SeniorCitizen` | Customer is 65 or older | 0, 1 |
| `Partner` | Customer has a partner | Yes, No |
| `Dependents` | Customer has dependents | Yes, No |
| `tenure` | Months the customer has been with the company | 0–72 |
| `PhoneService` | Has a phone line | Yes, No |
| `MultipleLines` | Has more than one phone line | Yes, No, No phone service |
| `InternetService` | Type of internet service | DSL, Fiber optic, No |
| `OnlineSecurity` | Online security add-on | Yes, No, No internet service |
| `OnlineBackup` | Online backup add-on | Yes, No, No internet service |
| `DeviceProtection` | Device protection add-on | Yes, No, No internet service |
| `TechSupport` | Technical support add-on | Yes, No, No internet service |
| `StreamingTV` | TV streaming add-on | Yes, No, No internet service |
| `StreamingMovies` | Movie streaming add-on | Yes, No, No internet service |
| `Contract` | Contract term | Month-to-month, One year, Two year |
| `PaperlessBilling` | Receives paperless bills | Yes, No |
| `PaymentMethod` | How the customer pays | Electronic check, Mailed check, Bank transfer (automatic), Credit card (automatic) |
| `MonthlyCharges` | Current monthly charge | amount |
| `TotalCharges` | Total amount charged to date | amount |
| `LastContactReason` | Reason for the customer's most recent contact with the call centre | Cancellation request, Billing question, Technical issue, Plan change, No contact |
| `Churn` | **Label.** Left within the month before the snapshot | Yes, No |
