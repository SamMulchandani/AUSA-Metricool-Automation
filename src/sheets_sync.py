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
from date_range import get_date_range

# toggle between these two to switch between local and cloud run
from google.oauth2.service_account import Credentials
# from google.oauth2.credentials import Credentials

from spotify_metrics import get_monthly_spotify_metrics, get_all_time_spotify_metrics


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

    # toggle between these two to switch between local and cloud run
    creds, _ = google.auth.default(scopes=SCOPES)
    # creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return gspread.authorize(creds)


def get_looker_sheet():
    SPREADSHEET_ID = "10_pz7I2u27s-eTKsatJDAbuZ6QnEpJTF9ZPAq2vk_EA"
    WORKSHEET_NAME = "Looker Source"
    sh = get_client_adc().open_by_key(SPREADSHEET_ID)
    try:
        ws = sh.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=WORKSHEET_NAME, rows=20, cols=6)

    return ws

def get_paid_ads_fiscal_sheet():
    SPREADSHEET_ID = "10_pz7I2u27s-eTKsatJDAbuZ6QnEpJTF9ZPAq2vk_EA"
    WORKSHEET_NAME = "Paid Ads Fiscal Year"
    sh = get_client_adc().open_by_key(SPREADSHEET_ID)
    try:
        ws = sh.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=WORKSHEET_NAME, rows=20, cols=6)

    return ws


def clear_bottom_row(ws):
    """Clear only the final non-empty row in a worksheet."""
    values = ws.get_all_values()
    if not values:
        return

    last_row = len(values)
    last_col = max(len(row) for row in values)
    if last_col == 0:
        return

    end_cell = gspread.utils.rowcol_to_a1(last_row, last_col)
    ws.update(f"A{last_row}:{end_cell}", [[""] * last_col])


def write_summary(spreadsheet_id, worksheet_name, month_label, platform_rows, client, youtube_shorts=None):
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
        urls_val1 = row["top_two_impression_urls"][0] if len(row["top_two_impression_urls"]) > 0 and row["top_two_impression_urls"] is not None and row["top_two_impression_urls"][0] is not None else "NA"
        urls_val2 = row["top_two_impression_urls"][1] if len(row["top_two_impression_urls"]) > 1 and row["top_two_impression_urls"] is not None and row["top_two_impression_urls"][1] is not None else "NA"
        rows.append([row["platform"], reach_val, row["impressions"], row["interactions"], row["likes"], row["comments"], row["shares"], clicks_val, reactions_val, time_watched_val, urls_val1, urls_val2, row["total_posts"]])
    ws.update("A4", rows)


    # Spotify column labels
    ws.update("A10", [["", "CTR", "Clicks", "Reach", "Impressions", "Listeners", "New Listeners", "Streams", "New Listener Streams", "Cost Per Stream", "Cost Per New Listener", "Spend", "New Listener Conversion Rate"]])
    spotify = get_monthly_spotify_metrics()
    spotify_row = ["Spotify", spotify["CTR"], spotify["CLICKS"], spotify["REACH"], spotify["IMPRESSIONS"], spotify["LISTENERS"], spotify["NEW_LISTENERS"], spotify["STREAMS"], spotify["NEW_LISTENER_STREAMS"], spotify["COST_PER_STREAM"], spotify["COST_PER_NEW_LISTENER"], spotify["SPEND"], spotify["NEW_LISTENER_CONVERSION_RATE"]]
    # "IMPRESSIONS", "CLICKS", "SPEND", "REACH", "CPM", "CTR", "LISTENERS", "CONVERSION_RATE", "NEW_LISTENER_CONVERSION_RATE", "STREAMS", "NEW_LISTENER_STREAMS", "NEW_LISTENERS", "AVG_STREAMS_PER_LISTENER"
    ws.update("A11", [spotify_row])

    # Youtube Shorts
    ws.update("A14", [["Youtube Shorts Performance"]])
    ws.update("A15", [["Video", "Video Views", "Avg. View Duration"]])
    # each short listed here with their views and avg view duration
    # 
    if youtube_shorts:
        averageWatchTime = 0
        for short in youtube_shorts:
            averageWatchTime += short.get("averageViewDuration")
        averageWatchTime /= len(youtube_shorts)

        shorts_rows = [
            [
                short.get("title") or short.get("watchUrl", "NA"),
                short.get("views", "NA"),
                short.get("averageViewDuration", "NA"),
            ]
            for short in youtube_shorts
        ]
        shorts_rows.append(["", "", averageWatchTime])
        ws.update("A15", shorts_rows)
    else:
        ws.update("A15", [["No Shorts published this period", "", ""]]) 

    # Looker sheet append
    looker_date_label = get_date_range()[0][:10]
    looker_list = [looker_date_label]
    for row in rows:
        # 1 -> 10
        for i in range(1, 10):
            if row[i] != "NA":
                looker_list.append(row[i])
    for i in range(1,len(spotify_row)):
        looker_list.append(spotify_row[i])

    print(looker_list)
    looker_sheet = get_looker_sheet()
    looker_sheet.append_row(looker_list)

    # Paid ads append
    fiscal_sheet = get_paid_ads_fiscal_sheet()

    # 
    monthly_row = [month_label, spotify["CTR"], spotify["CLICKS"], spotify["REACH"], spotify["IMPRESSIONS"], spotify["LISTENERS"], spotify["NEW_LISTENERS"], spotify["STREAMS"], spotify["NEW_LISTENER_STREAMS"], spotify["COST_PER_STREAM"], spotify["COST_PER_NEW_LISTENER"], spotify["SPEND"], spotify["NEW_LISTENER_CONVERSION_RATE"]]

    totals = get_all_time_spotify_metrics()
    totals_row = ["TOTAL", totals["CTR"], totals["CLICKS"], totals["REACH_approx_upper_bound"], totals["IMPRESSIONS"], totals["LISTENERS_approx_upper_bound"], totals["NEW_LISTENERS"], totals["STREAMS"], totals["NEW_LISTENER_STREAMS"], totals["COST_PER_STREAM"], totals["COST_PER_NEW_LISTENER"], totals["SPEND"], "NA"]

    clear_bottom_row(fiscal_sheet)
    fiscal_sheet.append_row(monthly_row)
    fiscal_sheet.append_row(totals_row)
    
