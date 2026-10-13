# Exploring rainfall downscaling over Sindh

Rainfall products give us useful estimates, but they often smooth out the local and short-lived structure of intense storms. This project asks whether a published generative model can add plausible fine-scale detail to hourly ERA5 rainfall over Sindh, Pakistan, and what we can responsibly learn from the result.

The work is a hands-on application of the pretrained **spateGAN-ERA5** model. It is also a learning project: the repository will show how the data are prepared, how the model is run, how comparisons are made, and where the evidence runs out. The generated 2 km, 10-minute fields are model realizations, not measurements of rainfall that was observed at that scale.

## The question

Can the released spateGAN-ERA5 workflow produce useful, physically plausible rainfall detail for Sindh when driven by ERA5, and how do those outputs compare with observations and other precipitation products at scales those datasets can actually support?

We will first reproduce the authors' radar-based example. Then we will try the workflow over Sindh and compare aggregated results with ERA5, NASA IMERG, and any suitable daily rain gauges we can identify.

## What makes this project useful

- It follows a published, reproducible workflow instead of presenting a new model as a discovery.
- It separates reproducing the original benchmark from applying the model in a new region.
- It checks comparisons at compatible time and space scales.
- It documents the practical lessons: data access, units, model setup, compute needs, and the limits of available observations.

## Current status

**Planning and repository setup.** No Sindh model outputs or validation results have been produced yet. The first data task is to inspect NOAA's GHCN-Daily station inventory and see whether any stations in or near Sindh have usable precipitation records for the periods we select.

As work progresses, this section will summarize completed milestones and the most important project findings. Results will be reported only after the corresponding code and comparisons are in the repository.

## How the project will proceed

1. Reproduce the published radar example and understand its inputs, outputs, and evaluation.
2. Choose a study boundary and event period for Sindh.
3. Check rainfall station coverage and prepare the required ERA5 input data.
4. Run the released pretrained model and retain its multiple possible rainfall realizations.
5. Compare at matched scales: aggregate the output for ERA5 and IMERG comparisons, and compare daily totals with eligible gauges.
6. Summarize what worked, what did not, and what the available evidence supports.

The full comparison strategy and its limits are described in [Method and evaluation](docs/methodology.md).

## What the comparisons can tell us

| Comparison | Useful for | Does not establish |
|---|---|---|
| Authors' radar example | Whether our reproduction follows the published evaluation workflow | Accuracy over Sindh |
| Output aggregated to ERA5 scale | Whether the generated fields remain consistent with the broad input event | Whether the fine-scale pattern is correct |
| IMERG at matched time and grid scales | How the results compare with another precipitation estimate | Independent ground truth or 2 km accuracy |
| NOAA GHCN-Daily, if suitable stations exist | Daily rainfall agreement at available station locations | Storm timing, 10-minute intensity, or 2 km rainfall structure |

A comparison is only as strong as its observations. In particular, daily gauges cannot verify 10-minute rainfall, and satellite products are estimates rather than ground truth.

## Learning path

The repository is intended to be followed in order. Each notebook and script will explain the decisions being made, not just provide code to run.

- `notebooks/` — guided walkthroughs and exploratory analysis
- `src/` — reusable data preparation and evaluation code
- `data/` — local input and derived data; large or restricted files are not committed
- `docs/methodology.md` — project design and interpretation guide
- `tests/` — checks for reusable code as it is added

## Limitations to keep in view

The pretrained model was developed using high-resolution radar observations in Germany. That does not establish that it performs equally well in Sindh, where rainfall regimes, terrain, and observation coverage differ. Without local high-resolution observations, we cannot verify the generated 2 km patterns or 10-minute storm structure. Model ensemble spread and data limitations will be reported alongside any results.

## References

- Glawion et al. (2025), [Global spatio-temporal ERA5 precipitation downscaling to km and sub-hourly scale using generative AI](https://doi.org/10.1038/s41612-025-01103-y).
- Authors' implementation: [LGlawion/spateGAN_ERA5](https://github.com/LGlawion/spateGAN_ERA5). Cite the paper and attribute the code when using it.
- NOAA NCEI, [Global Historical Climatology Network Daily (GHCN-Daily)](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily).
- NASA GPM, [IMERG product overview](https://gpm.nasa.gov/data/imerg).
