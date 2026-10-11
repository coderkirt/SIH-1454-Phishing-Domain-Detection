# PHISHEYE Knowledge Corpus: Vector Store Migration Architecture

This guide details the operational strategy, benchmark triggers, and technical steps for migrating the PHISHEYE phishing knowledge retrieval store from ChromaDB to **Qdrant** or **PostgreSQL + pgvector** as scale expands.

---

## 1. Scale Inflection Points & Architecture Selection

| Stage | Corpus Scale | Recommended Vector Engine | Storage Footprint | Target Query Latency | Operational Profile |
|---|---|---|---|---|---|
| **Phase 1 (Current)** | 300 – 50,000 chunks | **ChromaDB (Embedded Persistent)** | < 150 MB (SQLite + Parquet) | < 5 ms | Zero external server dependencies; embedded inside FastAPI process. |
| **Phase 2 (Growth)** | 50,000 – 500,000 chunks | **PostgreSQL 16 + pgvector (HNSW)** | 200 MB – 2 GB | < 12 ms | Unified relational ACID metadata + vector search; native JSONB filtering. |
| **Phase 3 (Enterprise)** | > 500,000 chunks | **Qdrant Cluster (Distributed)** | > 3 GB (Disk-backed vectors + mmap) | < 8 ms (p99) | High-throughput distributed clustering, filtered vector search, horizontal scaling. |

---

## 2. Migration Triggers (When to Migrate from ChromaDB)

Migrate away from embedded ChromaDB when any of the following triggers are met:

1. **Chunk Volume > 500,000**: When feed intelligence ingestion from URLhaus, OpenPhish, and PhishTank reaches hundreds of thousands of active indicator chunks, embedded SQLite memory contention increases.
2. **Multi-Replica Horizontal Scaling**: Chroma embedded mode operates on a single node. If the PHISHEYE FastAPI service scales horizontally across multiple Kubernetes pods or Cloud Run containers, a centralized vector database is required.
3. **Complex Filter Aggregation**: When retrieval queries require complex nested boolean queries, geo-spatial filters, or relational joins across organizational tenant boundaries.

---

## 3. Migration Target 1: PostgreSQL + pgvector

### Advantages
- Consolidates threat metadata, URL scan logs, brand verification tables, and vector embeddings into a single Postgres cluster.
- Native ACID transactions: adding or deleting a threat document and its vector happens in one atomic transaction.
- Supports HNSW and IVFFlat index structures with `vector_cosine_ops`.

### Schema DDL
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE phishing_knowledge_vectors (
    chunk_id VARCHAR(255) PRIMARY KEY,
    doc_id VARCHAR(255) NOT NULL,
    category VARCHAR(64) NOT NULL,
    document TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    metadata JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Cosine Distance HNSW Index
CREATE INDEX phishing_knowledge_vectors_hnsw_idx 
    ON phishing_knowledge_vectors 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- GIN Index for rapid metadata filtering (e.g. brand, category, tags)
CREATE INDEX phishing_knowledge_vectors_meta_idx 
    ON phishing_knowledge_vectors 
    USING gin (metadata);
```

### Execution via PHISHEYE CLI
Export the current ChromaDB store directly to SQL:
```bash
python scripts/migrate_vectors.py --target pgvector --output-dir data/migrations/
psql -h <postgres_host> -U <user> -d phisheye -f data/migrations/pgvector_dump.sql
```

---

## 4. Migration Target 2: Qdrant

### Advantages
- Written in Rust with memory-mapped vector storage (`on_disk: true`).
- Payload filtering without performance degradation.
- Native gRPC API for sub-millisecond retrieval in high-concurrency environments.

### Qdrant Collection Definition
```json
{
  "vectors": {
    "size": 384,
    "distance": "Cosine",
    "on_disk": true
  },
  "hnsw_config": {
    "m": 16,
    "ef_construct": 100,
    "full_scan_threshold": 1000
  }
}
```

### Execution via PHISHEYE CLI
Export the current ChromaDB store to Qdrant PointStruct JSONL:
```bash
python scripts/migrate_vectors.py --target qdrant --output-dir data/migrations/
```

Upload to Qdrant REST endpoint:
```bash
curl -X POST "http://localhost:6333/collections/phishing_knowledge/points?wait=true" \
  -H "Content-Type: application/json" \
  --data-binary @data/migrations/qdrant_points.jsonl
```

---

## 5. Zero-Downtime Migration Checklist

To migrate with zero downtime in production:
1. **Deploy Target Vector Store**: Provision PostgreSQL + pgvector or Qdrant in staging/production.
2. **Execute Initial Dump**: Run `python scripts/migrate_vectors.py --target all` to export existing knowledge vectors.
3. **Enable Dual-Write Adapter**: Update `app/chroma_store.py` to write new chunks to both ChromaDB and the target store simultaneously.
4. **Backfill Historical Delta**: Ingest any delta chunks created during the migration window.
5. **Switch Retrieval Read Path**: Point `app/retrieval.py` dense search queries to the target store.
6. **Decommission ChromaDB**: Archive the final Chroma snapshot using `app/backup.py` (`create_backup(tag="final_pre_migration")`) and retain in cloud storage for 30 days.
