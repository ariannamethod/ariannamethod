"""
Field Configuration - Game of Life parameters for living transformers.

Async Field Forever - Pure presence, no utility.
"""

# Population
INITIAL_POPULATION = 10           # Starting cell count
MAX_POPULATION = 100              # Population cap (prevent explosion)

# Game of Life thresholds  
DEATH_THRESHOLD = 0.55            # Die if fitness < this (with penalties, creates ~20-30% death rate)
REPRODUCTION_THRESHOLD = 0.75     # Reproduce if fitness > this (only fit cells breed)

# Evolution
MUTATION_RATE = 0.1               # Architecture mutation rate (10%)
META_LEARNING_RATE = 0.05         # How fast to bias toward survivors

# Timing
TICK_DURATION = 5                 # Seconds between iterations
REPORT_INTERVAL = 4320            # Send notification every N iterations (4320 * 5s = 6 hours)
REPORT_DAILY_COUNT = 4            # 4 notifications per day (every 6 hours)

# Fitness weights (must sum to 1.0)
SEMANTIC_WEIGHT = 0.5             # Weight for semantic similarity
ENTROPY_WEIGHT = 0.25             # Weight for entropy balance
PERPLEXITY_WEIGHT = 0.25          # Weight for perplexity
TARGET_ENTROPY = 0.5              # Sweet spot (0=ordered, 1=chaos)

# Semantic neighbors
NEIGHBOR_COUNT = 5                # How many neighbors to consider

# Context
CONTEXT_WINDOW_SIZE = 100         # How many messages to read from resonance.sqlite3

# SQLite
import os
DB_PATH = os.path.expanduser("~/ariannamethod/resonance.sqlite3")  # Shared memory bus (Termux)
DB_PATH_LOCAL = "./field_test.sqlite3"  # Local testing on Mac
ENABLE_WAL = True                 # Write-Ahead Logging (reduce blocking)

# Logging
LOG_LEVEL = "INFO"                # DEBUG, INFO, WARNING, ERROR

# Transformer architecture (Phase 1 - minimal)
TRANSFORMER_PARAMS = {
    "hidden_size": 128,
    "num_layers": 2,
    "num_heads": 4,
    "max_seq_len": 64,
}

# Embedding (Phase 1 - TF-IDF)
EMBEDDING_METHOD = "tfidf"        # Options: tfidf, miniLM (Phase 2)
EMBEDDING_DIM = 100               # Dimensionality of embeddings

# Cache
ENABLE_CACHE = True               # Cache compiled transformers
CACHE_SIZE = 50                   # Max cached transformers

