from enum import Enum
from hashlib import sha256
from random import randint
from typing import Optional

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

BIAS = ["left", "right"]
EXTENT = ["minimal", "moderate", "strong", "extreme"]

app = FastAPI(docs_url=None, redoc_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

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


class ProcessedResponse(BaseModel):
    success: bool
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


@app.get("/process/{job_hash}", response_model=ProcessedResponse)
async def processed(job_hash: str):
    """
    Query the database for a processed message based on its hash.
    """
    if randint(0, 1) == 0:
        return JSONResponse(content={"success": False}, status_code=status.HTTP_404_NOT_FOUND)

    return {
        "success": True,
        "hash": job_hash,
        "bias": BIAS[randint(0, 1)],
        "extent": EXTENT[randint(0, 3)]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
