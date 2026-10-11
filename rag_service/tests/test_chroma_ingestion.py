"""Comprehensive unit and integration test suite for ChromaDB Ingestion (Feature 6).

Covers:
- Chunk provenance locators: doc_id, chunk_index, char_start, char_end, paragraph_index, embedding info, content_hash
- Incremental upserting engine: added, updated, unchanged, and deleted chunk tracking
- Stale chunk deletion upon document edit
- Embedding version tracking & mismatch detection
- Point-in-time compressed backups with SHA-256 validation & rollback restore
- 30-day backup retention lifecycle pruning
- Qdrant and PostgreSQL + pgvector migration export
- High-scale threat feed indicator synthesis and batch ingestion
"""

import json
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest
import chromadb

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.backup import ChromaBackupManager, compute_file_sha256
from app.chunker import chunk_document, chunk_corpus
from app.chroma_store import (
    EmbeddingVersionMismatchError,
    delete_document_chunks,
    get_or_create_collection,
    incremental_ingest_corpus,
)
from app.config import settings
from app.corpus import CorpusDocument
from app.feed_ingestion import (
    batch_upsert_chunks,
    build_chunk_from_indicator,
    generate_synthetic_feed_records,
)
from app.migration import VectorMigrationExporter


@pytest.fixture
def sample_doc() -> CorpusDocument:
    return CorpusDocument(
        id="test-doc-prov",
        title="Sample Provenance Lure",
        category="playbook",
        source="CISA Advisory",
        source_url="https://cisa.gov/advisory/test-1",
        last_verified="2026-10-11",
        summary="A test document for verifying granular provenance.",
        language="en",
        region="global",
        channels=["email"],
        brands=["microsoft"],
        threat_tags=["session_hijack"],
        mitre=["T1539"],
        body="## Attack Flow\n\nAttacker sets up an AiTM reverse proxy.\n\n## Mitigation Steps\n\nEnforce FIDO2 WebAuthn keys.",
    )


def test_chunk_provenance_locators(sample_doc):
    """Test that all chunks contain chunk_index, char_start, char_end, paragraph_index, embedding info, and SHA-256 hash."""
    chunks = chunk_document(sample_doc)
    assert len(chunks) == 3  # 1 overview + 2 sections

    # 1. Overview chunk
    overview = chunks[0]
    assert overview.chunk_index == 0
    assert overview.paragraph_index == 0
    assert overview.char_start == 0
    assert overview.char_end > 0
    assert overview.embedding_model == settings.EMBEDDING_MODEL
    assert overview.embedding_version == settings.EMBEDDING_VERSION
    assert len(overview.content_hash) == 64  # SHA-256 hex string

    assert overview.metadata["chunk_index"] == 0
    assert overview.metadata["char_start"] == 0
    assert overview.metadata["content_hash"] == overview.content_hash
    assert overview.metadata["embedding_model"] == settings.EMBEDDING_MODEL
    assert overview.metadata["embedding_version"] == settings.EMBEDDING_VERSION

    # 2. Section chunks
    sec1 = chunks[1]
    assert sec1.chunk_index == 1
    assert sec1.paragraph_index == 1
    assert sec1.char_start >= 0
    assert sec1.char_end > sec1.char_start
    assert sec1.section_title == "Attack Flow"
    assert len(sec1.content_hash) == 64

    sec2 = chunks[2]
    assert sec2.chunk_index == 2
    assert sec2.paragraph_index == 2
    assert sec2.char_start >= sec1.char_end or sec2.char_start > 0
    assert sec2.section_title == "Mitigation Steps"


def test_incremental_ingest_added_updated_unchanged(sample_doc):
    """Test that incremental ingestion correctly categorizes added, updated, and unchanged chunks."""
    client = chromadb.EphemeralClient()
    col_name = "test_incremental_col"

    # Step 1: Initial Ingest -> All chunks should be added
    diff1 = incremental_ingest_corpus(
        docs=[sample_doc],
        client=client,
        collection_name=col_name,
    )
    assert len(diff1.added_chunks) == 3
    assert len(diff1.updated_chunks) == 0
    assert diff1.unchanged_chunks == 0
    assert len(diff1.deleted_chunks) == 0
    assert diff1.total_active_chunks == 3

    # Step 2: Re-ingest unchanged doc -> All chunks should be unchanged
    diff2 = incremental_ingest_corpus(
        docs=[sample_doc],
        client=client,
        collection_name=col_name,
    )
    assert len(diff2.added_chunks) == 0
    assert len(diff2.updated_chunks) == 0
    assert diff2.unchanged_chunks == 3
    assert len(diff2.deleted_chunks) == 0
    assert diff2.total_active_chunks == 3

    # Step 3: Modify one section of the document -> That section should be updated, others unchanged
    modified_doc = CorpusDocument(
        id="test-doc-prov",
        title="Sample Provenance Lure",
        category="playbook",
        source="CISA Advisory",
        source_url="https://cisa.gov/advisory/test-1",
        last_verified="2026-10-11",
        summary="A test document for verifying granular provenance.",
        language="en",
        region="global",
        channels=["email"],
        brands=["microsoft"],
        threat_tags=["session_hijack"],
        mitre=["T1539"],
        body="## Attack Flow\n\nAttacker sets up an AiTM reverse proxy with EVILGINX v3.\n\n## Mitigation Steps\n\nEnforce FIDO2 WebAuthn keys.",
    )

    diff3 = incremental_ingest_corpus(
        docs=[modified_doc],
        client=client,
        collection_name=col_name,
    )
    assert len(diff3.added_chunks) == 0
    assert len(diff3.updated_chunks) == 1
    assert "test-doc-prov#attack-flow" in diff3.updated_chunks
    assert diff3.unchanged_chunks == 2
    assert diff3.total_active_chunks == 3


