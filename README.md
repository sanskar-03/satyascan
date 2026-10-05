# Satyascan: Autonomous Multi-Signal Truth Intelligence System

Satyascan is a high-performance fake news detection and fact-checking pipeline that moves beyond traditional stylometric classification by employing real-time epistemic verification.

## Core Features
- **Multi-Language Frontend**: Satyascan features a multilingual user interface, breaking down language barriers in fact-checking.
- **High-Concurrency Retrieval**: Uses a 15-thread Python ThreadPoolExecutor to scrape DuckDuckGo and Wikipedia in parallel.
- **ChromaDB Vector Vault**: Instant sub-20ms lookup for historically verified claims using `sentence-transformers/all-MiniLM-L6-v2`.
- **DeBERTa-v3 Cross-Encoder**: Utilizes `nli-deberta-v3-small` to perform full bidirectional self-attention and Natural Language Inference (NLI) to calculate Entailment, Contradiction, and Neutrality.
- **Perceptual Image Forensics**: Secures against manipulated visual media using 64-bit DCT perceptual hashing (Hamming distance threshold $\le 8$).
- **Epistemic Calibration Filter**: Detects official debunking keywords to prevent false alarms.

## Deployment
1. `pip install -r requirements.txt`
2. Run backend: `uvicorn app:app --host 0.0.0.0 --port 8000`
3. Serve frontend: `python -m http.server 3000 --directory ./frontend`

## Academic Publication
This repository accompanies our original research paper submitted for peer review. Datasets (15 benchmark claims + 400 NLI pairs) are included in the `data/` directory.
