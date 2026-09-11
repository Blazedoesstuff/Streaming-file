import os
from urllib.parse import urlencode

from dotenv import load_dotenv

load_dotenv()

FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI")

FACEBOOK_AUTH_URL = "https://www.facebook.com/v23.0/dialog/oauth"
FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v23.0/oauth/access_token"


def create_facebook_authorization_url(state: str) -> str:
    params = {
        "client_id": FACEBOOK_APP_ID,
        "redirect_uri": FACEBOOK_REDIRECT_URI,
        "state": state,
        "response_type": "code",
        "scope": "public_profile,email",
    }

    # routes/connected_accounts.py

    @router.get("/facebook/callback")
    def facebook_callback(
            code: str,
            state: str,
            database: Session = Depends(get_database),
    ):
        # Find OAuthState
        # Exchange code for token
        # Save ConnectedAccount
        # Delete OAuthState
        ...