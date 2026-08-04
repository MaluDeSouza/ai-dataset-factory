# 🏭 AI Dataset Factory

> A platform for AI Data Engineering that transforms heterogeneous corporate documents into high-quality datasets ready for Fine Tuning and RAG systems.

> 🚧 **Project Status:** Under Development

## 📖 Overview

AI Dataset Factory is an open-source platform designed to automate one of the most expensive stages of enterprise AI projects: **data preparation**.

Instead of focusing on model training, the platform prepares raw and unstructured information for downstream AI pipelines by performing tasks such as:

- Multi-format document ingestion
- Data normalization
- Intelligent cleaning
- PII anonymization
- Document classification
- Dataset validation
- JSONL generation for Fine Tuning
- Embedding generation for RAG

The project follows a modular architecture, making it easy to extend with new document formats, LLM providers and vector databases.

---

## 🚀 Planned Features

- [ ] Multi-format document ingestion
- [ ] Cleaning Pipeline
- [ ] PII Anonymization
- [ ] Intelligent Document Classification
- [ ] Dataset Validation
- [ ] JSONL Export
- [ ] Embedding Generation
- [ ] Vector Database Integration
- [ ] REST API
- [ ] Processing Dashboard

---

## 🏗️ Architecture

The project follows a modular architecture based on independent processing pipelines.

```
Documents
     │
     ▼
 Import
     │
     ▼
Normalize
     │
     ▼
 Cleaning
     │
     ▼
Anonymization
     │
     ▼
Classification
     │
     ▼
Validation
     │
     ├────────► JSONL (Fine Tuning)
     │
     └────────► Embeddings (RAG)
```

Additional documentation is available in the **docs/** directory.

---

## 📚 Documentation

- Architecture (Coming Soon)
- API (Coming Soon)
- Pipeline (Coming Soon)

---

## 🛠️ Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Sentence Transformers
- HuggingFace Datasets
- Qdrant
- Docker

---

## 📌 Current Status

The project is currently in the architecture and planning phase.