from enum import Enum
import json
from hashlib import sha256
from random import randint
from typing import Optional

from asyncio import sleep
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

BIAS = ["left", "right"]
EXTENT = ["minimal", "moderate", "strong", "extreme"]

app = FastAPI(docs_url=None, redoc_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"])

processing = []


class ProcessingRequest(BaseModel):
    id: str
    text: str
    url: str


class Bias(str, Enum):
    """
    Which way the bias leans
    """
    left = "left"
    right = "right"
    neutral = "neutral"


class Extent(str, Enum):
    """
    How biased a given piece of text is
    """
    minimal = "minimal"
    moderate = "moderate"
    strong = "strong"
    extreme = "extreme"


class Response(BaseModel):
    processing: bool
    success: bool
    hash: Optional[str]
    bias: Optional[Bias]
    extent: Optional[Extent]


class StreamMessage(BaseModel):
    hash: str
    bias: Bias
    extent: Extent


@app.post("/process", response_model=Response)
async def process(req: ProcessingRequest):
    """
    Analyze a given piece of text to find the bias. Any given piece of text will be checked against the database to
    check if it has already been processed. If it has not yet been processed, it will be queued for processing and
    returned via the `/events` endpoint.
    """
    if randint(0, 1) == 0:
        # Generate the hash
        processing_id = sha256(f"{req.id}_{req.text}".encode()).hexdigest()
        processing.append(processing_id)

        return {"processing": True, "success": True, "hash": processing_id}
    else:
        return {"processing": False, "success": True, "bias": BIAS[randint(0, 1)], "extent": EXTENT[randint(0, 3)]}


async def event_stream():
    """
    A fake event stream for processed data
    """
    while True:
        await sleep(randint(2, 10))

        try:
            proc_id = processing.pop()
        except IndexError:
            proc_id = sha256(b"user-id_platform_some text").hexdigest()

        data = {"hash": proc_id, "bias": BIAS[randint(0, 1)], "extent": EXTENT[randint(0, 3)]}
        yield f"""data: {json.dumps(data)}\n\n"""


@app.get("/events", response_model=StreamMessage)
async def events():
    """
    Read a stream of all processing events. The processed events will be identified by a hash of the id, content, and
    URL. It is up to the requester to determine which event to read.

    **NOTE:** While the response content type is stated as `application/json`, it is actually a `text/event-stream` that
    sends JSON messages delimited by two newlines in accordance with the server-sent events specification. The messages
    can be read using the [EventSource](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) API in the
    browser.
    """
    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
