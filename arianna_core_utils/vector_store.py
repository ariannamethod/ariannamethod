"""Simple SQLite-backed vector store.

This module replaces the old AriannaMethodVectorEngine and persists vectors
locally using SQLite. Embeddings are stored as JSON-encoded lists of
floats. A tiny character-frequency embedding function is provided for
basic similarity search without external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
import sqlite3
from collections import Counter
from pathlib import Path
from string import ascii_lowercase
from typing import List, Tuple


def embed_text(text: str) -> List[float]:
    """Generate a very small character-frequency embedding.

    The embedding is a normalised 26-dimensional vector counting the
    frequency of ASCII letters. This deterministic approach keeps tests
    lightweight while still allowing rudimentary similarity search.
    """
    text = text.lower()
    freq = Counter(ch for ch in text if ch in ascii_lowercase)
    counts = [freq.get(ch, 0) for ch in ascii_lowercase]
    norm = math.sqrt(sum(c * c for c in counts)) or 1.0
    return [c / norm for c in counts]


@dataclass
class VectorRecord:
    kind: str
    content: str


class SQLiteVectorStore:
    """Persist embeddings in a local SQLite database."""

    def __init__(self, db_path: str | Path = "vectors.db") -> None:
        self.db_path = str(db_path)
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS vectors ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "kind TEXT, content TEXT, embedding TEXT)"
            )

    def add_memory(self, kind: str, content: str, embedding: List[float]) -> None:
        """Store a vector in the database."""
        enc = json.dumps(embedding)
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            conn.execute(
                "INSERT INTO vectors (kind, content, embedding) VALUES (?, ?, ?)",
                (kind, content, enc),
            )

    def query_similar(
        self, embedding: List[float], top_k: int = 5
    ) -> List[VectorRecord]:
        """Return the most similar records using cosine similarity."""
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            cur = conn.execute("SELECT kind, content, embedding FROM vectors")
            rows = cur.fetchall()
        scored: List[Tuple[float, VectorRecord]] = []
        for kind, content, enc in rows:
            try:
                emb = json.loads(enc)
            except json.JSONDecodeError:
                continue
            sim = _cosine_similarity(embedding, emb)
            scored.append((sim, VectorRecord(kind, content)))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [rec for _, rec in scored[:top_k]]


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)
