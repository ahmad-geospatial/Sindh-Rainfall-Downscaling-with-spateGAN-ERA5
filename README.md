# Exploring rainfall downscaling over Sindh

This project evaluates the pretrained **spateGAN-ERA5** model over Sindh,
Pakistan. It uses hourly ERA5 precipitation to generate 2 km, 10-minute
rainfall fields, then compares those estimates with ERA5 and available
NOAA GHCN-Daily station observations.

The fine-scale fields are model-generated estimates, not measurements of
rainfall observed at 2 km or 10-minute resolution. The project is assessing
whether they add useful information for future flood modeling; the current
validation does not establish that they are ready for operational use.

## Research question

How well does the pretrained spateGAN-ERA5 workflow represent rainfall over
Sindh, and does its downscaled output improve agreement with available
rain-gauge observations compared with ERA5?

## Current status

- Retrieved and combined the 12 monthly ERA5 files into a 2010 dataset with
  8,760 hourly records.
- Ran the pretrained model month by month in Google Colab for a domain
  centered near 26.5°N, 68.5°E.
- Repaired and audited the monthly output boundaries. The full-year output
  contains 52,560 ten-minute timestamps with no missing or infinite
  precipitation values.
- Compared ERA5 and spateGAN daily precipitation with 2010 NOAA GHCN-Daily
  observations at stations inside the model domain.
- Found no consistent improvement from spateGAN in the station comparisons.
  Further evaluation is needed before considering these estimates for a
  flood model.

## Data and outputs

The input ERA5 dataset contains hourly convective precipitation (`cp`) and
large-scale precipitation (`lsp`) over the study region. The pretrained model
produces precipitation estimates on a 144 × 144 grid with 2 km spacing,
covering approximately 288 × 288 km. The output has six time steps per hour
and precipitation units of `mm/h`.

Raw data, station files, and generated NetCDF outputs are kept outside this
repository and are not committed to GitHub. The local `data/` directory is
excluded by `.gitignore`. ERA5 data can be obtained from the Copernicus
Climate Data Store, and station data from NOAA GHCN-Daily. Users need to
obtain the required input data and model weights separately.

The full-year monthly ERA5 and repaired spateGAN outputs are stored in Google
Drive under `Sindh_Rainfall_Colab/full_2010/` and
`Sindh_Rainfall_Colab/full_2010_repaired/`, respectively.

## Processing and comparison

The full year was processed in monthly batches in Google Colab. Monthly
processing and boundary repair used neighboring ERA5 context so that the
repaired files form a continuous year.

For station validation, the six ten-minute precipitation-rate values in an
hour were averaged to obtain the hourly rate, then accumulated into daily
totals using UTC ending-day convention. The final daily period, December 31,
is excluded because the available files do not include the January 1, 2011
00:00 UTC hour needed to complete that period.

A separate same-footprint comparison found that the domain-average hourly
total matches ERA5 (prediction-to-ERA5 total ratio = 1.000). This is a
consistency check associated with the model's ERA5 constraint; it is not
independent evidence that the fine-scale rainfall pattern is accurate.

## Station validation

Five NOAA GHCN-Daily stations were examined. Three lie inside the
spateGAN domain: Nawabshah, Hyderabad Airport, and Chhor. Shahbaz AB and
Jinnah International are outside the downscaling domain, so only ERA5 results
are reported for those stations.

Metrics below use paired daily observations. Bias is model minus station
rainfall. Wet-day detection uses a threshold of at least 1 mm/day.
POD is probability of detection; FAR is false-alarm ratio.

| Station | Product | Paired days | Bias (mm/day) | MAE (mm/day) | RMSE (mm/day) | Correlation | POD | FAR |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Shahbaz AB | ERA5 | 300 | 0.22 | 1.36 | 6.97 | 0.320 | 0.400 | 0.700 |
| Nawabshah | ERA5 | 340 | -0.44 | 1.27 | 6.51 | 0.302 | 0.600 | 0.609 |
| Nawabshah | spateGAN | 340 | -0.31 | 1.42 | 6.78 | 0.298 | 0.600 | 0.640 |
| Hyderabad Airport | ERA5 | 332 | 0.05 | 1.31 | 6.94 | 0.163 | 0.812 | 0.606 |
| Hyderabad Airport | spateGAN | 332 | 0.21 | 1.33 | 6.93 | 0.268 | 0.500 | 0.692 |
| Chhor | ERA5 | 340 | -0.08 | 1.29 | 6.04 | 0.197 | 0.750 | 0.500 |
| Chhor | spateGAN | 340 | -0.05 | 1.34 | 5.91 | 0.239 | 0.600 | 0.684 |
| Jinnah International | ERA5 | 346 | -0.49 | 1.20 | 5.74 | 0.630 | 0.550 | 0.645 |

At Hyderabad Airport and Chhor, spateGAN has higher correlation than ERA5.
However, its MAE is slightly higher at all three in-domain stations, and its
wet-day detection is weaker at Hyderabad Airport and Chhor. These results do
not show a consistent station-level improvement.

## Limitations

- The model was pretrained using high-resolution radar observations in
  Germany. Its performance over Sindh cannot be assumed to be the same.
- Only three stations fall inside the downscaling domain, and station
  observations are daily. They cannot verify 10-minute rainfall timing or
  2 km rainfall structure.
- The evaluation covers one year and has gaps in station observations.
- Matching domain-average totals to ERA5 does not validate the location or
  intensity of downscaled storms.
- The current station results do not justify using spateGAN rainfall as a
  flood-model input without further validation.

## Next steps

1. Compare daily CHIRPS estimates with the same station observations using
   matched dates, locations, and metrics.
2. Examine major 2010 rainfall events separately, including event totals and
   timing at available stations.
3. Assess whether additional independent observations are available for
   validating storm timing and spatial patterns.
4. Consider flood-model use only after the rainfall inputs pass suitable
   hydrologic and event-based validation.

CHIRPS is planned as an additional comparison product. It is not a direct
replacement input for the pretrained spateGAN-ERA5 workflow, which expects
hourly ERA5 precipitation inputs.

## Repository layout

- `src/` — scripts for ERA5 preparation, station-data processing, and
  comparisons.
- `docs/methodology.md` — project design and evaluation approach.
- `data/` — local data directory; excluded from GitHub.
- `notebooks/` — Colab notebooks can be exported here to preserve the
  interactive analysis workflow.

## References

- Glawion et al. (2025), [Global spatio-temporal ERA5 precipitation
  downscaling to km and sub-hourly scale using generative AI]
  (https://doi.org/10.1038/s41612-025-01103-y).
- Authors' implementation: [LGlawion/spateGAN_ERA5]
  (https://github.com/LGlawion/spateGAN_ERA5). Cite the paper and attribute
  the code when using it.
- NOAA NCEI, [Global Historical Climatology Network Daily (GHCN-Daily)]
  (https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily).
- NASA GPM, [IMERG product overview](https://gpm.nasa.gov/data/imerg).