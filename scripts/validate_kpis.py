import pandas as pd
import os
import sys

PROC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

PASS = "PASS"
FAIL = "FAIL"


def check(name, condition):
    status = PASS if condition else FAIL
    print(f"  [{status}] {name}")
    return condition


def validate_trip_kpis():
    df = pd.read_csv(os.path.join(PROC_DIR, "trip_kpis.csv"))
    ok = True
    ok &= check("trip_kpis has rows", len(df) > 0)
    ok &= check("no null trip_ids", df["trip_id"].notna().all())
    ok &= check("on_time is 0 or 1", df["on_time"].isin([0, 1]).all())
    ok &= check("breached is 0 or 1", df["breached"].isin([0, 1]).all())
    ok &= check("delay_mins >= -5 (reasonable)", (df["delay_mins"] >= -5).all())
    ok &= check("on_time + breached covers all rows",
                 ((df["on_time"] + df["breached"]) >= 1).all())
    return ok


def validate_zone_monthly():
    df = pd.read_csv(os.path.join(PROC_DIR, "zone_monthly_summary.csv"))
    ok = True
    ok &= check("zone_monthly has rows", len(df) > 0)
    ok &= check("punctuality_pct between 0 and 100",
                 df["punctuality_pct"].between(0, 100).all())
    ok &= check("breach_pct between 0 and 100",
                 df["breach_pct"].between(0, 100).all())
    ok &= check("on_time + breach <= total",
                 (df["on_time_trips"] + df["breached_trips"] <= df["total_trips"] * 2).all())
    return ok


def validate_zone_ranking():
    df = pd.read_csv(os.path.join(PROC_DIR, "zone_ranking.csv"))
    ok = True
    ok &= check("zone_ranking has rows", len(df) > 0)
    ok &= check("ranks are sequential", list(df["rank"]) == list(range(1, len(df) + 1)))
    ok &= check("punctuality descending",
                 df["punctuality_pct"].is_monotonic_decreasing)
    return ok


def validate_complaints():
    df = pd.read_csv(os.path.join(PROC_DIR, "complaint_summary.csv"))
    ok = True
    ok &= check("complaint_summary has rows", len(df) > 0)
    ok &= check("sla_met_pct between 0 and 100",
                 df["sla_met_pct"].between(0, 100).all())
    ok &= check("avg_resolution_days > 0",
                 (df["avg_resolution_days"] > 0).all())
    return ok


def main():
    print("Validating KPIs...")
    all_ok = True
    all_ok &= validate_trip_kpis()
    all_ok &= validate_zone_monthly()
    all_ok &= validate_zone_ranking()
    all_ok &= validate_complaints()

    print()
    if all_ok:
        print("All validations passed.")
    else:
        print("Some validations failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
