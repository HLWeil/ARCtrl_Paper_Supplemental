"""Fetch download statistics of ARCtrl from npm, PyPI and NuGet.

Writes one tidy CSV per registry plus a combined file to repository_usage/data/:
    date, registry, package, downloads, cumulative

Sources:
- npm:   api.npmjs.org daily download ranges (full history)
- NuGet: nugettrends.com weekly cumulative totals (nuget.org itself has no history)
- PyPI:  Google BigQuery public dataset `bigquery-public-data.pypi.file_downloads`,
         either queried directly (needs `google-cloud-bigquery` and a GCP project)
         or read from a CSV exported from the BigQuery console
         (columns: day, downloads, downloads_no_mirrors)

Usage:
    python repository_usage/fetch.py --gcp-project my-project
    python repository_usage/fetch.py --pypi-csv bigquery_export.csv
"""

import argparse
import csv
import json
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

NPM_PACKAGE = "@nfdi4plants/arctrl"
PYPI_PACKAGE = "arctrl"
NUGET_PACKAGE = "ARCtrl"

# Earliest dates to query from; slightly before the first publish on each registry.
NPM_START = date(2023, 9, 1)
PYPI_START = date(2024, 3, 1)

DATA_DIR = Path(__file__).parent / "data"
# The *_no_mirrors columns are only filled for PyPI.
FIELDS = ["date", "registry", "package", "downloads", "cumulative", "downloads_no_mirrors", "cumulative_no_mirrors"]

# Installers counted as mirrors, same definition as pypistats.org.
# Like pypistats, downloads without an installer name (mostly bots) are excluded as well.
PYPI_MIRRORS = ["bandersnatch", "z3c.pypimirror", "Artifactory", "devpi"]

PYPI_QUERY = """
SELECT
  DATE(timestamp) AS day,
  COUNT(*) AS downloads,
  COUNTIF(details.installer.name IS NOT NULL AND details.installer.name NOT IN UNNEST(@mirrors)) AS downloads_no_mirrors
FROM `bigquery-public-data.pypi.file_downloads`
WHERE file.project = @package
  AND DATE(timestamp) BETWEEN @start AND @end
GROUP BY day
ORDER BY day
"""


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "arctrl-paper-snippets"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def to_rows(registry: str, package: str, daily: list[tuple[date, int]]) -> list[dict]:
    """Turn (date, downloads) pairs into rows with a running total."""
    rows = []
    total = 0
    for day, downloads in sorted(daily):
        total += downloads
        rows.append({
            "date": day.isoformat(),
            "registry": registry,
            "package": package,
            "downloads": downloads,
            "cumulative": total,
        })
    return rows


def to_pypi_rows(daily: list[tuple[date, int, int]]) -> list[dict]:
    """Like to_rows, with an additional running total of non-mirror downloads."""
    rows = to_rows("pypi", PYPI_PACKAGE, [(day, downloads) for day, downloads, _ in daily])
    total = 0
    for row, (_, _, no_mirrors) in zip(rows, sorted(daily)):
        total += no_mirrors
        row["downloads_no_mirrors"] = no_mirrors
        row["cumulative_no_mirrors"] = total
    return rows


def fetch_npm(end: date) -> list[dict]:
    # The npm API limits a single range request to 18 months, so query in yearly chunks.
    daily = []
    chunk_start = NPM_START
    while chunk_start <= end:
        chunk_end = min(chunk_start + timedelta(days=364), end)
        url = f"https://api.npmjs.org/downloads/range/{chunk_start}:{chunk_end}/{NPM_PACKAGE}"
        for entry in get_json(url)["downloads"]:
            daily.append((date.fromisoformat(entry["day"]), entry["downloads"]))
        chunk_start = chunk_end + timedelta(days=1)
    return to_rows("npm", NPM_PACKAGE, daily)


def fetch_nuget() -> list[dict]:
    # NuGet Trends reports the cumulative total at the start of each week.
    url = f"https://nugettrends.com/api/package/history/{NUGET_PACKAGE}?months=120"
    rows = []
    previous = 0
    for entry in get_json(url)["downloads"]:
        if entry["count"] is None:  # weeks without a snapshot
            continue
        rows.append({
            "date": entry["week"][:10],
            "registry": "nuget",
            "package": NUGET_PACKAGE,
            "downloads": entry["count"] - previous,
            "cumulative": entry["count"],
        })
        previous = entry["count"]
    return rows


def fetch_pypi_bigquery(project: str, end: date) -> list[dict]:
    from google.cloud import bigquery

    client = bigquery.Client(project=project)
    config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("package", "STRING", PYPI_PACKAGE),
        bigquery.ScalarQueryParameter("start", "DATE", PYPI_START),
        bigquery.ScalarQueryParameter("end", "DATE", end),
        bigquery.ArrayQueryParameter("mirrors", "STRING", PYPI_MIRRORS),
    ])
    result = client.query(PYPI_QUERY, job_config=config).result()
    return to_pypi_rows([(row.day, row.downloads, row.downloads_no_mirrors) for row in result])


def read_pypi_csv(path: Path) -> list[dict]:
    with path.open(newline="") as file:
        daily = [
            (date.fromisoformat(row["day"]), int(row["downloads"]), int(row["downloads_no_mirrors"]))
            for row in csv.DictReader(file)
        ]
    return to_pypi_rows(daily)


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    pypi = parser.add_mutually_exclusive_group()
    pypi.add_argument("--gcp-project", help="GCP project used to query the PyPI BigQuery dataset")
    pypi.add_argument("--pypi-csv", type=Path, help="CSV exported from BigQuery with columns day, downloads, downloads_no_mirrors")
    args = parser.parse_args()

    # Stop two days back, npm and BigQuery lag up to a day behind and would report zeros.
    end = date.today() - timedelta(days=2)
    DATA_DIR.mkdir(exist_ok=True)

    results = {
        "npm": fetch_npm(end),
        "nuget": fetch_nuget(),
    }
    if args.gcp_project:
        results["pypi"] = fetch_pypi_bigquery(args.gcp_project, end)
    elif args.pypi_csv:
        results["pypi"] = read_pypi_csv(args.pypi_csv)
    else:
        print("skipping PyPI: pass --gcp-project or --pypi-csv (see --help)", file=sys.stderr)

    for registry, rows in results.items():
        write_csv(DATA_DIR / f"{registry}.csv", rows)
    write_csv(DATA_DIR / "downloads.csv", [row for rows in results.values() for row in rows])
    (DATA_DIR / "retrieved.txt").write_text(f"{date.today().isoformat()}\n")


if __name__ == "__main__":
    main()
