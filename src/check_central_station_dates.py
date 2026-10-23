from pathlib import Path

import pandas as pd


project = Path(__file__).resolve().parents[1]
stations_file = project / "data" / "processed" / "sindh_daily_prcp.csv"

station_ids = [
    "PKM00041749",  # Nawabshah
    "PKM00041764",  # Hyderabad Airport
    "PKM00041768",  # Chhor
]

df = pd.read_csv(stations_file)
df["date"] = pd.to_datetime(df["date"])
df["prcp_mm"] = pd.to_numeric(df["prcp_mm"], errors="coerce")

df = df[
    (df["date"].dt.year == 2010)
    & (df["station_id"].isin(station_ids))
]

print("Valid reporting days per station:")
print(df.groupby("station_id")["prcp_mm"].count().to_string())

daily = df.pivot_table(
    index="date",
    columns="station_id",
    values="prcp_mm",
    aggfunc="first",
)

complete = daily.dropna(subset=station_ids)

print(f"\nDays when all three stations reported: {len(complete)}")

dry = complete[(complete[station_ids] == 0).all(axis=1)]
print(f"Days when all three recorded zero: {len(dry)}")

wet = complete[(complete[station_ids] > 0).any(axis=1)].copy()
wet["stations_with_rain"] = (wet[station_ids] > 0).sum(axis=1)
wet["total_observed_mm"] = wet[station_ids].sum(axis=1)

print("\nExamples of wet dates when all three reported:")
print(
    wet.sort_values("total_observed_mm", ascending=False)
    .head(15)
    .to_string()
)