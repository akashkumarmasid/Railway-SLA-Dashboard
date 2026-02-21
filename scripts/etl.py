import pandas as pd
import os

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def load_raw():
    trains = pd.read_csv(os.path.join(RAW_DIR, "trains.csv"))
    trips = pd.read_csv(os.path.join(RAW_DIR, "trips.csv"))
    complaints = pd.read_csv(os.path.join(RAW_DIR, "complaints.csv"))
    return trains, trips, complaints


def enrich_trips(trains, trips):
    df = trips.merge(trains[["train_id", "train_name", "train_type", "zone", "division"]], on="train_id")
    df["trip_date"] = pd.to_datetime(df["trip_date"])
    df["year_month"] = df["trip_date"].dt.to_period("M").astype(str)
    df["on_time"] = (df["delay_mins"] <= df["sla_threshold_mins"]).astype(int)
    return df


def build_trip_kpis(df):
    return df[[
        "trip_id", "train_id", "train_name", "train_type", "zone", "division",
        "trip_date", "year_month", "delay_mins", "sla_threshold_mins",
        "on_time", "breached",
    ]]


def build_zone_monthly_summary(df):
    grouped = df.groupby(["zone", "year_month"]).agg(
        total_trips=("trip_id", "count"),
        on_time_trips=("on_time", "sum"),
        breached_trips=("breached", "sum"),
        avg_delay_mins=("delay_mins", "mean"),
    ).reset_index()

    grouped["punctuality_pct"] = round(grouped["on_time_trips"] / grouped["total_trips"] * 100, 2)
    grouped["breach_pct"] = round(grouped["breached_trips"] / grouped["total_trips"] * 100, 2)
    grouped["avg_delay_mins"] = round(grouped["avg_delay_mins"], 2)
    return grouped


def build_train_summary(df):
    grouped = df.groupby(["train_id", "train_name", "train_type", "zone", "division"]).agg(
        total_trips=("trip_id", "count"),
        on_time_trips=("on_time", "sum"),
        breached_trips=("breached", "sum"),
        avg_delay_mins=("delay_mins", "mean"),
    ).reset_index()

    grouped["punctuality_pct"] = round(grouped["on_time_trips"] / grouped["total_trips"] * 100, 2)
    grouped["breach_pct"] = round(grouped["breached_trips"] / grouped["total_trips"] * 100, 2)
    grouped["avg_delay_mins"] = round(grouped["avg_delay_mins"], 2)
    return grouped


def build_complaint_summary(complaints):
    monthly = complaints.copy()
    monthly["filed_date"] = pd.to_datetime(monthly["filed_date"])
    monthly["year_month"] = monthly["filed_date"].dt.to_period("M").astype(str)

    grouped = monthly.groupby(["zone", "year_month", "category"]).agg(
        total_complaints=("complaint_id", "count"),
        met_sla=("met_sla", "sum"),
        avg_resolution_days=("resolved_in_days", "mean"),
    ).reset_index()

    grouped["sla_met_pct"] = round(grouped["met_sla"] / grouped["total_complaints"] * 100, 2)
    grouped["avg_resolution_days"] = round(grouped["avg_resolution_days"], 2)
    return grouped


def build_zone_ranking(df):
    ranked = df.groupby("zone").agg(
        total_trips=("trip_id", "count"),
        on_time_trips=("on_time", "sum"),
        breached_trips=("breached", "sum"),
        avg_delay_mins=("delay_mins", "mean"),
    ).reset_index()

    ranked["punctuality_pct"] = round(ranked["on_time_trips"] / ranked["total_trips"] * 100, 2)
    ranked["breach_pct"] = round(ranked["breached_trips"] / ranked["total_trips"] * 100, 2)
    ranked["avg_delay_mins"] = round(ranked["avg_delay_mins"], 2)
    ranked = ranked.sort_values("punctuality_pct", ascending=False).reset_index(drop=True)
    ranked["rank"] = ranked.index + 1
    return ranked


def save(df, filename):
    path = os.path.join(OUT_DIR, filename)
    df.to_csv(path, index=False)
    print(f"  {filename}: {len(df)} rows")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Running ETL...")

    trains, trips, complaints = load_raw()
    enriched = enrich_trips(trains, trips)

    save(build_trip_kpis(enriched), "trip_kpis.csv")
    save(build_zone_monthly_summary(enriched), "zone_monthly_summary.csv")
    save(build_train_summary(enriched), "train_summary.csv")
    save(build_complaint_summary(complaints), "complaint_summary.csv")
    save(build_zone_ranking(enriched), "zone_ranking.csv")

    print("Done.")


if __name__ == "__main__":
    main()
