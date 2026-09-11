from pydantic import BaseModel, Field


class StreamPlatform(BaseModel):
    name: str = Field(min_length=1)
    server_url: str = Field(min_length=1)
    stream_key: str = Field(min_length=1)


class StartStreamRequest(BaseModel):
    input_source: str = Field(min_length=1)
    platforms: list[StreamPlatform] = Field(min_length=1)


class StreamResponse(BaseModel):
    stream_id: str
    status: str


class StreamStatusResponse(BaseModel):
    stream_id: str
    status: str
    platforms: list[str]