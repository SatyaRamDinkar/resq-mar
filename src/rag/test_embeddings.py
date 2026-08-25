"""
Dependencies: pytest, chromadb
"""
import os
import tempfile
import pytest
from src.rag.embeddings import SOPKnowledgeBase

@pytest.fixture
def temp_kb():
    """
    Fixture that creates a temporary ChromaDB instance and ingests dummy data.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        kb = SOPKnowledgeBase(persist_dir=temp_dir)
        
        # Create dummy SOP files for testing
        sops_dir = os.path.join(temp_dir, "test_sops")
        os.makedirs(sops_dir, exist_ok=True)
        
        with open(os.path.join(sops_dir, "flood.md"), "w", encoding="utf-8") as f:
            f.write("## SOP-FLD-TEST: Flood Evacuation\nDetails about moving away from rising water.")
            
        with open(os.path.join(sops_dir, "fire.md"), "w", encoding="utf-8") as f:
            f.write("## SOP-FIR-TEST: Building Fire\nDetails about putting out the fire and rescuing people.")
            
        kb.ingest_sops(sop_dir=sops_dir)
        yield kb

def test_ingest_sops(temp_kb):
    """Verify SOPs are ingested and the collection has the correct count."""
    stats = temp_kb.get_collection_stats()
    assert stats["total_sops"] == 2
    assert stats["by_hazard"]["flood"] == 1
    assert stats["by_hazard"]["fire"] == 1

def test_query_flood(temp_kb):
    """Query with hazard_type='flood', verify results are flood-related."""
    results = temp_kb.query(hazard_type="flood", query_text="people trapped in water", top_k=3)
    assert len(results) == 1
    assert results[0]["hazard_type"] == "flood"
    assert results[0]["id"] == "SOP-FLD-TEST"

def test_query_unknown(temp_kb):
    """Query without hazard filter (unknown), verify it returns mixed results based on semantics."""
    results = temp_kb.query(hazard_type="unknown", query_text="rescue operation", top_k=3)
    assert len(results) == 2
    # The results should include both fire and flood SOPs
    hazard_types = [r["hazard_type"] for r in results]
    assert "flood" in hazard_types
    assert "fire" in hazard_types

def test_collection_stats(temp_kb):
    """Verify collection stats accurately reflect the ingested database."""
    stats = temp_kb.get_collection_stats()
    assert "total_sops" in stats
    assert "by_hazard" in stats
    assert stats["total_sops"] == 2
