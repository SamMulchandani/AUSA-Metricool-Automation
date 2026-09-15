from datetime import timedelta
from datetime import datetime

from spotify_token_manager import *
from date_range import get_previous_month_date_range, get_fiscal_year_range
import requests

def get_monthly_spotify_metrics():

    entity_type = "AD_ACCOUNT"
    granularity = "LIFETIME"
    report_start, report_end = f"{get_previous_month_date_range()[0][:10]}T00%3A00%3A00Z", f"{get_previous_month_date_range()[1][:10]}T00%3A00%3A00Z"
    # report_start, report_end = f"2026-08-01T00%3A00%3A00Z", f"2026-08-31T00%3A00%3A00Z"
    # report_start, report_end = f"{get_date_range()[0][:10]}T00%3A00%3A00Z", f"2026-08-31T00%3A00%3A00Z"
    fields = ["IMPRESSIONS", "CLICKS", "SPEND", "REACH", "CTR", "LISTENERS", "CONVERSION_RATE", "NEW_LISTENER_CONVERSION_RATE", "STREAMS", "NEW_LISTENER_STREAMS", "NEW_LISTENERS"]

    fields_str = ""
    for field in fields:
        fields_str += f"&fields={field}"

    url = f"https://api-partner.spotify.com/ads/v3/ad_accounts/93123185-b327-438d-8d3b-757a91f798f4/aggregate_reports?entity_type={entity_type}{fields_str}&report_start={report_start}&report_end={report_end}&granularity={granularity}"
    # url = f"https://api-partner.spotify.com/ads/v3/ad_accounts/93123185-b327-438d-8d3b-757a91f798f4/aggregate_reports?entity_type={entity_type}{fields_str}&report_start={report_start}&granularity={granularity}"

    token = get_valid_access_token()

    response = requests.get(url=url, headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        data = response.json()

    # print(data.get("rows"))
    stats = data.get("rows")

    fixed = {}
    for diction in stats[0].get("stats"):
        key = diction.get("field_type")
        value = diction.get("field_value")
        fixed[key] = value


    fixed["COST_PER_NEW_LISTENER"] = fixed["SPEND"] / fixed["NEW_LISTENERS"] if fixed["NEW_LISTENERS"] != 0 else 0
    fixed["COST_PER_STREAM"] = fixed["SPEND"] / fixed["STREAMS"] if fixed["STREAMS"] != 0 else 0

    return fixed

FIELDS = [
    "IMPRESSIONS", "CLICKS", "SPEND", "REACH", "CTR", "LISTENERS",
    "CONVERSION_RATE", "NEW_LISTENER_CONVERSION_RATE", "STREAMS",
    "NEW_LISTENER_STREAMS", "NEW_LISTENERS",
]

# Safe to sum directly across chunks — these are plain counts.
ADDITIVE_FIELDS = {
    "IMPRESSIONS", "CLICKS", "SPEND", "STREAMS",
    "NEW_LISTENER_STREAMS", "NEW_LISTENERS",
}

# Deduplicated/unique counts — summing across chunks overcounts
# anyone reached in more than one window.
DEDUP_FIELDS = {"REACH", "LISTENERS"}


def _chunk_date_ranges(start: datetime, end: datetime, max_days: int = 90):
    current = start
    while current < end:
        chunk_end = min(current + timedelta(days=max_days), end)
        yield current, chunk_end
        current = chunk_end



def _fetch_chunk(report_start: str, report_end: str, token: str):
    fields_str = "".join(f"&fields={f}" for f in FIELDS)
    url = (
        f"https://api-partner.spotify.com/ads/v3/ad_accounts/93123185-b327-438d-8d3b-757a91f798f4"
        f"/aggregate_reports?entity_type=AD_ACCOUNT{fields_str}"
        f"&report_start={report_start}&report_end={report_end}"
        f"&granularity=LIFETIME"
    )
    response = requests.get(url=url, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        print(f"Chunk {report_start} -> {report_end} failed: "
              f"{response.status_code} {response.text}")
        return {}

    rows = response.json().get("rows") or []
    if not rows:
        return {}

    return {
        entry.get("field_type"): entry.get("field_value")
        for entry in rows[0].get("stats", [])
    }



def get_all_time_spotify_metrics():
    token = get_valid_access_token()

    start = datetime.strptime(get_fiscal_year_range()[0], "%Y-%m-%dT00%%3A00%%3A00Z")
    end = datetime.strptime(get_fiscal_year_range()[1], "%Y-%m-%dT00%%3A00%%3A00Z")
    # start = datetime.strptime("2026-07-01T00%3A00%3A00Z", "%Y-%m-%dT00%%3A00%%3A00Z")
    # end = datetime.strptime("2026-T00%3A00%3A00Z", "%Y-%m-%dT00%%3A00%%3A00Z")
    
    totals = {field: 0 for field in ADDITIVE_FIELDS}
    dedup_sums = {field: 0 for field in DEDUP_FIELDS}

    for chunk_start, chunk_end in _chunk_date_ranges(start, end, max_days=89):
        report_start = chunk_start.strftime("%Y-%m-%dT00%%3A00%%3A00Z")
        report_end = chunk_end.strftime("%Y-%m-%dT00%%3A00%%3A00Z")

        stats = _fetch_chunk(report_start, report_end, token)

        for field in ADDITIVE_FIELDS:
            totals[field] += stats.get(field, 0) or 0
        for field in DEDUP_FIELDS:
            dedup_sums[field] += stats.get(field, 0) or 0

    # Recompute the one rate metric with a well-known definition from the
    # true summed counts (don't sum/average the per-chunk CTR values directly).
    totals["CTR"] = (
        totals["CLICKS"] / totals["IMPRESSIONS"] if totals["IMPRESSIONS"] else 0
    )

    totals["COST_PER_NEW_LISTENER"] = (
        totals["SPEND"] / totals["NEW_LISTENERS"] if totals["NEW_LISTENERS"] else 0
    )
    totals["COST_PER_STREAM"] = (
        totals["SPEND"] / totals["STREAMS"] if totals["STREAMS"] else 0
    )

    # Upper-bound only — true yearly-unique REACH/LISTENERS isn't obtainable
    # from 90-day sub-windows since Spotify doesn't expose a >90-day dedup total.
    totals["REACH_approx_upper_bound"] = dedup_sums["REACH"]
    totals["LISTENERS_approx_upper_bound"] = dedup_sums["LISTENERS"]
    totals["CTR"] = totals["CLICKS"] / totals["IMPRESSIONS"] if totals["IMPRESSIONS"] else 0
    totals["CONVERSION_RATE"] = totals["STREAMS"] / totals["CLICKS"] if totals["CLICKS"] else 0
    totals["COST_PER_CLICK"] = totals["SPEND"] / totals["CLICKS"] if totals["CLICKS"] else 0
    totals["COST_PER_STREAM"] = totals["SPEND"] / totals["STREAMS"] if totals["STREAMS"] else 0
    totals["COST_PER_NEW_LISTENER"] = (
        totals["SPEND"] / totals["NEW_LISTENERS"] if totals["NEW_LISTENERS"] else 0
    )
    # totals["NEW_LISTENER_CONVERSION_RATE"] = (
    #     totals["NEW_LISTENER_STREAMS"] / totals["CLICKS"] if totals["CLICKS"] else 0
    # )

    return totals


if __name__ == "__main__":
    print(json.dumps(get_all_time_spotify_metrics(),indent=2))
