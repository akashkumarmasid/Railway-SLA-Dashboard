import csv
import random
import os
from datetime import datetime, timedelta

SEED = 42
random.seed(SEED)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

ZONES = {
    "NR": ["Delhi", "Ambala", "Lucknow", "Moradabad"],
    "SR": ["Chennai", "Trivandrum", "Madurai", "Salem"],
    "ER": ["Howrah", "Sealdah", "Asansol", "Malda"],
    "WR": ["Mumbai Central", "Ahmedabad", "Rajkot", "Vadodara"],
    "CR": ["CSMT Mumbai", "Pune", "Nagpur", "Bhusawal"],
    "SER": ["Garden Reach", "Ranchi", "Chakradharpur", "Kharagpur"],
    "SCR": ["Secunderabad", "Hyderabad", "Vijayawada", "Guntur"],
    "NER": ["Gorakhpur", "Varanasi", "Lucknow NER", "Izzatnagar"],
}

TRAIN_TYPES = ["Rajdhani", "Shatabdi", "Mail/Express", "Superfast", "Passenger"]

TYPE_WEIGHTS = [0.08, 0.07, 0.45, 0.25, 0.15]

SLA_THRESHOLDS_MINS = {
    "Rajdhani": 10,
    "Shatabdi": 10,
    "Mail/Express": 15,
    "Superfast": 15,
    "Passenger": 20,
}

COMPLAINT_CATEGORIES = [
    "Cleanliness", "Catering", "Punctuality", "Staff Behavior",
    "Coach Maintenance", "Water Availability", "Security",
]

DATE_START = datetime(2024, 1, 1)
DATE_END = datetime(2025, 12, 31)
NUM_TRAINS = 150
TRIPS_PER_TRAIN_PER_MONTH = 26
NUM_COMPLAINTS = 3000


def random_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def generate_trains():
    trains = []
    for i in range(1, NUM_TRAINS + 1):
        zone = random.choice(list(ZONES.keys()))
        division = random.choice(ZONES[zone])
        train_type = random.choices(TRAIN_TYPES, weights=TYPE_WEIGHTS, k=1)[0]
        origin, destination = random.sample(
            [s for stations in ZONES.values() for s in stations], 2
        )
        trains.append({
            "train_id": f"T{i:04d}",
            "train_name": f"{origin}-{destination} {train_type}",
            "train_type": train_type,
            "zone": zone,
            "division": division,
            "origin": origin,
            "destination": destination,
            "scheduled_duration_mins": random.choice([180, 240, 360, 480, 600, 720]),
        })
    return trains


def generate_trips(trains):
    trips = []
    trip_id = 1
    months = []
    d = DATE_START
    while d <= DATE_END:
        months.append(d)
        if d.month == 12:
            d = d.replace(year=d.year + 1, month=1)
        else:
            d = d.replace(month=d.month + 1)

    for train in trains:
        threshold = SLA_THRESHOLDS_MINS[train["train_type"]]
        for month_start in months:
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
            month_end = min(month_end, DATE_END)

            for _ in range(TRIPS_PER_TRAIN_PER_MONTH):
                trip_date = random_date(month_start, month_end)
                sched_dep_hour = random.randint(4, 22)
                sched_dep = trip_date.replace(hour=sched_dep_hour, minute=random.randint(0, 59))

                delay_mins = _sample_delay(train["train_type"])
                actual_dep = sched_dep + timedelta(minutes=max(0, delay_mins * 0.3))

                sched_arr = sched_dep + timedelta(minutes=train["scheduled_duration_mins"])
                actual_arr = sched_arr + timedelta(minutes=delay_mins)

                trips.append({
                    "trip_id": f"TR{trip_id:07d}",
                    "train_id": train["train_id"],
                    "trip_date": trip_date.strftime("%Y-%m-%d"),
                    "scheduled_departure": sched_dep.strftime("%Y-%m-%d %H:%M"),
                    "actual_departure": actual_dep.strftime("%Y-%m-%d %H:%M"),
                    "scheduled_arrival": sched_arr.strftime("%Y-%m-%d %H:%M"),
                    "actual_arrival": actual_arr.strftime("%Y-%m-%d %H:%M"),
                    "delay_mins": round(delay_mins, 1),
                    "sla_threshold_mins": threshold,
                    "breached": 1 if delay_mins > threshold else 0,
                })
                trip_id += 1
    return trips


def _sample_delay(train_type):
    if train_type in ("Rajdhani", "Shatabdi"):
        if random.random() < 0.78:
            return random.uniform(-2, 8)
        return random.uniform(8, 60)
    elif train_type == "Superfast":
        if random.random() < 0.70:
            return random.uniform(-2, 12)
        return random.uniform(12, 90)
    else:
        if random.random() < 0.60:
            return random.uniform(-2, 15)
        return random.uniform(15, 120)


def generate_complaints(trains):
    complaints = []
    for i in range(1, NUM_COMPLAINTS + 1):
        train = random.choice(trains)
        filed = random_date(DATE_START, DATE_END)
        sla_days = random.choice([3, 5, 7, 10])
        resolved_in = random.randint(1, sla_days + 5)
        resolved = filed + timedelta(days=resolved_in)

        complaints.append({
            "complaint_id": f"C{i:05d}",
            "train_id": train["train_id"],
            "zone": train["zone"],
            "category": random.choice(COMPLAINT_CATEGORIES),
            "filed_date": filed.strftime("%Y-%m-%d"),
            "resolved_date": resolved.strftime("%Y-%m-%d"),
            "sla_target_days": sla_days,
            "resolved_in_days": resolved_in,
            "met_sla": 1 if resolved_in <= sla_days else 0,
        })
    return complaints


def write_csv(filename, rows):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {filename}: {len(rows)} rows")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Generating raw data...")

    trains = generate_trains()
    write_csv("trains.csv", trains)

    trips = generate_trips(trains)
    write_csv("trips.csv", trips)

    complaints = generate_complaints(trains)
    write_csv("complaints.csv", complaints)

    print("Done.")


if __name__ == "__main__":
    main()
