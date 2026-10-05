from services.utils.logger import logger
import os
import chromadb
from chromadb.utils import embedding_functions
import feedparser
import hashlib

CHROMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")

# Trusted fact-check / news RSS feeds
TRUSTED_FEEDS = {
    "FactCheck.org": "https://www.factcheck.org/feed/",
    "Lead Stories": "https://leadstories.com/atom.xml",
    "Full Fact": "https://fullfact.org/feed/all/",
    "TruthOrFiction": "https://www.truthorfiction.com/feed/",
}

from core.device import get_device

_client = chromadb.PersistentClient(path=CHROMA_PATH)
try:
    _embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2",
        device=get_device().type,
        local_files_only=True
    )
except Exception:
    _embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2",
        device=get_device().type
    )

_collection = _client.get_or_create_collection(
    name="trusted_sources",
    embedding_function=_embedder
)

def _make_id(url: str, title: str = "") -> str:
    key = f"{url}::{title}" if title else url
    return hashlib.sha256(key.encode()).hexdigest()[:16]

def ingest_document(title: str, content: str, url: str, source: str):
    """Add a single trusted document to the vector store."""
    doc_id = _make_id(url, title)
    _collection.upsert(
        ids=[doc_id],
        documents=[content],
        metadatas=[{"title": title, "url": url, "source": source}]
    )
    return doc_id

def ingest_rss_feed(feed_name: str, feed_url: str, limit: int = 20):
    """Pull recent entries from a trusted RSS feed and ingest them."""
    parsed = feedparser.parse(feed_url)
    count = 0

    for entry in parsed.entries[:limit]:
        title = entry.get("title", "")
        summary = entry.get("summary", "") or entry.get("description", "")
        url = entry.get("link", "")

        if not title or not url:
            continue

        content = f"{title}\n\n{summary}"
        ingest_document(title, content, url, feed_name)
        count += 1

    return {"feed": feed_name, "ingested": count}

def ingest_all_feeds():
    results = []
    for name, url in TRUSTED_FEEDS.items():
        try:
            result = ingest_rss_feed(name, url)
            results.append(result)
        except Exception as e:
            results.append({"feed": name, "error": str(e)})
    return results

def query_trusted_sources(query: str, n_results: int = 2, max_distance: float = 0.38):
    """Query the trusted-source vector DB for relevant fact-checks.
    max_distance filters out weak/irrelevant matches — ChromaDB always
    returns its nearest neighbors even if none are actually relevant."""
    results = _collection.query(
        query_texts=[query],
        n_results=n_results
    )

    output = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            if dist > max_distance:
                continue
            output.append({
                "content": doc,
                "title": meta.get("title"),
                "url": meta.get("url"),
                "source": meta.get("source"),
                "relevance_distance": dist
            })

    return output