# Satyascan: Autonomous Multi-Signal Truth Intelligence System

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)
![Status](https://img.shields.io/badge/status-Production_Ready-success.svg)

**Satyascan** is a high-performance fake news detection and fact-checking pipeline. It moves beyond traditional stylometric classification by employing real-time epistemic verification. By cross-referencing incoming claims against real-world web data and verified fact-check databases, Satyascan accurately determines the truth using Deep Natural Language Inference (NLI).

---

## 🚀 Core Features

- **Multi-Language Frontend:** A highly responsive Diamond Blue UI with a built-in translation module supporting 18+ languages, breaking down language barriers in fact-checking.
- **High-Concurrency Retrieval:** Utilizes a 15-thread Python `ThreadPoolExecutor` to scrape live evidence from DuckDuckGo and Wikipedia in parallel.
- **ChromaDB Vector Vault:** Instant sub-20ms RAG (Retrieval-Augmented Generation) lookup for historically verified claims using `sentence-transformers/all-MiniLM-L6-v2`.
- **DeBERTa-v3 Cross-Encoder Inference:** Employs `nli-deberta-v3-small` to perform full bidirectional self-attention, accurately resolving logical negations to calculate *Entailment*, *Contradiction*, or *Neutrality*.
- **Perceptual Image Forensics:** Secures against manipulated or recycled visual media using 64-bit DCT perceptual hashing (matching via Hamming distance threshold $\le 8$).
- **Epistemic Calibration Filter:** Detects official debunking keywords in authoritative sources to prevent "epistemic inversion" false alarms.

---

## ⚙️ System Architecture

1. **Claim Decomposition:** The input text is separated into core propositions and queried.
2. **Multi-Stream Harvesting:** Parallel REST queries extract the top 15-30 authoritative articles.
3. **Cross-Encoder Inference:** Extracted evidence is paired with the claim `[CLS] Evidence [SEP] Claim [SEP]` and passed into the DeBERTa model.
4. **Credibility Synthesis:** Raw NLI stances are weighted by the domain credibility (e.g., `.gov`, wire services, national media).
5. **Verdict Generation:** Returns `REAL`, `FAKE`, or `UNVERIFIED` in under 0.88 seconds.

---

## 💻 Full Setup & Deployment Instructions

### Prerequisites
- Python 3.10 or higher
- Git
- (Optional) CUDA-enabled GPU for faster inference

### Step 1: Clone the Repository
```bash
git clone https://github.com/sanskar-03/satyascan.git
cd satyascan
```

### Step 2: Create a Virtual Environment
It is highly recommended to isolate the dependencies.
**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```
**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
Install all required backend libraries including FastAPI, Transformers, PyTorch, and ChromaDB.
```bash
pip install -r requirements.txt
```
*(Note: If you have a dedicated NVIDIA GPU, install PyTorch with CUDA support first: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118`)*

### Step 4: Seed the Vector Database (Optional)
If your `rag` directory contains seeding scripts for the ChromaDB memory vault, run them to populate the base facts:
```bash
# Example if using a populate script
python backend/rag/populate_knowledge.py
```

### Step 5: Launch the FastAPI Backend
Start the high-performance Uvicorn server.
```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
The backend API will be live at `http://localhost:8000`. You can access the Swagger documentation at `http://localhost:8000/docs`.

### Step 6: Launch the Frontend
Open a new terminal window, navigate to the project root, and serve the UI using Python's built-in HTTP server.
```bash
# Open a new terminal
cd satyascan/frontend
python -m http.server 3000
```
Visit `http://localhost:3000` in your web browser. 

---

## 📚 Academic Publication
This repository accompanies original research submitted for peer review, detailing the structural advantages of Cross-Encoder NLI architectures over traditional Bi-Encoders in computational fact-checking.

## 🤝 Authors & Contributors
- **Sanskar Kumar**
- **Jayasri**
- **Sumit Kumar**
- **Dr. G. Kavitha** *(Project Supervisor)*

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
