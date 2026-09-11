from datetime import datetime, timedelta
import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from googleapiclient.discovery import build
from sqlalchemy import select
from sqlalchemy.orm import Session
import secrets
from db import get_database
from Database.connected_accounts import ConnectedAccount
from Database.users import User
from security import get_current_user
from services.youtube_oauth import create_youtube_flow
from services.kick_oauth import (
    create_kick_authorization_url,
    generate_pkce,
)

router = APIRouter()


@router.get("/youtube/connect")
def connect_youtube(
    current_user: User = Depends(get_current_user),
):
    flow = create_youtube_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=str(current_user.id),
    )

    return RedirectResponse(
        authorization_url
    )
@router.get("/")
def list_connected_accounts(
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_database),
):
    accounts = database.scalars(
        select(ConnectedAccount).where(
            ConnectedAccount.user_id
            == current_user.id
        )
    ).all()

    return [
        {
            "platform": account.platform,
            "account_name": account.account_name,
        }
        for account in accounts
    ]
@router.delete("/{platform}")
def disconnect_account(
    platform: str,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_database),
):
    account = database.scalar(
        select(ConnectedAccount).where(
            ConnectedAccount.user_id
            == current_user.id,
            ConnectedAccount.platform
            == platform.lower(),
        )
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Connected account not found.",
        )

    database.delete(account)
    database.commit()

    return {
        "message": f"{platform} disconnected."
    }
@router.delete("/{platform}")
def disconnect_account(
    platform: str,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_database),
):
    account = database.scalar(
        select(ConnectedAccount).where(
            ConnectedAccount.user_id
            == current_user.id,
            ConnectedAccount.platform
            == platform.lower(),
        )
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Connected account not found.",
        )

    database.delete(account)
    database.commit()

    return {
        "message": f"{platform} disconnected."
    }

@router.get("/kick/connect")
def connect_kick(
    current_user: User = Depends(get_current_user),
):
    state = secrets.token_urlsafe(32)

    code_verifier, code_challenge = (
        generate_pkce()
    )

    # TEMPORARY:
    # We'll replace this with a database/session
    # once the basic OAuth flow works.
    oauth_state = {
        "user_id": current_user.id,
        "code_verifier": code_verifier,
    }

    authorization_url = (
        create_kick_authorization_url(
            state=state,
            code_challenge=code_challenge,
        )
    )

    return RedirectResponse(
        authorization_url
    )
@router.get("/kick/callback")
def kick_callback(
    code: str,
    state: str,
    database: Session = Depends(get_database),
):
    # We'll retrieve the stored OAuth state here.
    # For now this is the placeholder.
    oauth_state = get_stored_oauth_state(state)

    if oauth_state is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth state.",
        )

    token_response = requests.post(
        "https://id.kick.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": KICK_CLIENT_ID,
            "client_secret": KICK_CLIENT_SECRET,
            "redirect_uri": KICK_REDIRECT_URI,
            "code_verifier": oauth_state[
                "code_verifier"
            ],
            "code": code,
        },
        timeout=15,
    )

    if not token_response.ok:
        raise HTTPException(
            status_code=400,
            detail="Kick authorization failed.",
        )

    tokens = token_response.json()

    return {
        "message": "Kick authorization successful."
    }
@router.get("/twitch/callback")
def twitch_callback(
    code: str,
    state: str,
    database: Session = Depends(get_database),
):
    oauth_state = (
        database.query(OAuthState)
        .filter(OAuthState.state == state)
        .first()
    )

    if not oauth_state:
        raise HTTPException(
            status_code=400,
            detail="Invalid state"
        )

    token_response = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": TWITCH_REDIRECT_URI,
        },
        timeout=15,
    )

    if not token_response.ok:
        raise HTTPException(
            status_code=400,
            detail="Twitch authorization failed"
        )

    tokens = token_response.json()
    account = ConnectedAccount(
        user_id=oauth_state.user_id,
        platform="twitch",
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
    )

    database.add(account)

    database.delete(oauth_state)

    database.commit()

    return {
        "message": "Twitch connected successfully"
    }
@router.get("/facebook/connect")
def connect_facebook(
    database: Session = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    state = secrets.token_urlsafe(32)

    oauth_state = OAuthState(
        state=state,
        user_id=current_user.id,
        platform="facebook",
        code_verifier=None,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )

    database.add(oauth_state)
    database.commit()

    auth_url = create_facebook_authorization_url(state)

    return RedirectResponse(auth_url)
