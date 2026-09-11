import os
from urllib.parse import urlencode

from dotenv import load_dotenv

load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_REDIRECT_URI = os.getenv("TWITCH_REDIRECT_URI")

TWITCH_AUTH_URL = "https://id.twitch.tv/oauth2/authorize"
TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"


def create_twitch_authorization_url(state: str) -> str:
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "redirect_uri": TWITCH_REDIRECT_URI,
        "response_type": "code",
        "scope": "user:read:email",
        "state": state,
    }

    return f"{TWITCH_AUTH_URL}?{urlencode(params)}"
@router.get("/twitch/connect")
def connect_twitch(
    database: Session = Depends(get_database),
    current_user=Depends(get_current_user)
):
    state = secrets.token_urlsafe(32)

    oauth_state = OAuthState(
        state=state,
        user_id=current_user.id,
        platform="twitch",
        code_verifier=None,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )

    database.add(oauth_state)
    database.commit()

    auth_url = create_twitch_authorization_url(state)

    return RedirectResponse(auth_url)