from enum import Enum
from typing import Optional

from pydantic import BaseModel


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


class Request(BaseModel):
    """
    Text and corresponding URL to be processed by the BERT model
    """
    id: str
    text: str
    url: str


class Response(BaseModel):
    """
    The response for (potentially) queuing a piece of text to be processed
    """
    success: bool
    bias: Optional[Bias]
    extent: Optional[Extent]