def test_incremental_ingest_deletes_stale_chunks(sample_doc):
    """Test that removing a section from a document automatically deletes the stale chunk from ChromaDB."""
    client = chromadb.EphemeralClient()
    col_name = "test_stale_delete_col"

    # Ingest 3 chunks
    incremental_ingest_corpus(docs=[sample_doc], client=client, collection_name=col_name)

    # Document now only has 1 section (Mitigation Steps removed)
    shortened_doc = CorpusDocument(
        id="test-doc-prov",
        title="Sample Provenance Lure",
        category="playbook",
        source="CISA Advisory",
        source_url="https://cisa.gov/advisory/test-1",
        last_verified="2026-10-11",
        summary="A test document for verifying granular provenance.",
        language="en",
        region="global",
        channels=["email"],
        brands=["microsoft"],
        threat_tags=["session_hijack"],
        mitre=["T1539"],
        body="## Attack Flow\n\nAttacker sets up an AiTM reverse proxy.",
    )

    diff = incremental_ingest_corpus(docs=[shortened_doc], client=client, collection_name=col_name)
    assert len(diff.deleted_chunks) == 1
    assert "test-doc-prov#mitigation-steps" in diff.deleted_chunks
    assert diff.total_active_chunks == 2


def test_delete_document_chunks(sample_doc):
    """Test explicit deletion of all chunks for a doc_id."""
    client = chromadb.EphemeralClient()
    col_name = "test_explicit_del_col"

    incremental_ingest_corpus(docs=[sample_doc], client=client, collection_name=col_name)
    deleted_count = delete_document_chunks("test-doc-prov", client=client, collection_name=col_name)
    assert deleted_count == 3

    col = client.get_collection(col_name)
    assert col.count() == 0


def test_embedding_version_mismatch_detection(sample_doc):
    """Test that collection metadata mismatch triggers EmbeddingVersionMismatchError unless force_reembed is True."""
    client = chromadb.EphemeralClient()
    col_name = "test_version_mismatch_col"

    # Create collection with old version metadata
    ef = chromadb.utils.embedding_functions.DefaultEmbeddingFunction()
    col = client.create_collection(
        name=col_name,
        embedding_function=ef,
        metadata={
            "embedding_model": "old-sentence-transformers",
            "embedding_version": "v0.1.0",
        },
    )
    # Add dummy chunk
    col.add(ids=["dummy#1"], documents=["dummy text"], metadatas=[{"doc_id": "dummy"}])

    with pytest.raises(EmbeddingVersionMismatchError):
        incremental_ingest_corpus(
            docs=[sample_doc],
            client=client,
            collection_name=col_name,
            force_reembed=False,
        )

    # With force_reembed=True, it should succeed by recreating collection
    diff = incremental_ingest_corpus(
        docs=[sample_doc],
        client=client,
        collection_name=col_name,
        force_reembed=True,
    )
    assert diff.total_active_chunks == 3


def test_chroma_backup_and_restore(tmp_path):
    """Test backup creation, SHA-256 checksum verification, and safe rollback restore."""
    persist_dir = tmp_path / "chroma_source"
    backup_dir = tmp_path / "backups"
    restore_target = tmp_path / "chroma_restored"

    persist_dir.mkdir(parents=True, exist_ok=True)
    # Create mock chroma files
    (persist_dir / "chroma.sqlite3").write_text("SQLite format 3 mock data", encoding="utf-8")
    (persist_dir / "index_data.bin").write_bytes(b"\x00\x01\x02\x03" * 64)

    mgr = ChromaBackupManager(persist_dir=persist_dir, backup_dir=backup_dir)

    # 1. Create backup
    manifest = mgr.create_backup(tag="unit_test", chunk_count=42)
    assert manifest.backup_id.startswith("backup_")
    assert manifest.total_chunks == 42
    assert manifest.size_bytes > 0
    assert len(manifest.sha256_checksum) == 64
    assert Path(manifest.archive_path).exists()

    # 2. List backups
    listed = mgr.list_backups()
    assert len(listed) >= 1
    assert listed[0]["backup_id"] == manifest.backup_id

    # 3. Restore backup
    res = mgr.restore_backup(
        archive_path=Path(manifest.archive_path),
        target_dir=restore_target,
        verify_checksum=True,
    )
    assert res["status"] == "success"
    assert (restore_target / "chroma.sqlite3").exists()
    assert (restore_target / "index_data.bin").exists()
    assert (restore_target / "chroma.sqlite3").read_text(encoding="utf-8") == "SQLite format 3 mock data"

    # 4. Test cloud export adapter
    cloud_res = mgr.export_to_cloud_storage(Path(manifest.archive_path), provider="s3")
    assert cloud_res["status"] == "exported"
    assert cloud_res["provider"] == "s3"
    assert cloud_res["uri"].startswith("s3://")


