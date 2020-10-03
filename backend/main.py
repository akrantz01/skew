from hashlib import sha256
import json
from os import environ

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.cloud import firestore, pubsub_v1

import models

# Project level constants
PROJECT_ID = environ.get("GOOGLE_CLOUD_PROJECT")
TOPIC_ID = environ.get("PUBLISHER_TOPIC") or "processing-queue"

# Database client
db = firestore.Client()

# Pub/sub client
publisher = pubsub_v1.PublisherClient()
to_be_processed_topic = publisher.topic_path(PROJECT_ID, TOPIC_ID)

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


@app.post("/process", response_model=models.ProcessingResponse)
async def process(req: models.Request):
    """
    Analyze a given piece of text to find the bias. Any given piece of text will be checked against the database to
    check if it has already been processed. If it has not yet been processed, it will be queued for processing and
    returned via the `/events` endpoint.
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
            "processing": job_data["processing"],
            "hash": job_hash,
            "bias": job_data.get("bias"),
            "extent": job_data.get("extent")
        }

    # Set the unprocessed data to the database
    job_ref.set({
        "processing": True,
        "url": req.url,
        "text": req.text
    })

    # Publish a message to be processed
    publisher.publish(to_be_processed_topic, json.dumps({
        "hash": job_hash,
        "text": req.text
    }).encode())

    return {
        "success": True,
        "processing": True,
        "hash": job_hash
    }


@app.get("/process/{job_hash}", response_model=models.PollingResponse)
async def processed(job_hash: str):
    """
    Query the database for a processed message based on its hash.
    """
    # Check if processing has completed
    job = db.collection("text").document(job_hash).get()
    job_data = job.to_dict()
    if job.exists and not job_data.get("processing"):
        return {
            "success": True,
            "hash": job_hash,
            "bias": job_data.get("bias"),
            "extent": job_data.get("extent")
        }

    # Not yet processed, return not found
    return JSONResponse(content={"success": False}, status_code=status.HTTP_404_NOT_FOUND)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
