
from fastapi import FastAPI

from db import Base, engine

from Database.users import User
from Database.connected_accounts import ConnectedAccount
from Database.oauth_states import OAuthState

from routes.streams import router as stream_router
from routes.connected_accounts import router as accounts_router

app = FastAPI(title="Social Multistream API")

Base.metadata.create_all(bind=engine)


# Livestream routes
app.include_router(
    stream_router,
    prefix="/streams",
    tags=["Streams"],
)


# Connected account routes
app.include_router(
    accounts_router,
    prefix="/accounts",
    tags=["Connected Accounts"],
)


@app.get("/")
def home() -> dict[str, str]:
    return {
        "message": "Multistream API is running"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )