import os
import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.config import settings
from backend.app.core.logging_config import logger
from backend.app.ml.embeddings import get_embedding_provider
from backend.app.retrieval.vector_store import vector_store
from backend.app.database.database import SyncSessionLocal, Base, sync_engine
from backend.app.database.db_models import EvidenceItemRecord


def seed_evidence_database():
    logger.info("Initializing database tables and vector index...")
    Base.metadata.create_all(sync_engine)

    starter_file = settings.EVIDENCE_PATH / "starter_evidence.json"
    if not starter_file.exists():
        logger.error(f"Starter evidence file not found at {starter_file}")
        return

    with open(starter_file, "r", encoding="utf-8") as f:
        items = json.load(f)

    logger.info(f"Loaded {len(items)} evidence records from JSON. Generating dense embeddings...")
    embedder = get_embedding_provider()
    
    texts = [f"{item['title']}. {item['text']}" for item in items]
    embeddings = embedder.embed_batch(texts)

    # Add to vector store
    vector_store.add_documents(items, embeddings)

    # Add to SQLite database
    db = SyncSessionLocal()
    try:
        # Clear existing to avoid duplicate seeds
        db.query(EvidenceItemRecord).delete()
        for itm in items:
            rec = EvidenceItemRecord(
                id=itm.get("id"),
                title=itm["title"],
                text=itm["text"],
                source=itm["source"],
                url=itm.get("url"),
                publication_date=itm.get("publication_date"),
                domain=itm.get("domain", ""),
                credibility_score=itm.get("credibility_score", 0.95),
                category=itm.get("category", "General"),
                stance_tag=itm.get("stance_tag", "Supporting")
            )
            db.add(rec)
        db.commit()
        logger.info("✅ Evidence database and vector index successfully seeded!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_evidence_database()
