import os
import chromadb
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.verify import router
from services.utils.logger import logger
from sentence_transformers import CrossEncoder
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)


state = {}

def verify_and_seed_chromadb():
    try:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./rag/chroma_db")
        client = chromadb.PersistentClient(path=persist_dir)
        collection = client.get_or_create_collection("fact_checks")
        if collection.count() == 0:
            logger.warning("ChromaDB is empty. Running automatic database population...")
            try:
                from rag.populate_knowledge import populate
                populate()
                logger.info("ChromaDB successfully seeded.")
            except ImportError:
                logger.error("Could not find populate script, skipping auto-seed.")
    except Exception as e:
        logger.error(f"Error checking ChromaDB: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup chroma DB if missing
    verify_and_seed_chromadb()
    
    # Global Model Caching for high-concurrency requests
    logger.info("Loading DeBERTa-v3 cross-encoder into memory...")
    try:
        state["nli_model"] = CrossEncoder("cross-encoder/nli-deberta-v3-small")
        logger.info("Model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load NLI model: {e}")
    yield
    state.clear()

def get_nli_model():
    return state.get("nli_model")

app = FastAPI(title="Satyascan Truth Intelligence System", version="2.0", lifespan=lifespan)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in frontend_origin.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"status": "online", "service": "Satyascan Truth Intelligence API", "version": "2.0", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "Satyascan Backend Engine"}
