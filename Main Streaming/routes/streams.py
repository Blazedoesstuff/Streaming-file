from fastapi import APIRouter, HTTPException

from model import StartStreamRequest
from services.stream_manager import start_stream, stop_stream


router = APIRouter()


@router.post("/start")
def start_multistream(
    request: StartStreamRequest,
) -> dict[str, str]:
    stream_id = start_stream(
        input_url=request.input_url,
        platforms=request.platforms,
    )

    return {
        "stream_id": stream_id,
        "status": "started",
    }


@router.post("/{stream_id}/stop")
def stop_multistream(
    stream_id: str,
) -> dict[str, str]:
    stopped = stop_stream(stream_id)

    if not stopped:
        raise HTTPException(
            status_code=404,
            detail="Stream was not found.",
        )

    return {
        "stream_id": stream_id,
        "status": "stopped",
    }