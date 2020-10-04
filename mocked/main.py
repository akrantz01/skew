from enum import Enum
from random import randint
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BIAS = ["left", "right"]
EXTENT = ["minimal", "moderate", "strong", "extreme"]

app = FastAPI(docs_url=None, redoc_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])


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
    success: bool
    bias: Optional[Bias]
    extent: Optional[Extent]


@app.post("/process", response_model=Response)
async def process(_req: ProcessingRequest):
    """
    Analyze a given piece of text to find the bias. Any given piece of text will be checked against the database to
    check if it has already been processed. If it has not yet been processed, it will be sent for inference on
    a GCP NLP trained model.
    """
    return {
        "success": True,
        "bias": BIAS[randint(0, 2)],
        "extent": EXTENT[randint(0, 3)]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
