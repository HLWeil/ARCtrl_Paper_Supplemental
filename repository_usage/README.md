# Repository usage

Download statistics of ARCtrl from the three package registries it is published to, used for the cumulative download figure in the paper.

| Registry | Package | Source | Resolution |
|---|---|---|---|
| npm | `@nfdi4plants/arctrl` | [npm downloads API](https://github.com/npm/registry/blob/main/docs/download-counts.md) | daily |
| PyPI | `arctrl` | [Google BigQuery public dataset](https://docs.pypi.org/api/bigquery/) `bigquery-public-data.pypi.file_downloads` | daily |
| NuGet | `ARCtrl` | [NuGet Trends](https://nugettrends.com/packages?ids=ARCtrl) | weekly |

Only the top-level NuGet package `ARCtrl` is used. The sub-packages (`ARCtrl.Core`, `ARCtrl.Json`, ...) are pulled in as its dependencies, so adding them up would count the same install several times.

## Usage

```powershell
.venv\Scripts\python.exe repository_usage\fetch.py --gcp-project <gcp-project-id>
```

npm and NuGet need no setup. PyPI needs:

1. `uv pip install google-cloud-bigquery`
2. The [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) and `gcloud auth application-default login`
3. A GCP project with the BigQuery API enabled. If the login uses a different default project, set it with `gcloud auth application-default set-quota-project <gcp-project-id>`.

The query scans a few GB and stays within the BigQuery free tier.

Without GCP access, run the query in `fetch.py` (`PYPI_QUERY`) in the BigQuery console, export the result as CSV and pass it with `--pypi-csv <file>`.

The data ends two days before the run, since npm and BigQuery lag up to a day behind.

## Output

`data/npm.csv`, `data/pypi.csv`, `data/nuget.csv` and all of them combined in `data/downloads.csv`, with the columns:

| Column | Description |
|---|---|
| `date` | day (npm, PyPI) or start of the week (NuGet) |
| `registry` | `npm`, `pypi` or `nuget` |
| `package` | package name on the registry |
| `downloads` | downloads in that day or week |
| `cumulative` | running total of `downloads` |
| `downloads_no_mirrors` | PyPI only: downloads without mirror and bot traffic |
| `cumulative_no_mirrors` | PyPI only: running total of `downloads_no_mirrors` |

`data/retrieved.txt` holds the date the data was fetched.

## Comparing the registries

Raw download counts are not directly comparable between registries. All of them include CI runs, mirrors and bots to a different degree.

- **PyPI** is the only registry where this traffic can be filtered out. The `*_no_mirrors` columns follow the definition of [pypistats.org](https://pypistats.org): downloads by the mirror tools `bandersnatch`, `z3c.pypimirror`, `Artifactory` and `devpi`, and downloads without an installer name, are excluded. The numbers match pypistats.org day by day. About two thirds of all PyPI downloads of `arctrl` are filtered out this way.
- **npm** only publishes daily totals, with no information on which tool made a download.
- **NuGet** only offers a breakdown by client for the [last 6 weeks](https://www.nuget.org/stats/packages/ARCtrl?groupby=ClientName). In October 2026 about 63% of `ARCtrl` downloads came from NuGet clients (package restores), the rest from browsers, scripts, crawlers and unknown clients. No history of this breakdown is kept.
