from hashlib import sha256
from os import environ

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore, language_v1

import models

# Service clients
db = firestore.Client()
language = language_v1.LanguageServiceClient()

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


def extract_from_categories(categories: language_v1.types.ClassificationCategory):
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
        if category.name == "left" or category.name == "right" or category.name == "neutral":
            biases.append(category)
        else:
            extents.append(category)

    # Find most confident category
    biases.sort(key=lambda c: c.confidence)
    extents.sort(key=lambda c: c.confidence)

    return biases[0], extents[0]


@app.post("/process", response_model=models.Response)
async def process(req: models.Request):
    """
    Analyze a given piece of text to find the bias. Any given piece of text will be checked against the database to
    check if it has already been processed. If it has not yet been processed, it will be sent for inference on
    a GCP NLP trained model.
    """
    # Calculate hash of id and text
    job_hash = compute_job_hash(req.id, req.text)

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
    response = language.classify_text({
        "content": req.text,
        "type": language_v1.enums.Document.Type.PLAIN_TEXT,
        "language": "en",
    })
    bias, extent = extract_from_categories(response.categories)

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
