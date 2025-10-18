"""
Resonance Bridge - Connect Field to resonance.sqlite3 shared memory bus.

Field reads context from ecosystem conversations.
Field writes metrics for other AI entities to observe.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any


class ResonanceBridge:
    """Bridge between Field and ecosystem memory."""
    
    def __init__(self, db_path: str):
        """
        Initialize bridge to resonance.sqlite3.
        
        Args:
            db_path: Path to SQLite database
        """
        # Expand ~ to home directory
        self.db_path = os.path.expanduser(db_path)
        
        # Initialize Field tables
        self._init_field_tables()
        
        # Enable WAL mode for better concurrency
        from config import ENABLE_WAL
        if ENABLE_WAL:
            self._enable_wal()
    
    def _enable_wal(self):
        """Enable Write-Ahead Logging mode."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.close()
    
    def _init_field_tables(self):
        """Create Field-specific tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Field state table (aggregate metrics)
        c.execute("""
            CREATE TABLE IF NOT EXISTS field_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                iteration INTEGER,
                cell_count INTEGER,
                avg_resonance REAL,
                avg_age REAL,
                births INTEGER,
                deaths INTEGER
            )
        """)
        
        # Field cells table (individual cells)
        c.execute("""
            CREATE TABLE IF NOT EXISTS field_cells (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cell_id TEXT,
                age INTEGER,
                resonance_score REAL,
                entropy REAL,
                perplexity REAL,
                fitness REAL,
                architecture TEXT,
                status TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def fetch_recent_context(self, limit: int = 100) -> str:
        """
        Fetch recent context from resonance_notes.
        
        This is the "food" for Field - conversations from Arianna/Monday/etc.
        
        Args:
            limit: Number of recent messages
        
        Returns:
            Combined context string
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # Try to read from resonance_notes (Arianna Method standard table)
            c.execute("""
                SELECT content FROM resonance_notes 
                ORDER BY id DESC LIMIT ?
            """, (limit,))
            
            rows = c.fetchall()
            
            if not rows:
                # Fallback: create sample context
                return "Field initializing... No prior context available."
            
            # Combine messages into single context
            context = " ".join(row[0] for row in rows if row[0])
            
            return context
        
        except sqlite3.OperationalError:
            # Table doesn't exist yet - return default
            return "Field initializing... Awaiting ecosystem conversations."
        
        finally:
            conn.close()
    
    def log_field_state(self, cells: List, iteration: int, births: int, deaths: int):
        """
        Log current field state (aggregate metrics).
        
        Args:
            cells: List of all living cells
            iteration: Current iteration number
            births: Number of births this iteration
            deaths: Number of deaths this iteration
        """
        if not cells:
            avg_resonance = 0.0
            avg_age = 0.0
        else:
            avg_resonance = sum(c.resonance_score for c in cells) / len(cells)
            avg_age = sum(c.age for c in cells) / len(cells)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO field_state (timestamp, iteration, cell_count, avg_resonance, avg_age, births, deaths)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            iteration,
            len(cells),
            avg_resonance,
            avg_age,
            births,
            deaths
        ))
        
        conn.commit()
        conn.close()
    
    def log_cell(self, cell):
        """
        Log individual cell state.
        
        Args:
            cell: TransformerCell to log
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO field_cells (
                timestamp, cell_id, age, resonance_score, entropy, perplexity, 
                fitness, architecture, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            cell.id,
            cell.age,
            cell.resonance_score,
            cell.entropy,
            cell.perplexity,
            cell.evaluate_fitness(),
            str(cell.architecture),
            "alive" if cell.alive else "dead"
        ))
        
        conn.commit()
        conn.close()
    
    def get_field_metrics(self, last_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent field state metrics.
        
        This allows other AI entities (Arianna, Claude, Monday) to observe Field.
        
        Args:
            last_n: Number of recent states to fetch
        
        Returns:
            List of state dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT timestamp, iteration, cell_count, avg_resonance, avg_age, births, deaths
            FROM field_state
            ORDER BY id DESC LIMIT ?
        """, (last_n,))
        
        rows = c.fetchall()
        conn.close()
        
        metrics = []
        for row in rows:
            metrics.append({
                "timestamp": row[0],
                "iteration": row[1],
                "cell_count": row[2],
                "avg_resonance": row[3],
                "avg_age": row[4],
                "births": row[5],
                "deaths": row[6],
            })
        
        return metrics
