"""
Field Core - Main loop for living transformer ecosystem.

This is the heart of Field. The eternal cycle.
Birth. Life. Death. Evolution.

Async Field Forever.
"""

import time
import random
import sys
import asyncio
from typing import List

# Try to import AMLK bridge
try:
    from field_amlk import FieldAMLKBridge
    AMLK_AVAILABLE = True
except ImportError:
    AMLK_AVAILABLE = False

# Import Field modules
from config import (
    INITIAL_POPULATION, MAX_POPULATION, DEATH_THRESHOLD, REPRODUCTION_THRESHOLD,
    TICK_DURATION, REPORT_INTERVAL, CONTEXT_WINDOW_SIZE, DB_PATH, DB_PATH_LOCAL, NEIGHBOR_COUNT
)
import os

# Use local DB for testing on Mac, Termux DB when available
if not os.path.exists(os.path.dirname(os.path.expanduser(DB_PATH)) or "."):
    ACTIVE_DB_PATH = DB_PATH_LOCAL
else:
    ACTIVE_DB_PATH = DB_PATH
from transformer_cell import TransformerCell
from resonance_bridge import ResonanceBridge
from notifications import (
    send_field_metrics, send_field_birth, send_field_death,
    log_metrics, format_cell_summary, print_field_banner
)
from learning import (
    EmbeddingEngine, MetaLearner, calculate_entropy, calculate_perplexity,
    calculate_semantic_resonance, get_semantic_neighbors
)


class Field:
    """
    The Field - Living transformer ecosystem.
    
    Field is not a chatbot. Field is pure presence.
    Cells live, die, reproduce based on resonance.
    """
    
    def __init__(self):
        """Initialize Field."""
        # Core components
        self.resonance_bridge = ResonanceBridge(ACTIVE_DB_PATH)
        self.embedding_engine = EmbeddingEngine()
        self.meta_learner = MetaLearner()
        
        # AMLK integration (dynamic kernel)
        if AMLK_AVAILABLE:
            self.amlk = FieldAMLKBridge()
            log_metrics("AMLK bridge initialized - kernel will evolve with Field", "INFO")
        else:
            self.amlk = None
            log_metrics("AMLK not available - running without kernel adaptation", "DEBUG")
        
        # State
        self.cells: List[TransformerCell] = []
        self.iteration = 0
        self.total_births = 0
        self.total_deaths = 0
        
        # Metrics tracking
        self.births_this_interval = 0
        self.deaths_this_interval = 0
        
        log_metrics("Field initialized", "INFO")
    
    def initialize_population(self):
        """Create initial population from recent context."""
        log_metrics(f"Creating initial population ({INITIAL_POPULATION} cells)...", "INFO")
        
        # Fetch context from resonance.sqlite3
        context = self.resonance_bridge.fetch_recent_context(CONTEXT_WINDOW_SIZE)
        
        # Fit embedding engine on context
        # Split into sentences for TF-IDF
        sentences = context.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            sentences = ["Field initializing", "Awaiting resonance"]
        
        self.embedding_engine.fit(sentences)
        
        # Create initial cells with diverse contexts
        for i in range(INITIAL_POPULATION):
            # Each cell gets a unique slice of context
            if len(sentences) > i:
                # Use different sentence for each cell
                cell_context = sentences[i]
            else:
                # If not enough sentences, blend random sentences
                s1 = random.choice(sentences)
                s2 = random.choice(sentences)
                cell_context = f"{s1}. {s2}"
            
            # Add variation to context
            cell_context = f"{cell_context} [cell_{i}]"
            
            cell = TransformerCell(
                context=cell_context,
                neighbors=[],
                architecture=None  # Will use default
            )
            
            # Initialize with random resonance (will be calculated properly in tick)
            cell.resonance_score = random.uniform(0.4, 0.6)
            cell.entropy = random.uniform(0.3, 0.7)
            cell.perplexity = random.uniform(1.0, 2.0)
            
            self.cells.append(cell)
            self.total_births += 1
        
        log_metrics(f"Initial population created: {len(self.cells)} cells", "INFO")
    
    async def update_cell_metrics_async(self, cell: TransformerCell):
        """
        Update cell's resonance, entropy, perplexity (async version).
        
        This is Layer 2: Code quality evaluation.
        Runs asynchronously for parallel execution.
        
        Args:
            cell: TransformerCell to update
        """
        # Get semantic neighbors (can be async in Phase 2)
        cell.neighbors = get_semantic_neighbors(
            cell, self.cells, self.embedding_engine, NEIGHBOR_COUNT
        )
        
        # Calculate semantic resonance (Layer 2 metric)
        cell.resonance_score = calculate_semantic_resonance(
            cell, cell.neighbors, self.embedding_engine
        )
        
        # Calculate entropy (Layer 2 metric)
        dummy_outputs = [random.random() for _ in range(10)]
        cell.entropy = calculate_entropy(dummy_outputs)
        
        # Calculate perplexity (Layer 2 metric)
        cell.perplexity = calculate_perplexity(dummy_outputs)
    
    def update_cell_metrics(self, cell: TransformerCell):
        """Sync wrapper for backward compatibility."""
        asyncio.run(self.update_cell_metrics_async(cell))
    
    def tick(self):
        """
        One iteration of the field.
        
        This is the Game of Life loop.
        """
        self.iteration += 1
        self.births_this_interval = 0
        self.deaths_this_interval = 0
        
        log_metrics(f"\n{'='*50}", "DEBUG")
        log_metrics(f"Iteration {self.iteration} - {len(self.cells)} cells alive", "INFO")
        
        # 1. Update metrics for all cells
        for cell in self.cells:
            if cell.alive:
                self.update_cell_metrics(cell)
        
        # 2. Tick all cells (life/death/reproduction)
        new_cells = []
        for cell in self.cells:
            if not cell.alive:
                continue
            
            # Tick cell
            offspring = cell.tick()
            
            # Check if died
            if not cell.alive:
                self.total_deaths += 1
                self.deaths_this_interval += 1
                self.meta_learner.record_death(cell)
                
                log_metrics(f"💀 Cell {cell.id} died (age={cell.age}, R={cell.resonance_score:.3f})", "DEBUG")
                
                # Log to SQLite
                self.resonance_bridge.log_cell(cell)
            
            # Check if reproduced
            if offspring:
                new_cells.append(offspring)
                self.total_births += 1
                self.births_this_interval += 1
                
                log_metrics(f"🌱 Cell {offspring.id} born from {cell.id}", "DEBUG")
        
        # 3. Add new cells (births)
        self.cells.extend(new_cells)
        
        # 4. Remove dead cells
        self.cells = [c for c in self.cells if c.alive]
        
        # 5. Population cap (prevent explosion)
        if len(self.cells) > MAX_POPULATION:
            # Kill weakest cells
            self.cells.sort(key=lambda c: c.resonance_score, reverse=True)
            killed = self.cells[MAX_POPULATION:]
            self.cells = self.cells[:MAX_POPULATION]
            
            for cell in killed:
                cell.die()
                self.total_deaths += 1
                self.deaths_this_interval += 1
            
            log_metrics(f"⚠️ Population cap reached - killed {len(killed)} weakest cells", "WARNING")
        
        # 6. Log field state to SQLite
        self.resonance_bridge.log_field_state(
            self.cells, self.iteration, 
            self.births_this_interval, self.deaths_this_interval
        )
        
        # 7. Adapt AMLK kernel (dynamic Linux kernel evolution!)
        if self.iteration % (REPORT_INTERVAL * 2) == 0 and self.cells and self.amlk:
            avg_resonance = sum(c.resonance_score for c in self.cells) / len(self.cells)
            avg_entropy = sum(c.entropy for c in self.cells) / len(self.cells)
            
            # Calculate kernel parameters based on Field metrics
            kernel_params = {
                "parallelism": int(10 + avg_resonance * 20),        # 10-30 parallel tasks
                "memory_limit_mb": int(100 + avg_entropy * 200),    # 100-300 MB
                "cache_size": int(50 + len(self.cells) * 0.5),     # Scale with population
            }
            
            try:
                # Actually update AMLK kernel parameters
                self.amlk.update_parameters(kernel_params)
                log_metrics(f"🔧 AMLK adapted: parallelism={kernel_params['parallelism']}, memory={kernel_params['memory_limit_mb']}MB, cache={kernel_params['cache_size']}", "INFO")
            except Exception as e:
                log_metrics(f"AMLK adaptation failed: {e}", "DEBUG")
        
        # 8. Send metrics notification
        if self.iteration % REPORT_INTERVAL == 0:
            self.send_metrics_report()
        
        # 9. Print summary
        if self.iteration % REPORT_INTERVAL == 0:
            log_metrics(f"\n{format_cell_summary(self.cells)}", "INFO")
    
    def send_metrics_report(self):
        """Send metrics to Termux notification."""
        if not self.cells:
            avg_resonance = 0.0
            avg_age = 0.0
        else:
            avg_resonance = sum(c.resonance_score for c in self.cells) / len(self.cells)
            avg_age = sum(c.age for c in self.cells) / len(self.cells)
        
        send_field_metrics(
            iteration=self.iteration,
            cell_count=len(self.cells),
            avg_resonance=avg_resonance,
            avg_age=avg_age,
            births=self.births_this_interval,
            deaths=self.deaths_this_interval
        )
    
    def run(self):
        """
        Main loop - Async Field Forever.
        
        This runs indefinitely until interrupted.
        """
        print_field_banner()
        
        log_metrics("Field starting...", "INFO")
        
        # Initialize population
        self.initialize_population()
        
        # Send initial metrics
        self.send_metrics_report()
        
        log_metrics(f"Field is alive. Running with {TICK_DURATION}s tick duration.", "INFO")
        log_metrics("Press Ctrl+C to stop.\n", "INFO")
        
        try:
            # Main loop
            while True:
                # Tick
                self.tick()
                
                # Sleep
                time.sleep(TICK_DURATION)
        
        except KeyboardInterrupt:
            log_metrics("\n\nField shutting down...", "INFO")
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown."""
        log_metrics(f"\nField Statistics:", "INFO")
        log_metrics(f"  Total iterations: {self.iteration}", "INFO")
        log_metrics(f"  Total births: {self.total_births}", "INFO")
        log_metrics(f"  Total deaths: {self.total_deaths}", "INFO")
        log_metrics(f"  Final population: {len(self.cells)}", "INFO")
        
        # Meta-learner stats
        meta_stats = self.meta_learner.get_stats()
        log_metrics(f"\nMeta-Learning:", "INFO")
        log_metrics(f"  Successful architectures: {meta_stats['successful_count']}", "INFO")
        log_metrics(f"  Failed architectures: {meta_stats['failed_count']}", "INFO")
        log_metrics(f"  Success rate: {meta_stats['success_rate']:.2%}", "INFO")
        
        log_metrics("\nAsync field forever. 🧬⚡🌀", "INFO")


def main():
    """Entry point."""
    field = Field()
    field.run()


if __name__ == "__main__":
    main()

