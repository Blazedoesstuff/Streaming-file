import shutil
import subprocess

from model import StreamPlatform


def check_ffmpeg() -> bool:
    """Return True when FFmpeg is installed and available."""
    return shutil.which("ffmpeg") is not None


def build_destination(platform: StreamPlatform) -> str:
    server = platform.server_url.rstrip("/")
    key = platform.stream_key.lstrip("/")

    return f"{server}/{key}"


def create_ffmpeg_command(
    input_source: str,
    platforms: list[StreamPlatform],
) -> list[str]:
    outputs: list[str] = []

    for platform in platforms:
        destination = build_destination(platform)

        outputs.append(
            f"[f=flv:onfail=ignore]"
            f"{destination}"
        )

    tee_output = "|".join(outputs)

    return [
        "ffmpeg",

        # Read a video file at its normal playback rate.
        "-re",

        # Input file or incoming stream.
        "-i",
        input_source,

        # Select the first video stream.
        "-map",
        "0:v:0",

        # Select audio when audio exists.
        "-map",
        "0:a:0?",

        # Video encoding.
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        "-b:v",
        "2500k",
        "-maxrate",
        "2500k",
        "-bufsize",
        "5000k",
        "-r",
        "30",
        "-g",
        "60",

        # Audio encoding.
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-ar",
        "48000",

        # Required for several streamed outputs.
        "-flags",
        "+global_header",

        # Send one encoded stream to every destination.
        "-f",
        "tee",
        tee_output,
    ]


def start_ffmpeg(
    input_source: str,
    platforms: list[StreamPlatform],
) -> subprocess.Popen[str]:
    if not check_ffmpeg():
        raise RuntimeError(
            "FFmpeg is not installed or is not available in PATH."
        )

    command = create_ffmpeg_command(
        input_source=input_source,
        platforms=platforms,
    )

    return subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )