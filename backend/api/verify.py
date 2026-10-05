from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from services.agent import verify_news
from rag.ingest import ingest_all_feeds, ingest_document, query_trusted_sources

class ManualDoc(BaseModel):
    title: str
    content: str
    url: str
    source: str
router = APIRouter()
@router.post("/rag/ingest-feeds")
def rag_ingest_feeds():
    """Trigger ingestion from all configured trusted RSS feeds."""
    return {"results": ingest_all_feeds()}

@router.post("/rag/ingest-manual")
def rag_ingest_manual(doc: ManualDoc):
    """Manually add a trusted document (e.g. a specific fact-check article)."""
    doc_id = ingest_document(doc.title, doc.content, doc.url, doc.source)
    return {"status": "ingested", "id": doc_id}

@router.get("/rag/query")
def rag_query(q: str):
    """Query the trusted-source knowledge base directly (for debugging)."""
    return {"results": query_trusted_sources(q)}



class News(BaseModel):
    article: str
    image_url: Optional[str] = None

@router.post("/verify")
def verify(news: News):
    return verify_news(news.article, news.image_url)