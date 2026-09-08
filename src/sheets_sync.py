# sheets_sync.py
#
# Writes the monthly platform summary table to a Google Sheet.
#
# Uses a SERVICE ACCOUNT rather than the InstalledAppFlow browser login
# in sheets_quickstart.py, because a Cloud Run job has no browser and
# no user sitting in front of it to click "Allow".
#
# One-time setup:
#   1. In GCP Console -> IAM & Admin -> Service Accounts, create one
#      (or reuse the one your Cloud Run job already runs as).
#   2. Enable the Google Sheets API for the project.
#   3. Open your target spreadsheet, click Share, and share it with
#      the service account's email address (looks like
#      xxxx@your-project.iam.gserviceaccount.com) as Editor.
#   4. Either:
#        a) download a JSON key for the service account and mount it
#           into Cloud Run as a secret file, then set
#           GOOGLE_APPLICATION_CREDENTIALS or pass the path in below, or
#        b) if Cloud Run is already running AS that service account
#           (recommended — no key file to manage), use
#           google.auth.default() instead. See get_client_adc() below.
#
# pip install gspread google-auth

import gspread
from google.oauth2.service_account import Credentials
from spotify_metrics import get_spotify_metrics

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


# def get_client(service_account_file):
#     """Auth via a downloaded service-account JSON key file."""
#     creds = Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
#     return gspread.authorize(creds)


def get_client_adc():
    """
    Auth via Application Default Credentials — use this if the Cloud
    Run job's runtime service account already has edit access to the
    sheet. No key file needed; nothing to leak or rotate.
    """
    import google.auth

    creds, _ = google.auth.default(scopes=SCOPES)
    return gspread.authorize(creds)


def write_summary(spreadsheet_id, worksheet_name, month_label, platform_rows, client):
    """
    platform_rows: list of dicts in display order, e.g.
        [
            {"platform": "LinkedIn",  "reach": None, "impressions": 9282, "total_posts": 9},
            {"platform": "Facebook",  "reach": None, "impressions": 8151, "total_posts": 8},
            {"platform": "Instagram", "reach": 6426, "impressions": 8259, "total_posts": 8},
        ]
    `reach: None` renders as "NA" (matches the sheet in the screenshot for
    platforms/posts where Metricool doesn't report reach).
    """
    sh = client.open_by_key(spreadsheet_id)
    try:
        ws = sh.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet_name, rows=20, cols=6)

    ws.clear()
    ws.update("A1", [[f"Organic Social Media Performance — {month_label}"]])
    ws.update("A3", [["Platform", "Reach", "Impressions/Views", "Interactions","Likes", "Comments", "Shares", "Clicks", "Reactions", "Average Video Watch Time", "Top Post by Impressions", "Second Post by Impressions", "Total Posts"]])

    rows = []
    for row in platform_rows:
        reach_val = row["reach"] if row["reach"] is not None else "NA"
        clicks_val = row["clicks"] if row["clicks"] is not None else "NA"
        reactions_val = row["reactions"] if row["reactions"] is not None else "NA"
        time_watched_val = row["average_time_watched_for_video_views"] if row["average_time_watched_for_video_views"] is not None else "NA"
        urls_val1 = row["top_two_impression_urls"][0] if row["top_two_impression_urls"] is not None and row["top_two_impression_urls"][0] is not None else "NA"
        urls_val2 = row["top_two_impression_urls"][1] if row["top_two_impression_urls"] is not None and row["top_two_impression_urls"][1] is not None else "NA"
        rows.append([row["platform"], reach_val, row["impressions"], row["interactions"], row["likes"], row["comments"], row["shares"], clicks_val, reactions_val, time_watched_val, urls_val1, urls_val2, row["total_posts"]])
    ws.update("A4", rows)

    # Spotify column labels
    ws.update("A9", [["", "CTR", "Clicks", "Reach", "Impressions", "New Listeners", "Cost Per New Listener", "Streams", "Cost Per Stream", "Spend"]])
    spotify = get_spotify_metrics()
    ws.update("A10", [["Spotify", spotify["CTR"], spotify["CLICKS"], spotify["REACH"], spotify["IMPRESSIONS"], spotify["NEW_LISTENERS"], spotify["COST_PER_NEW_LISTENER"], spotify["STREAMS"], spotify["COST_PER_STREAM"], spotify["SPEND"]]])
