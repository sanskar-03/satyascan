import imagehash
from PIL import Image
import requests
from io import BytesIO
import json
import os

HASH_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rag", "image_hashes.json")

def _load_db():
    if os.path.exists(HASH_DB_PATH):
        with open(HASH_DB_PATH) as f:
            return json.load(f)
    return {}

def _save_db(db):
    with open(HASH_DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

def _get_image(image_url):
    resp = requests.get(image_url, timeout=10, headers={
        "User-Agent": "Mozilla/5.0"
    })
    content_type = resp.headers.get("Content-Type", "")

    if "image" not in content_type:
        raise ValueError(
            f"URL did not return an image (got Content-Type: {content_type}, "
            f"status: {resp.status_code}). First 200 bytes: {resp.content[:200]}"
        )

    return Image.open(BytesIO(resp.content))

def add_known_image(image_url, metadata):
    """Add an image to your trusted/known corpus, e.g. after manual fact-check."""
    img = _get_image(image_url)
    phash = str(imagehash.phash(img))

    db = _load_db()
    db[phash] = {"image_url": image_url, "metadata": metadata}
    _save_db(db)
    return phash

def reverse_image_search(image_url: str, threshold: int = 8):
    """Compare against known corpus using perceptual hash distance."""
    img = _get_image(image_url)
    query_hash = imagehash.phash(img)

    db = _load_db()
    matches = []

    for stored_hash, entry in db.items():
        distance = query_hash - imagehash.hex_to_hash(stored_hash)
        if distance <= threshold:
            matches.append({
                "similarity_distance": distance,
                "matched_image": entry["image_url"],
                "metadata": entry["metadata"]
            })

    matches.sort(key=lambda m: m["similarity_distance"])

    return {
        "total_matches": len(matches),
        "matches": matches
    }