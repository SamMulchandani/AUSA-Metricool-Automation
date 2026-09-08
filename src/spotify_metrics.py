from spotify_token_manager import *
from network_find_funcs import get_date_range
import requests

def get_spotify_metrics():

    payload = """
    {
      "continuation_token": "",
      "report_start": "2026-07-01T00:00:00Z",
      "report_end": "2026-07-31T00:00:00Z",
      "granularity": "LIFETIME",
      "rows": [
        {
          "entity_type": "AD_ACCOUNT",
          "entity_id": "93123185-b327-438d-8d3b-757a91f798f4",
          "entity_name": "Association of the United States Army - Podcast",
          "entity_status": null,
          "parent_entity": null,
          "start_time": null,
          "end_time": null,
          "stats": [
            {
              "field_type": "IMPRESSIONS",
              "field_value": 73775.0
            },
            {
              "field_type": "CLICKS",
              "field_value": 474.0
            },
            {
              "field_type": "CLICKS",
              "field_value": 474.0
            },
            {
              "field_type": "SPEND",
              "field_value": 456.0
            },
            {
              "field_type": "REACH",
              "field_value": 53919.0
            },
            {
              "field_type": "CTR",
              "field_value": 0.6424
            },
            {
              "field_type": "STREAMS",
              "field_value": 47.0
            },
            {
              "field_type": "COST_PER_LEAD",
              "field_value": -5.0
            },
            {
              "field_type": "STREAMS_PER_NEW_LISTENER",
              "field_value": 1.516129
            },
            {
              "field_type": "NEW_LISTENERS",
              "field_value": 31.0
            },
            {
              "field_type": "COMPLETION_RATE",
              "field_value": 0.0
            }
          ]
        }
      ],
      "warnings": null
    }
    """

    entity_type = "AD_ACCOUNT"
    granularity = "LIFETIME"
    report_start, report_end = f"{get_date_range()[0][:10]}T00%3A00%3A00Z", f"{get_date_range()[1][:10]}T00%3A00%3A00Z"
    fields = ["IMPRESSIONS", "CLICKS", "SPEND", "REACH", "CTR", "STREAMS", "STREAMS_PER_NEW_LISTENER", "NEW_LISTENERS", "COMPLETION_RATE"]

    fields_str = ""
    for field in fields:
        fields_str += f"&fields={field}"

    url = f"https://api-partner.spotify.com/ads/v3/ad_accounts/93123185-b327-438d-8d3b-757a91f798f4/aggregate_reports?entity_type={entity_type}{fields_str}&report_start={report_start}&report_end={report_end}&granularity={granularity}"

    token = get_valid_access_token()

    response = requests.get(url=url, headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        data = response.json()

    stats = data.get("rows")[0].get("stats")

    fixed = {}
    for diction in stats:
        key = diction.get("field_type")
        value = diction.get("field_value")
        fixed[key] = value

    fixed["COST_PER_NEW_LISTENER"] = fixed["SPEND"] / fixed["NEW_LISTENERS"]
    fixed["COST_PER_STREAM"] = fixed["SPEND"] / fixed["STREAMS"]

    return fixed


# print(json.dumps(get_spotify_metrics(), indent=2))
