import json
import time
import requests
from google.cloud import secretmanager

PROJECT_ID = "ausa-data-automation-506918"
SECRET_ID = "SPOTIFY_ADS_TOKEN"
TOKEN_URL = "https://accounts.spotify.com/api/token"

EXPIRY_BUFFER_SECONDS = 60

_client = secretmanager.SecretManagerServiceClient()

def _cleanup_old_versions(keep_latest: int = 3):
    """
    Destroys all ENABLED versions of SECRET_ID except the `keep_latest` most recent.
    Already-destroyed versions are skipped automatically.
    """
    parent = f"projects/{PROJECT_ID}/secrets/{SECRET_ID}"

    versions = list(_client.list_secret_versions(request={"parent": parent}))

    # list_secret_versions returns newest-first by default, but don't rely on that —
    # sort explicitly by version number (name ends in .../versions/<N>)
    versions.sort(key=lambda v: int(v.name.split("/")[-1]), reverse=True)

    enabled_versions = [
        v for v in versions
        if v.state == secretmanager.SecretVersion.State.ENABLED
    ]

    to_destroy = enabled_versions[keep_latest:]

    for v in to_destroy:
        print(f"Destroying old version: {v.name}")
        _client.destroy_secret_version(request={"name": v.name})


def _get_secret(secret_path: str) -> str:
    response = _client.access_secret_version(request={"name": secret_path})
    return response.payload.data.decode("UTF-8")


# Base64(client_id:client_secret) for the Basic auth header, per Spotify's spec
BASE64_OUTPUT = _get_secret(
    "projects/42769899857/secrets/SPOTIFY_ADS_BASE_64_OUTPUT/versions/latest"
)


def _secret_name(version="latest"):
    return f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/{version}"


def _read_token_data() -> dict:
    payload = _get_secret(_secret_name())
    return json.loads(payload)


def _write_token_data(data: dict):
    payload = json.dumps(data).encode("UTF-8")
    parent = f"projects/{PROJECT_ID}/secrets/{SECRET_ID}"
    _client.add_secret_version(
        request={"parent": parent, "payload": {"data": payload}}
    )
    _cleanup_old_versions(keep_latest=3)


def _refresh_access_token(refresh_token: str) -> dict:
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        headers={"Authorization": f"Basic {BASE64_OUTPUT}"},
    )
    resp.raise_for_status()
    token_response = resp.json()

    new_data = {
        "access_token": token_response["access_token"],
        "expires_at": time.time() + token_response["expires_in"],
        "refresh_token": token_response.get("refresh_token", refresh_token),
    }
    return new_data


def get_valid_access_token() -> str:
    data = _read_token_data()

    if time.time() < (data["expires_at"] - EXPIRY_BUFFER_SECONDS):
        return data["access_token"]

    # print("fetching new token...")
    new_data = _refresh_access_token(data["refresh_token"])
    _write_token_data(new_data)
    return new_data["access_token"]


if __name__ == "__main__":
    token = get_valid_access_token()
    print(token)