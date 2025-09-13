import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "credentials_from_json.json")

# Only official scopes — remove "profile"
SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email"
]


def create_flow(redirect_uri: str):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    return flow

def get_authorization_url(redirect_uri: str):
    flow = create_flow(redirect_uri)
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',  # lowercase string!
        prompt='consent'
    )
    return auth_url

def exchange_code_for_credentials(redirect_uri: str, code: str):
    try:
        flow = create_flow(redirect_uri)
        flow.fetch_token(code=code)
        creds = flow.credentials
        return {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }
    except Exception as e:
        print("Error fetching token:", e)
        raise

def credentials_from_json(creds_json: dict) -> Credentials:
    return Credentials(
        token=creds_json.get("token"),
        refresh_token=creds_json.get("refresh_token"),
        token_uri=creds_json.get("token_uri"),
        client_id=creds_json.get("client_id"),
        client_secret=creds_json.get("client_secret"),
        scopes=creds_json.get("scopes"),
    )
