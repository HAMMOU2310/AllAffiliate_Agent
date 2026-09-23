import os
import shutil
import tempfile
import unittest

from memory.memory_manager import MemoryManager


class MemoryManagerConstructionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "test_mem.db")

    def tearDown(self):
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def test_creates_database_file(self):
        MemoryManager(self.db_path)
        self.assertTrue(os.path.exists(self.db_path))

    def test_creates_parent_directories(self):
        nested = os.path.join(self.tmp, "a", "b", "mem.db")
        MemoryManager(nested)
        self.assertTrue(os.path.exists(nested))


class MemoryManagerValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "test_mem.db")
        self.mm = MemoryManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def test_invalid_memory_type_raises(self):
        with self.assertRaises(ValueError):
            self.mm.save(memory_type="invalid", key="k", value="v")

    def test_invalid_memory_type_get_raises(self):
        with self.assertRaises(ValueError):
            self.mm.get(memory_type="bad", key="k")

    def test_invalid_memory_type_delete_raises(self):
        with self.assertRaises(ValueError):
            self.mm.delete(memory_type="bad", key="k")

    def test_empty_key_raises(self):
        with self.assertRaises(ValueError):
            self.mm.save(memory_type="session", key="", value="v")

    def test_whitespace_key_raises(self):
        with self.assertRaises(ValueError):
            self.mm.save(memory_type="session", key="   ", value="v")


class MemoryManagerSaveGetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "test_mem.db")
        self.mm = MemoryManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def test_save_returns_id(self):
        mid = self.mm.save(memory_type="session", key="k1", value="v1")
        self.assertIsInstance(mid, str)
        self.assertGreater(len(mid), 0)

    def test_get_returns_value(self):
        self.mm.save(memory_type="session", key="k2", value="v2")
        val = self.mm.get(memory_type="session", key="k2")
        self.assertEqual(val, "v2")

    def test_get_missing_returns_none(self):
        val = self.mm.get(memory_type="session", key="nonexistent")
        self.assertIsNone(val)

    def test_save_complex_value(self):
        data = {"list": [1, 2], "nested": {"a": True}}
        self.mm.save(memory_type="long_term", key="complex", value=data)
        val = self.mm.get(memory_type="long_term", key="complex")
        self.assertEqual(val, data)

    def test_upsert_updates_existing(self):
        self.mm.save(memory_type="session", key="u1", value="first")
        self.mm.save(memory_type="session", key="u1", value="second")
        val = self.mm.get(memory_type="session", key="u1")
        self.assertEqual(val, "second")

    def test_upsert_returns_same_id(self):
        id1 = self.mm.save(memory_type="session", key="u2", value="v1")
        id2 = self.mm.save(memory_type="session", key="u2", value="v2")
        self.assertEqual(id1, id2)

    def test_session_scoped_isolation(self):
        self.mm.save(memory_type="session", key="sk", value="sval", session_id="s1")
        val = self.mm.get(memory_type="session", key="sk", session_id="s2")
        self.assertIsNone(val)

    def test_global_and_session_coexist(self):
        self.mm.save(memory_type="session", key="gk", value="global")
        self.mm.save(memory_type="session", key="gk", value="scoped", session_id="s1")
        self.assertEqual(self.mm.get(memory_type="session", key="gk"), "global")
        self.assertEqual(self.mm.get(memory_type="session", key="gk", session_id="s1"), "scoped")


class MemoryManagerGetEntryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "test_mem.db")
        self.mm = MemoryManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def test_get_entry_returns_full_record(self):
        self.mm.save(memory_type="context", key="e1", value="ev", metadata={"src": "test"})
        entry = self.mm.get_entry(memory_type="context", key="e1")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["key"], "e1")
        self.assertEqual(entry["value"], "ev")
        self.assertEqual(entry["memory_type"], "context")
        self.assertIn("id", entry)
        self.assertIn("created_at", entry)

    def test_get_entry_missing_returns_none(self):
        entry = self.mm.get_entry(memory_type="session", key="nope")
        self.assertIsNone(entry)

    def test_get_entry_metadata_preserved(self):
        self.mm.save(memory_type="long_term", key="m1", value="v", metadata={"k": 42})
        entry = self.mm.get_entry(memory_type="long_term", key="m1")
        self.assertEqual(entry["metadata"], {"k": 42})


class MemoryManagerSearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "test_mem.db")
        self.mm = MemoryManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def test_search_finds_matching_keys(self):
        self.mm.save(memory_type="session", key="alpha_1", value="a")
        self.mm.save(memory_type="session", key="alpha_2", value="b")
        self.mm.save(memory_type="session", key="beta_1", value="c")
        results = self.mm.search(query="alpha")
        self.assertEqual(len(results), 2)

    def test_search_no_match(self):
        self.mm.save(memory_type="session", key="xyz", value="v")
        results = self.mm.search(query="alpha")
        self.assertEqual(len(results), 0)

    def test_search_with_memory_type_filter(self):
        self.mm.save(memory_type="session", key="filter_k", value="v")
        self.mm.save(memory_type="long_term", key="filter_k", value="v")
        results = self.mm.search(query="filter", memory_type="session")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["memory_type"], "session")

    def test_search_with_session_filter(self):
        self.mm.save(memory_type="session", key="sf_k", value="v", session_id="s1")
        self.mm.save(memory_type="session", key="sf_k", value="v", session_id="s2")
        results = self.mm.search(query="sf_k", session_id="s1")
        self.assertEqual(len(results), 1)

    def test_search_limit_zero_returns_empty(self):
        results = self.mm.search(query="any", limit=0)
        self.assertEqual(results, [])

    def test_search_invalid_memory_type_raises(self):
        with self.assertRaises(ValueError):
            self.mm.search(query="k", memory_type="bad")


class MemoryManagerListTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "test_mem.db")
        self.mm = MemoryManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def test_list_returns_all(self):
        self.mm.save(memory_type="session", key="l1", value="v1")
        self.mm.save(memory_type="long_term", key="l2", value="v2")
        results = self.mm.list_memories()
        self.assertEqual(len(results), 2)

    def test_list_with_type_filter(self):
        self.mm.save(memory_type="session", key="lt1", value="v1")
        self.mm.save(memory_type="long_term", key="lt2", value="v2")
        results = self.mm.list_memories(memory_type="session")
        self.assertEqual(len(results), 1)

    def test_list_with_session_filter(self):
        self.mm.save(memory_type="session", key="ls1", value="v1", session_id="s1")
        self.mm.save(memory_type="session", key="ls2", value="v2", session_id="s2")
        results = self.mm.list_memories(session_id="s1")
        self.assertEqual(len(results), 1)

    def test_list_limit_zero_returns_empty(self):
        results = self.mm.list_memories(limit=0)
        self.assertEqual(results, [])

    def test_list_invalid_memory_type_raises(self):
        with self.assertRaises(ValueError):
            self.mm.list_memories(memory_type="bad")


class MemoryManagerDeleteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "test_mem.db")
        self.mm = MemoryManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def test_delete_existing_returns_true(self):
        self.mm.save(memory_type="session", key="d1", value="v")
        self.assertTrue(self.mm.delete(memory_type="session", key="d1"))

    def test_delete_nonexistent_returns_false(self):
        self.assertFalse(self.mm.delete(memory_type="session", key="nope"))

    def test_delete_removes_entry(self):
        self.mm.save(memory_type="session", key="d2", value="v")
        self.mm.delete(memory_type="session", key="d2")
        self.assertIsNone(self.mm.get(memory_type="session", key="d2"))

    def test_delete_session_scoped(self):
        self.mm.save(memory_type="session", key="ds", value="v", session_id="s1")
        self.assertTrue(self.mm.delete(memory_type="session", key="ds", session_id="s1"))
        self.assertIsNone(self.mm.get(memory_type="session", key="ds", session_id="s1"))


class MemoryManagerClearSessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "test_mem.db")
        self.mm = MemoryManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def test_clear_session_removes_session_and_context(self):
        self.mm.save(memory_type="session", key="cs1", value="v", session_id="s1")
        self.mm.save(memory_type="context", key="cs2", value="v", session_id="s1")
        count = self.mm.clear_session("s1")
        self.assertEqual(count, 2)
        self.assertIsNone(self.mm.get(memory_type="session", key="cs1", session_id="s1"))
        self.assertIsNone(self.mm.get(memory_type="context", key="cs2", session_id="s1"))

    def test_clear_session_preserves_long_term(self):
        self.mm.save(memory_type="long_term", key="lt", value="persistent", session_id="s1")
        self.mm.save(memory_type="session", key="st", value="temp", session_id="s1")
        self.mm.clear_session("s1")
        self.assertEqual(self.mm.get(memory_type="long_term", key="lt", session_id="s1"), "persistent")

    def test_clear_session_empty_id_raises(self):
        with self.assertRaises(ValueError):
            self.mm.clear_session("")

    def test_clear_session_returns_zero_when_no_match(self):
        count = self.mm.clear_session("nonexistent")
        self.assertEqual(count, 0)


class MemoryManagerCountTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "test_mem.db")
        self.mm = MemoryManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def test_count_empty(self):
        self.assertEqual(self.mm.count(), 0)

    def test_count_with_entries(self):
        self.mm.save(memory_type="session", key="c1", value="v")
        self.mm.save(memory_type="long_term", key="c2", value="v")
        self.assertEqual(self.mm.count(), 2)

    def test_count_by_type(self):
        self.mm.save(memory_type="session", key="ct1", value="v")
        self.mm.save(memory_type="long_term", key="ct2", value="v")
        self.assertEqual(self.mm.count(memory_type="session"), 1)

    def test_count_by_session(self):
        self.mm.save(memory_type="session", key="cs1", value="v", session_id="s1")
        self.mm.save(memory_type="session", key="cs2", value="v", session_id="s2")
        self.assertEqual(self.mm.count(session_id="s1"), 1)

    def test_count_invalid_memory_type_raises(self):
        with self.assertRaises(ValueError):
            self.mm.count(memory_type="bad")


class MemoryManagerHealthCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "test_mem.db")
        self.mm = MemoryManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def test_health_check_ok(self):
        self.assertTrue(self.mm.health_check())

    def test_health_check_corrupt_db(self):
        self.mm.database_path = "/nonexistent/path/memory.db"
        self.assertFalse(self.mm.health_check())


class MemoryManagerSerializationTests(unittest.TestCase):
    def test_serialize_dict(self):
        result = MemoryManager._serialize({"a": 1})
        self.assertIn("a", result)

    def test_serialize_list(self):
        result = MemoryManager._serialize([1, 2, 3])
        self.assertIn("1", result)

    def test_deserialize_valid(self):
        result = MemoryManager._deserialize('{"key": "val"}')
        self.assertEqual(result, {"key": "val"})

    def test_deserialize_none(self):
        self.assertIsNone(MemoryManager._deserialize(None))

    def test_deserialize_invalid_json(self):
        result = MemoryManager._deserialize("not json {{{")
        self.assertEqual(result, "not json {{{")


if __name__ == "__main__":
    unittest.main()
