import os
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+psycopg2://postgres:yourpassword@localhost:5432/incident_assist"

# The following lines related to OpenAI have been removed as per the user's request.
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# client = OpenAI(api_key=OPENAI_API_KEY)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

app = FastAPI(title="Incident Assist API")

# --- Models ---
class SearchRequest(BaseModel):
    query: str
    k: int = 5

class SuggestRequest(BaseModel):
    query: str
    k: int = 3

# --- Helpers ---
# This helper function has been replaced with a placeholder since the
# original functionality relied on an external AI model.
def embed_text(text: str) -> List[float]:
    """
    Placeholder for a removed embedding function.
    This function originally called an external AI model to generate embeddings.
    It has been replaced with a placeholder to demonstrate the endpoint structure.
    """
    # The actual dimension of the embeddings would depend on the model used.
    # We use 1536 as it's a common dimension for many embedding models.
    return [0.0] * 1536

# --- Endpoints ---
@app.post("/search")
def search(req: SearchRequest):
    qvec = embed_text(req.query)
    with engine.begin() as db:
        rows = db.execute(
            text("""
                SELECT t.ticket_id,
                       t.issue_summary,
                       t.resolution_notes,
                       1 - (te.embedding <-> :qvec) AS similarity
                FROM ticket_embeddings te
                JOIN tickets t ON t.ticket_id = te.ticket_id
                ORDER BY te.embedding <-> :qvec
                LIMIT :k;
            """),
            {"qvec": qvec, "k": req.k},
        ).mappings().all()
    return {"matches": list(rows)}

@app.post("/suggest")
def suggest(req: SuggestRequest):
    qvec = embed_text(req.query)
    with engine.begin() as db:
        rows = db.execute(
            text("""
                SELECT t.ticket_id,
                       t.issue_summary,
                       t.resolution_notes
                FROM ticket_embeddings te
                JOIN tickets t ON t.ticket_id = te.ticket_id
                ORDER BY te.embedding <-> :qvec
                LIMIT :k;
            """),
            {"qvec": qvec, "k": req.k},
        ).mappings().all()

    # The following logic for generating a suggestion using a large language model
    # has been removed as per the user's request. A placeholder is returned instead.
    mock_suggestion = """This is a placeholder for the AI-generated suggestion.
The AI functionality has been removed. The application still performs vector search
to find similar tickets, but it no longer uses an LLM to formulate a resolution."""

    return {
        "matches": list(rows),
        "suggestion": mock_suggestion,
    }