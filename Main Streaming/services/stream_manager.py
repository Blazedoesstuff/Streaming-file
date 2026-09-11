import subprocess
import uuid
from dataclasses import dataclass

from model import StreamPlatform
from services.ffmpeg_service import start_ffmpeg


@dataclass
class ActiveStream:
    process: subprocess.Popen[str]
    platforms: list[str]
    owner_id: int


active_streams: dict[str, ActiveStream] = {}


def start_stream(
    input_source: str,
    platforms: list[StreamPlatform],
    owner_id: int,
) -> str:
    stream_id = str(uuid.uuid4())

    process = start_ffmpeg(
        input_source=input_source,
        platforms=platforms,
    )

    active_streams[stream_id] = ActiveStream(
        process=process,
        platforms=[
            platform.name
            for platform in platforms
        ],
        owner_id=owner_id,
    )

    return stream_id


def get_stream_status(
    stream_id: str,
    owner_id: int,
) -> dict[str, object] | None:
    active_stream = active_streams.get(stream_id)

    if active_stream is None:
        return None

    if active_stream.owner_id != owner_id:
        return None

    return_code = active_stream.process.poll()

    if return_code is None:
        stream_status = "running"
    elif return_code == 0:
        stream_status = "finished"
    else:
        stream_status = "failed"

    return {
        "stream_id": stream_id,
        "status": stream_status,
        "platforms": active_stream.platforms,
    }


def stop_stream(
    stream_id: str,
    owner_id: int,
) -> bool:
    active_stream = active_streams.get(stream_id)

    if active_stream is None:
        return False

    if active_stream.owner_id != owner_id:
        return False

    process = active_stream.process

    if process.poll() is None:
        process.terminate()

        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    del active_streams[stream_id]

    return True