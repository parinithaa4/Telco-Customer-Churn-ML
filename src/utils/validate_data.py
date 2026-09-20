from typing import List, Tuple
import great_expectations as ge
import pandas as pd


def validate_telco_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    print("🔍 Starting data validation with Great Expectations...")

    df = df.copy()

    # Required columns check
    required_columns = [
        "customerID",
        "gender",
        "Partner",
        "Dependents",
        "PhoneService",
        "InternetService",
        "Contract",
        "tenure",
        "MonthlyCharges",
        "TotalCharges",
    ]

    failed = []
    for column in required_columns:
        if column not in df.columns:
            failed.append(f"Missing column: {column}")

    if failed:
        print(f"❌ Validation failed: {failed}")
        return False, failed

    # Coerce blank strings " " in TotalCharges to NaN so numeric comparison works
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    # Wrap dataframe with Great Expectations (0.18.x syntax)
    ge_df = ge.from_pandas(df)

    # List of expectation calls
    checks = [
        # Null checks
        ("customerID null check", lambda: ge_df.expect_column_values_to_not_be_null("customerID")),
        ("tenure null check", lambda: ge_df.expect_column_values_to_not_be_null("tenure")),
        ("MonthlyCharges null check", lambda: ge_df.expect_column_values_to_not_be_null("MonthlyCharges")),

        # Categorical set checks
        ("gender in set", lambda: ge_df.expect_column_values_to_be_in_set("gender", ["Male", "Female"])),
        ("Partner in set", lambda: ge_df.expect_column_values_to_be_in_set("Partner", ["Yes", "No"])),
        ("Dependents in set", lambda: ge_df.expect_column_values_to_be_in_set("Dependents", ["Yes", "No"])),
        ("PhoneService in set", lambda: ge_df.expect_column_values_to_be_in_set("PhoneService", ["Yes", "No"])),
        ("Contract in set", lambda: ge_df.expect_column_values_to_be_in_set("Contract", ["Month-to-month", "One year", "Two year"])),
        ("InternetService in set", lambda: ge_df.expect_column_values_to_be_in_set("InternetService", ["DSL", "Fiber optic", "No"])),

        # Range checks
        ("tenure range (0-120)", lambda: ge_df.expect_column_values_to_be_between("tenure", min_value=0, max_value=120)),
        ("MonthlyCharges range (0-200)", lambda: ge_df.expect_column_values_to_be_between("MonthlyCharges", min_value=0, max_value=200)),
        ("TotalCharges range (>=0)", lambda: ge_df.expect_column_values_to_be_between("TotalCharges", min_value=0)),
    ]

    for name, check_fn in checks:
        result = check_fn()
        if not result.success:
            failed.append(name)

    if failed:
        print(f"❌ Data validation FAILED: {failed}")
        return False, failed

    print("✅ Data validation PASSED")
    return True, []