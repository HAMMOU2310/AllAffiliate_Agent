"""
memory/memory_manager.py

Core memory management layer for AllAffiliate_Agent.

Responsibilities:
- Session memory
- Long-term memory
- Context memory
- Persistent storage
- Memory retrieval
- Memory deletion

This module contains memory implementation logic.
Agents should only coordinate with this layer and must not
contain memory storage logic themselves.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class MemoryManager:
    """
    Central manager for the project's memory system.

    Memory types:
        session     -> temporary/session-related information
        long_term   -> persistent information intended to survive sessions
        context     -> contextual information used during execution
    """

    VALID_MEMORY_TYPES = {
        "session",
        "long_term",
        "context",
    }

    def __init__(self, database_path: str = "database/memory.db") -> None:
        self.database_path = Path(database_path)

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._fts_available = self._check_fts5()
        self._initialize_database()

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        """
        Create a database connection.
        """

        connection = sqlite3.connect(
            self.database_path,
        )

        connection.row_factory = sqlite3.Row

        return connection

    @staticmethod
    def _check_fts5() -> bool:
        """Detect whether FTS5 is available in this SQLite build."""
        try:
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE VIRTUAL TABLE _fts_test USING fts5(content)")
            conn.execute("DROP TABLE _fts_test")
            conn.close()
            return True
        except sqlite3.OperationalError:
            return False

    def _initialize_database(self) -> None:
        """
        Initialize the memory database and required table.
        """

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    memory_type TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memories_type
                ON memories(memory_type)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memories_session
                ON memories(session_id)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memories_key
                ON memories(key)
                """
            )

            if self._fts_available:
                self._initialize_fts(connection)

    def _initialize_fts(self, connection: sqlite3.Connection) -> None:
        """Create the FTS5 virtual table and backfill from memories."""
        connection.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
            USING fts5(
                memory_id UNINDEXED,
                key,
                value
            )
            """
        )

        existing_count = connection.execute(
            "SELECT COUNT(*) FROM memories_fts"
        ).fetchone()[0]

        if existing_count == 0:
            connection.execute(
                """
                INSERT INTO memories_fts (memory_id, key, value)
                SELECT id, key, value FROM memories
                """
            )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_memory_type(self, memory_type: str) -> None:
        """
        Validate a memory type.
        """

        if memory_type not in self.VALID_MEMORY_TYPES:
            raise ValueError(
                f"Invalid memory type: {memory_type}. "
                f"Expected one of: "
                f"{', '.join(sorted(self.VALID_MEMORY_TYPES))}"
            )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize(value: Any) -> str:
        """
        Serialize arbitrary Python data to JSON.
        """

        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def _deserialize(value: str | None) -> Any:
        """
        Deserialize JSON data.
        """

        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(
        self,
        memory_type: str,
        key: str,
        value: Any,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Save or update a memory entry.

        Returns:
            Memory ID.
        """

        self._validate_memory_type(memory_type)

        if not key or not key.strip():
            raise ValueError("Memory key cannot be empty.")

        now = datetime.now(timezone.utc).isoformat()

        serialized_value = self._serialize(value)
        serialized_metadata = self._serialize(metadata or {})

        with self._connect() as connection:

            existing = connection.execute(
                """
                SELECT id
                FROM memories
                WHERE memory_type = ?
                  AND key = ?
                  AND (
                      session_id = ?
                      OR (
                          session_id IS NULL
                          AND ? IS NULL
                      )
                  )
                LIMIT 1
                """,
                (
                    memory_type,
                    key,
                    session_id,
                    session_id,
                ),
            ).fetchone()

            if existing:

                memory_id = existing["id"]

                connection.execute(
                    """
                    UPDATE memories
                    SET value = ?,
                        metadata = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        serialized_value,
                        serialized_metadata,
                        now,
                        memory_id,
                    ),
                )

                if self._fts_available:
                    connection.execute(
                        """
                        DELETE FROM memories_fts
                        WHERE memory_id = ?
                        """,
                        (memory_id,),
                    )
                    connection.execute(
                        """
                        INSERT INTO memories_fts (memory_id, key, value)
                        VALUES (?, ?, ?)
                        """,
                        (memory_id, key, serialized_value),
                    )

                return memory_id

            memory_id = str(uuid.uuid4())

            connection.execute(
                """
                INSERT INTO memories (
                    id,
                    memory_type,
                    key,
                    value,
                    session_id,
                    metadata,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory_id,
                    memory_type,
                    key,
                    serialized_value,
                    session_id,
                    serialized_metadata,
                    now,
                    now,
                ),
            )

            if self._fts_available:
                connection.execute(
                    """
                    INSERT INTO memories_fts (memory_id, key, value)
                    VALUES (?, ?, ?)
                    """,
                    (memory_id, key, serialized_value),
                )

            return memory_id

    # ------------------------------------------------------------------
    # Get
    # ------------------------------------------------------------------

    def get(
        self,
        memory_type: str,
        key: str,
        session_id: str | None = None,
    ) -> Any | None:
        """
        Retrieve a memory value by type and key.
        """

        self._validate_memory_type(memory_type)

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT value
                FROM memories
                WHERE memory_type = ?
                  AND key = ?
                  AND (
                      session_id = ?
                      OR (
                          session_id IS NULL
                          AND ? IS NULL
                      )
                  )
                LIMIT 1
                """,
                (
                    memory_type,
                    key,
                    session_id,
                    session_id,
                ),
            ).fetchone()

        if row is None:
            return None

        return self._deserialize(row["value"])

    # ------------------------------------------------------------------
    # Get entry
    # ------------------------------------------------------------------

    def get_entry(
        self,
        memory_type: str,
        key: str,
        session_id: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Retrieve a complete memory entry.
        """

        self._validate_memory_type(memory_type)

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT
                    id,
                    memory_type,
                    key,
                    value,
                    session_id,
                    metadata,
                    created_at,
                    updated_at
                FROM memories
                WHERE memory_type = ?
                  AND key = ?
                  AND (
                      session_id = ?
                      OR (
                          session_id IS NULL
                          AND ? IS NULL
                      )
                  )
                LIMIT 1
                """,
                (
                    memory_type,
                    key,
                    session_id,
                    session_id,
                ),
            ).fetchone()

        if row is None:
            return None

        return {
            "id": row["id"],
            "memory_type": row["memory_type"],
            "key": row["key"],
            "value": self._deserialize(row["value"]),
            "session_id": row["session_id"],
            "metadata": self._deserialize(row["metadata"]) or {},
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        memory_type: str | None = None,
        session_id: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Search memory entries by key and content.

        Uses FTS5 when available for full-text search across key and
        value fields.  Falls back to LIKE-based key search when FTS5
        is unavailable or the query contains FTS-special characters.
        """

        if limit <= 0:
            return []

        if not query or not query.strip():
            return []

        if memory_type is not None:
            self._validate_memory_type(memory_type)

        if self._fts_available and self._is_safe_fts_query(query):
            return self._search_fts(query, memory_type, session_id, limit)

        return self._search_like(query, memory_type, session_id, limit)

    @staticmethod
    def _is_safe_fts_query(query: str) -> bool:
        """Return True if query is safe for FTS5 MATCH syntax."""
        unsafe = set('*"\'():;^[]{}\\')
        return not any(c in unsafe for c in query)

    def _search_fts(
        self,
        query: str,
        memory_type: str | None,
        session_id: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        """FTS5-based content search across key and value."""
        fts_query = self._build_fts_query(query)

        sql = """
            SELECT
                m.id,
                m.memory_type,
                m.key,
                m.value,
                m.session_id,
                m.metadata,
                m.created_at,
                m.updated_at
            FROM memories m
            JOIN memories_fts fts ON fts.memory_id = m.id
            WHERE memories_fts MATCH ?
        """

        parameters: list[Any] = [fts_query]

        if memory_type is not None:
            sql += " AND m.memory_type = ?"
            parameters.append(memory_type)

        if session_id is not None:
            sql += " AND m.session_id = ?"
            parameters.append(session_id)

        sql += " ORDER BY m.updated_at DESC LIMIT ?"
        parameters.append(limit)

        with self._connect() as connection:
            rows = connection.execute(sql, parameters).fetchall()

        return [
            {
                "id": row["id"],
                "memory_type": row["memory_type"],
                "key": row["key"],
                "value": self._deserialize(row["value"]),
                "session_id": row["session_id"],
                "metadata": self._deserialize(row["metadata"]) or {},
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    @staticmethod
    def _build_fts_query(query: str) -> str:
        """Build an FTS5 MATCH query that searches key and value."""
        tokens = query.split()
        if not tokens:
            return '""'
        parts = [f'"{t}"' for t in tokens]
        return " OR ".join(parts)

    def _search_like(
        self,
        query: str,
        memory_type: str | None,
        session_id: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Fallback LIKE-based search across key and value."""
        sql = """
            SELECT
                id,
                memory_type,
                key,
                value,
                session_id,
                metadata,
                created_at,
                updated_at
            FROM memories
            WHERE key LIKE ?
               OR value LIKE ?
        """

        like_param = f"%{query}%"
        parameters: list[Any] = [like_param, like_param]

        if memory_type is not None:
            sql += " AND memory_type = ?"
            parameters.append(memory_type)

        if session_id is not None:
            sql += " AND session_id = ?"
            parameters.append(session_id)

        sql += " ORDER BY updated_at DESC LIMIT ?"
        parameters.append(limit)

        with self._connect() as connection:
            rows = connection.execute(sql, parameters).fetchall()

        seen_ids: set[str] = set()
        results: list[dict[str, Any]] = []

        for row in rows:
            if row["id"] in seen_ids:
                continue
            seen_ids.add(row["id"])
            results.append({
                "id": row["id"],
                "memory_type": row["memory_type"],
                "key": row["key"],
                "value": self._deserialize(row["value"]),
                "session_id": row["session_id"],
                "metadata": self._deserialize(row["metadata"]) or {},
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            })

        return results

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def list_memories(
        self,
        memory_type: str | None = None,
        session_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Return stored memories.
        """

        if limit <= 0:
            return []

        if memory_type is not None:
            self._validate_memory_type(memory_type)

        sql = """
            SELECT
                id,
                memory_type,
                key,
                value,
                session_id,
                metadata,
                created_at,
                updated_at
            FROM memories
            WHERE 1 = 1
        """

        parameters: list[Any] = []

        if memory_type is not None:
            sql += " AND memory_type = ?"
            parameters.append(memory_type)

        if session_id is not None:
            sql += " AND session_id = ?"
            parameters.append(session_id)

        sql += """
            ORDER BY updated_at DESC
            LIMIT ?
        """

        parameters.append(limit)

        with self._connect() as connection:
            rows = connection.execute(
                sql,
                parameters,
            ).fetchall()

        return [
            {
                "id": row["id"],
                "memory_type": row["memory_type"],
                "key": row["key"],
                "value": self._deserialize(row["value"]),
                "session_id": row["session_id"],
                "metadata": self._deserialize(row["metadata"]) or {},
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(
        self,
        memory_type: str,
        key: str,
        session_id: str | None = None,
    ) -> bool:
        """
        Delete a memory entry.

        Returns:
            True if an entry was deleted.
            False if no matching entry existed.
        """

        self._validate_memory_type(memory_type)

        with self._connect() as connection:

            if self._fts_available:
                ids_to_delete = connection.execute(
                    """
                    SELECT id FROM memories
                    WHERE memory_type = ?
                      AND key = ?
                      AND (
                          session_id = ?
                          OR (
                              session_id IS NULL
                              AND ? IS NULL
                          )
                      )
                    """,
                    (memory_type, key, session_id, session_id),
                ).fetchall()

                for row in ids_to_delete:
                    connection.execute(
                        "DELETE FROM memories_fts WHERE memory_id = ?",
                        (row["id"],),
                    )

            cursor = connection.execute(
                """
                DELETE FROM memories
                WHERE memory_type = ?
                  AND key = ?
                  AND (
                      session_id = ?
                      OR (
                          session_id IS NULL
                          AND ? IS NULL
                      )
                  )
                """,
                (
                    memory_type,
                    key,
                    session_id,
                    session_id,
                ),
            )

            return cursor.rowcount > 0

    # ------------------------------------------------------------------
    # Clear session
    # ------------------------------------------------------------------

    def clear_session(self, session_id: str) -> int:
        """
        Delete all session and context memories belonging
        to a specific session.

        Long-term memories are intentionally preserved.
        """

        if not session_id:
            raise ValueError("Session ID cannot be empty.")

        with self._connect() as connection:

            if self._fts_available:
                ids_to_delete = connection.execute(
                    """
                    SELECT id FROM memories
                    WHERE session_id = ?
                      AND memory_type IN ('session', 'context')
                    """,
                    (session_id,),
                ).fetchall()

                for row in ids_to_delete:
                    connection.execute(
                        "DELETE FROM memories_fts WHERE memory_id = ?",
                        (row["id"],),
                    )

            cursor = connection.execute(
                """
                DELETE FROM memories
                WHERE session_id = ?
                  AND memory_type IN ('session', 'context')
                """,
                (session_id,),
            )

            return cursor.rowcount

    # ------------------------------------------------------------------
    # Count
    # ------------------------------------------------------------------

    def count(
        self,
        memory_type: str | None = None,
        session_id: str | None = None,
    ) -> int:
        """
        Return the number of stored memory entries.
        """

        if memory_type is not None:
            self._validate_memory_type(memory_type)

        sql = """
            SELECT COUNT(*)
            FROM memories
            WHERE 1 = 1
        """

        parameters: list[Any] = []

        if memory_type is not None:
            sql += " AND memory_type = ?"
            parameters.append(memory_type)

        if session_id is not None:
            sql += " AND session_id = ?"
            parameters.append(session_id)

        with self._connect() as connection:
            row = connection.execute(
                sql,
                parameters,
            ).fetchone()

        return int(row[0])

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def health_check(self) -> bool:
        """
        Verify that the memory database is accessible.
        """

        try:
            with self._connect() as connection:
                connection.execute(
                    "SELECT 1"
                ).fetchone()

            return True

        except sqlite3.Error:
            return False

    def close(self) -> None:
        """Release memory resources.

        MemoryManager uses ephemeral connections, so this is a
        no-op that establishes the lifecycle contract for
        ServiceContainer.shutdown().
        """
        pass