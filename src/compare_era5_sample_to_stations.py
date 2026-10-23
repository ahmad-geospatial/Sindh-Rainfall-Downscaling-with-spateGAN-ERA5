from pathlib import Path

import pandas as pd
import xarray as xr


project = Path(__file__).resolve().parents[1]
era5_file = project / "data" / "raw" / "era5" / "era5_sindh_sample_2010-08-01.nc"
stations_file = project / "data" / "processed" / "sindh_daily_prcp.csv"
date = "2010-08-01"

stations = pd.read_csv(stations_file)
stations = stations[stations["date"] == date].copy()

with xr.open_dataset(era5_file, engine="h5netcdf") as ds:
    day = ds.sel(valid_time=date)

    rows = []
    for _, station in stations.iterrows():
        cell = day.sel(
            latitude=station["latitude"],
            longitude=station["longitude"],
            method="nearest",
        )

        # ERA5 cp and lsp are precipitation amounts in metres.
        era5_mm = float((cell["cp"] + cell["lsp"]).sum().values) * 1000

        rows.append({
            "station_id": station["station_id"],
            "station_name": station["station_name"],
            "date": date,
            "observed_mm": station["prcp_mm"],
            "era5_nearest_grid_mm": round(era5_mm, 3),
        })

print(pd.DataFrame(rows).to_string(index=False))