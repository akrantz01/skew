from hashlib import sha256
from os import environ
from typing import List, Tuple

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore, automl
from newspaper import Article, ArticleException

import models

# Project level constants
PROJECT_ID = environ.get("GOOGLE_CLOUD_PROJECT")
MODEL_ID = environ.get("MODEL_ID")
MODEL_PATH = automl.AutoMlClient.model_path(PROJECT_ID, "us-central1", MODEL_ID)

# Service clients
db = firestore.Client()
predictor = automl.PredictionServiceClient()

# HTTP API server
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])


def compute_job_hash(content_id: str, text: str) -> str:
    """
    Compute the job hash for a piece of text given its text and generated ID.

    :param content_id: the generated id of the text
    :param text: the text to be computed
    :return: the job hash
    """
    writer = sha256(content_id.encode())
    writer.update(b"_")
    writer.update(text.encode())
    return writer.hexdigest()


def extract_from_categories(categories: List[automl.AnnotationPayload]) -> Tuple[str, str]:
    """
    Retrieve the bias and extent from a list of categories from a response.

    :param categories: the detected categories
    :return: the bias and extent parameters
    """
    biases = []
    extents = []

    # Sort categories by type
    #   Bias: left, right, neutral
    #   Extent: minimal, moderate, strong, extreme
    for category in categories:
        if category.display_name == "left" or category.display_name == "right" or category.display_name == "neutral":
            biases.append(category)
        else:
            extents.append(category)

    # Find most confident category
    biases.sort(key=lambda c: c.classification.score)
    extents.sort(key=lambda c: c.classification.score)

    return biases[0].display_name, extents[0].display_name


@app.post("/process", response_model=models.Response)
async def process(req: models.Request):
    """
    Analyze a given piece of text to find the bias. Any given piece of text will be checked against the database to
    check if it has already been processed. If it has not yet been processed, it will be sent for inference on
    a GCP NLP trained model.
    """
    # Either fetch the content from the site or use the provided text
    if req.url != "":
        try:
            article = Article(req.url)
            article.download()
            article.parse()

            if article.text != "" and article.text is not None:
                text = article.text
            else:
                text = req.text
        except ArticleException:
            text = req.text
    else:
        text = req.text

    # Calculate hash of id and text
    job_hash = compute_job_hash(req.id, text)

    # Ensure job has not been computed or is being computed
    job_ref = db.collection("text").document(job_hash)
    job = job_ref.get()
    if job.exists:
        job_data = job.to_dict()
        return {
            "success": True,
            "bias": job_data.get("bias"),
            "extent": job_data.get("extent")
        }

    # Process the data
    snippet = automl.TextSnippet(content=text, mime_type="text/plain")
    payload = automl.ExamplePayload(text_snippet=snippet)
    response = predictor.predict(name=MODEL_PATH, payload=payload)
    bias, extent = extract_from_categories(response.payload)

    # Set the processed data to the database
    job_ref.set({
        "hash": job_hash,
        "bias": bias,
        "extent": extent
    })

    return {
        "success": True,
        "bias": bias,
        "extent": extent
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
