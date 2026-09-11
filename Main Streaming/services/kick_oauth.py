import base64
import hashlib
import os
import secrets

from dotenv import load_dotenv
from urllib.parse import urlencode


load_dotenv()

KICK_CLIENT_ID = os.getenv("KICK_CLIENT_ID")
KICK_CLIENT_SECRET = os.getenv("KICK_CLIENT_SECRET")

KICK_REDIRECT_URI = os.getenv(
    "KICK_REDIRECT_URI"
)

KICK_AUTH_URL = "https://id.kick.com/oauth/authorize"
KICK_TOKEN_URL = "https://id.kick.com/oauth/token"

KICK_SCOPES = [
    "user:read",
    "channel:read",
    "channel:write",
    "streamkey:read",
]


def generate_pkce():
    """
    Generate the PKCE verifier and challenge
    required by Kick OAuth.
    """

    code_verifier = secrets.token_urlsafe(64)

    digest = hashlib.sha256(
        code_verifier.encode("ascii")
    ).digest()

    code_challenge = (
        base64.urlsafe_b64encode(digest)
        .rstrip(b"=")
        .decode("ascii")
    )

    return code_verifier, code_challenge


def create_kick_authorization_url(
    state: str,
    code_challenge: str,
) -> str:

    parameters = {
        "response_type": "code",
        "client_id": KICK_CLIENT_ID,
        "redirect_uri": KICK_REDIRECT_URI,
        "scope": " ".join(KICK_SCOPES),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
    }

    return (
        f"{KICK_AUTH_URL}?"
        f"{urlencode(parameters)}"
    )
@router.get("/connect/kick")
def connect_kick():
    state = secrets.token_urlsafe(32)

    code_verifier, code_challenge = generate_pkce()

    # STORE THEM HERE
    pkce_store[state] = {
        "code_verifier": code_verifier
    }

    auth_url = create_kick_authorization_url(
        state=state,
        code_challenge=code_challenge
    )

    return RedirectResponse(auth_url)
{
    "grant_type": "authorization_code",
    "code": code,
    "client_id": KICK_CLIENT_ID,
    "redirect_uri": KICK_REDIRECT_URI,
    "code_verifier": code_verifier
}