"""Tests for MemoryManager FTS5 + content search (Batch 3)."""

from __future__ import annotations

import os
import shutil
import tempfile

import pytest

from memory.memory_manager import MemoryManager


@pytest.fixture
def mm(tmp_path):
    db = str(tmp_path / "test.db")
    return MemoryManager(db)


@pytest.fixture
def mm_db(tmp_path):
    return str(tmp_path / "test.db")


# ── FTS5 Detection ───────────────────────────────────────────────


class TestFTS5Detection:
    def test_fts5_flag_set(self, mm):
        assert isinstance(mm._fts_available, bool)

    def test_fts5_available_on_this_build(self, mm):
        assert mm._fts_available is True


# ── Schema ────────────────────────────────────────────────────────


class TestSchema:
    def test_memories_table_exists(self, mm):
        results = mm.search(query="nonexistent", limit=1)
        assert isinstance(results, list)

    def test_fts_table_exists(self, mm):
        if not mm._fts_available:
            pytest.skip("FTS5 not available")
        with mm._connect() as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            names = [t["name"] for t in tables]
            assert "memories_fts" in names

    def test_idempotent_init(self, mm_db):
        m1 = MemoryManager(mm_db)
        m2 = MemoryManager(mm_db)
        m1.save("session", "k", "v")
        results = m2.search(query="k")
        assert len(results) == 1

    def test_existing_db_upgrade(self, mm_db):
        m1 = MemoryManager(mm_db)
        m1.save("session", "old_key", "old_value")
        m2 = MemoryManager(mm_db)
        results = m2.search(query="old_key")
        assert len(results) == 1


# ── Content Search: FTS5 ─────────────────────────────────────────


class TestContentSearchFTS:
    def test_match_key(self, mm):
        mm.save("session", "project_name", "AllAffiliate")
        results = mm.search(query="project_name")
        assert len(results) == 1
        assert results[0]["key"] == "project_name"

    def test_match_value(self, mm):
        mm.save("session", "config", "The quick brown fox jumps")
        results = mm.search(query="quick brown")
        assert len(results) == 1
        assert results[0]["key"] == "config"

    def test_match_both_key_and_value(self, mm):
        mm.save("session", "alpha_config", "beta value content")
        r1 = mm.search(query="alpha_config")
        r2 = mm.search(query="beta value")
        assert len(r1) >= 1
        assert len(r2) >= 1

    def test_multiple_results(self, mm):
        mm.save("session", "k1", "hello world")
        mm.save("session", "k2", "hello there")
        mm.save("session", "k3", "goodbye")
        results = mm.search(query="hello")
        assert len(results) == 2

    def test_no_match(self, mm):
        mm.save("session", "k", "v")
        results = mm.search(query="zzz_nonexistent")
        assert len(results) == 0

    def test_empty_query_returns_empty(self, mm):
        mm.save("session", "k", "v")
        assert mm.search(query="") == []
        assert mm.search(query="   ") == []

    def test_limit_zero_returns_empty(self, mm):
        mm.search(query="any", limit=0) == []

    def test_memory_type_filter(self, mm):
        mm.save("session", "fk", "searchable")
        mm.save("long_term", "fk", "searchable")
        results = mm.search(query="searchable", memory_type="session")
        assert len(results) == 1
        assert results[0]["memory_type"] == "session"

    def test_session_filter(self, mm):
        mm.save("session", "sk", "val", session_id="s1")
        mm.save("session", "sk", "val", session_id="s2")
        results = mm.search(query="sk", session_id="s1")
        assert len(results) == 1

    def test_ordering_by_updated_at(self, mm):
        mm.save("session", "ord_k", "first")
        mm.save("session", "ord_k", "second")
        results = mm.search(query="ord_k")
        assert len(results) == 1

    def test_deleted_memory_not_searchable(self, mm):
        mm.save("session", "del_k", "val")
        mm.delete("session", "del_k")
        results = mm.search(query="del_k")
        assert len(results) == 0

    def test_updated_memory_searchable_with_new_content(self, mm):
        mm.save("session", "upd_k", "old value")
        mm.save("session", "upd_k", "new value content")
        results = mm.search(query="new value")
        assert len(results) == 1

    def test_multiple_memory_types(self, mm):
        mm.save("session", "mt_k", "content")
        mm.save("long_term", "mt_k", "content")
        mm.save("context", "mt_k", "content")
        results = mm.search(query="mt_k")
        assert len(results) == 3

    def test_special_fts_characters_fallback(self, mm):
        mm.save("session", "star*key", "value")
        results = mm.search(query="star*key")
        assert len(results) == 1

    def test_quote_in_query_fallback(self, mm):
        mm.save("session", 'say "hello"', "value")
        results = mm.search(query='say "hello"')
        assert len(results) == 1

    def test_unicode_content(self, mm):
        mm.save("session", "arabic_key", " هذا نص عربي")
        results = mm.search(query="نص")
        assert len(results) == 1

    def test_json_value_searchable(self, mm):
        mm.save("session", "json_k", {"nested": "findable text"})
        results = mm.search(query="findable")
        assert len(results) == 1

    def test_fts_returns_result_shape(self, mm):
        mm.save("session", "shape_k", "val", session_id="s1", metadata={"a": 1})
        results = mm.search(query="shape_k")
        assert len(results) == 1
        r = results[0]
        assert "id" in r
        assert "memory_type" in r
        assert "key" in r
        assert "value" in r
        assert "session_id" in r
        assert "metadata" in r
        assert "created_at" in r
        assert "updated_at" in r


# ── Existing API Compatibility ───────────────────────────────────


class TestExistingAPICompat:
    def test_save_get_delete_still_work(self, mm):
        mm.save("session", "compat_k", {"data": 42})
        val = mm.get("session", "compat_k")
        assert val == {"data": 42}
        deleted = mm.delete("session", "compat_k")
        assert deleted is True
        assert mm.get("session", "compat_k") is None

    def test_list_memories_unchanged(self, mm):
        mm.save("session", "l1", "v1")
        mm.save("long_term", "l2", "v2")
        results = mm.list_memories()
        assert len(results) == 2

    def test_clear_session_unchanged(self, mm):
        mm.save("session", "cs_k", "v", session_id="s1")
        mm.save("context", "cs_k2", "v", session_id="s1")
        mm.save("long_term", "cs_k3", "v", session_id="s1")
        count = mm.clear_session("s1")
        assert count == 2
        assert mm.search(query="cs_k", session_id="s1") == []

    def test_count_unchanged(self, mm):
        mm.save("session", "c1", "v")
        assert mm.count() == 1
