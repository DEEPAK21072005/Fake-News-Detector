import json
from typing import List, Dict, Any, Optional
import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.core.config import settings
from backend.app.database.database import get_db
from backend.app.database.db_models import EvidenceItemRecord
from backend.app.retrieval.vector_store import vector_store
from backend.app.ml.embeddings import get_embedding_provider

router = APIRouter(prefix="/evidence", tags=["Evidence Vault"])


@router.get("")
async def list_evidence_endpoint(
    category: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List indexed verified evidence documents."""
    docs = vector_store.documents
    if category and category.lower() != "all":
        docs = [d for d in docs if d.get("category", "").lower() == category.lower()]
    return docs[:limit]


@router.post("")
async def add_evidence_endpoint(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """Add a new verified or debunked claim to the evidence database."""
    title = payload.get("title", "").strip()
    text = payload.get("text", "").strip()
    source = payload.get("source", "Verified Source").strip()
    url = payload.get("url", "")
    stance = payload.get("stance_tag", "Supporting")
    category = payload.get("category", "General")
    domain = payload.get("domain", source.lower().replace(" ", "") + ".org")
    credibility = float(payload.get("credibility_score", 0.90))

    if not title or not text:
        raise HTTPException(status_code=400, detail="Title and text are required.")

    embedder = get_embedding_provider()
    embedding = embedder.embed_text(f"{title}. {text}")

    doc = {
        "id": vector_store.count() + 1,
        "title": title,
        "text": text,
        "source": source,
        "url": url,
        "publication_date": payload.get("publication_date", "2024-2025"),
        "domain": domain,
        "credibility_score": credibility,
        "category": category,
        "stance_tag": stance
    }

    vector_store.add_documents([doc], embedding[np.newaxis, :])

    # Also persist to DB
    record = EvidenceItemRecord(
        title=title,
        text=text,
        source=source,
        url=url,
        domain=domain,
        credibility_score=credibility,
        category=category,
        stance_tag=stance
    )
    db.add(record)
    await db.commit()

    return {"status": "success", "evidence_item": doc}


@router.post("/seed")
async def seed_starter_evidence_endpoint():
    """Seed the vector store with starter verified research evidence."""
    starter_file = settings.EVIDENCE_PATH / "starter_evidence.json"
    if not starter_file.exists():
        raise HTTPException(status_code=404, detail="Starter evidence file not found.")

    with open(starter_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    embedder = get_embedding_provider()
    texts_to_embed = [f"{item['title']}. {item['text']}" for item in data]
    embeddings = embedder.embed_batch(texts_to_embed)

    vector_store.add_documents(data, embeddings)
    return {"status": "seeded", "count": len(data)}