def test_backup_retention_prune(tmp_path):
    """Test 30-day retention pruning keeping minimum backup floor."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    mgr = ChromaBackupManager(persist_dir=tmp_path, backup_dir=backup_dir)

    now = datetime.now(timezone.utc)

    # Create 4 synthetic backups: 2 old (40 and 50 days ago) and 2 recent (2 and 5 days ago)
    ages = [50, 40, 5, 2]
    for age in ages:
        dt = now - timedelta(days=age)
        b_id = f"backup_{dt.strftime('%Y%m%d_%H%M%S')}"
        archive_file = backup_dir / f"{b_id}.tar.gz"
        archive_file.write_bytes(b"dummy archive data")
        mf_file = backup_dir / f"{b_id}_manifest.json"
        mf_data = {
            "backup_id": b_id,
            "created_at": dt.isoformat(),
            "archive_filename": archive_file.name,
            "archive_path": str(archive_file),
            "sha256_checksum": "dummyhash",
            "size_bytes": 18,
            "collection_name": "test",
            "total_chunks": 10,
            "embedding_model": settings.EMBEDDING_MODEL,
            "embedding_version": settings.EMBEDDING_VERSION,
        }
        mf_file.write_text(json.dumps(mf_data), encoding="utf-8")

    # Prune with 30-day retention and keep_min=2
    prune_res = mgr.prune_backups(max_age_days=30, keep_min=2)
    assert prune_res["pruned_count"] == 2
    assert prune_res["retained_count"] == 2
    assert len(list(backup_dir.glob("*.tar.gz"))) == 2


def test_migration_exporter_qdrant_and_pgvector(sample_doc, tmp_path):
    """Test exporting Chroma collection to Qdrant points JSONL and PostgreSQL + pgvector SQL script."""
    client = chromadb.EphemeralClient()
    col_name = "test_migration_col"

    incremental_ingest_corpus(docs=[sample_doc], client=client, collection_name=col_name)

    exporter = VectorMigrationExporter(collection_name=col_name, client=client)

    # 1. Qdrant export
    qdrant_file = tmp_path / "qdrant_test.jsonl"
    q_res = exporter.export_to_qdrant(qdrant_file)
    assert q_res["total_points"] == 3
    assert qdrant_file.exists()

    with open(qdrant_file, "r", encoding="utf-8") as f:
        first_line = json.loads(f.readline())
        assert "id" in first_line
        assert "vector" in first_line
        assert "payload" in first_line
        assert first_line["payload"]["category"] == "playbook"

    # 2. pgvector export
    pg_file = tmp_path / "pgvector_test.sql"
    pg_res = exporter.export_to_pgvector(pg_file, table_name="test_embeddings")
    assert pg_res["total_rows"] == 3
    assert pg_file.exists()

    sql_content = pg_file.read_text(encoding="utf-8")
    assert "CREATE EXTENSION IF NOT EXISTS vector;" in sql_content
    assert "CREATE TABLE IF NOT EXISTS test_embeddings" in sql_content
    assert "vector(384)" in sql_content
    assert "INSERT INTO test_embeddings" in sql_content


def test_feed_intelligence_generation_and_batch_upsert():
    """Test synthetic feed indicator generation, provenance building, and batch upsert."""
    indicators = generate_synthetic_feed_records(count=20, seed=42)
    assert len(indicators) == 20

    ind = indicators[0]
    chunk = build_chunk_from_indicator(ind, chunk_index=0)
    assert chunk.category == "threat_feed"
    assert chunk.chunk_type == "threat_feed"
    assert chunk.metadata["doc_id"].startswith("feed_")
    assert chunk.metadata["embedding_model"] == settings.EMBEDDING_MODEL
    assert len(chunk.metadata["content_hash"]) == 64
    assert chunk.metadata["brands"] != ["_none_"]
    assert chunk.metadata["mitre"] != ["_none_"]

    client = chromadb.EphemeralClient()
    chunks = [build_chunk_from_indicator(x, chunk_index=i) for i, x in enumerate(indicators)]
    res = batch_upsert_chunks(chunks=chunks, client=client, collection_name="test_feed_col", batch_size=10)
    assert res["status"] == "success"
    assert res["upserted_chunks"] == 20
    assert res["collection_total"] == 20
