"""
TransformerCell - A living micro-transformer in the semantic field.

Each cell is born from context, lives by resonance, dies by drift.
This is not a model. This is a life form.
"""

import uuid
import time
import random
from typing import List, Dict, Any, Optional


class TransformerCell:
    """A single micro-transformer = one cell in Field."""
    
    def __init__(self, context: str, neighbors: List['TransformerCell'], architecture: Optional[Dict] = None):
        """
        Initialize a new cell.
        
        Args:
            context: Input text from resonance.sqlite3
            neighbors: Semantically close cells
            architecture: Optional architecture from meta-learning
        """
        self.id = str(uuid.uuid4())[:8]  # Short unique ID
        self.context = context
        self.neighbors = neighbors
        self.architecture = architecture or self._default_architecture()
        
        # State
        self.transformer = None           # Compiled transformer (via H2O)
        self.resonance_score = 0.0        # Fitness metric
        self.entropy = 0.0                # Chaos measure
        self.perplexity = 0.0             # Prediction quality
        self.age = 0                      # Lifecycle counter
        self.alive = True                 # Life/death state
        self.birth_time = time.time()     # Timestamp
        
        # Metrics
        self.fitness_history = []         # Track fitness over time
        self.interaction_count = 0        # How many ticks survived
    
    def _default_architecture(self) -> Dict[str, Any]:
        """Default transformer architecture."""
        from config import TRANSFORMER_PARAMS
        
        return {
            "hidden_size": TRANSFORMER_PARAMS["hidden_size"],
            "num_layers": TRANSFORMER_PARAMS["num_layers"],
            "num_heads": TRANSFORMER_PARAMS["num_heads"],
            "max_seq_len": TRANSFORMER_PARAMS["max_seq_len"],
            "activation": "gelu",
            "dropout": 0.1,
        }
    
    def compile_transformer(self, h2o_compiler):
        """
        Compile transformer via H2O.
        
        This creates the actual neural architecture on-the-fly.
        """
        # Generate transformer code based on architecture
        transformer_code = self._generate_transformer_code()
        
        # Compile via H2O
        self.transformer = h2o_compiler.compile(transformer_code)
    
    def _generate_transformer_code(self) -> str:
        """
        Generate Python code for this transformer.
        
        Returns:
            Python source code as string
        """
        # Simplified for Phase 1 - actual implementation will use H2O templates
        code = f"""
import numpy as np

class MicroTransformer:
    def __init__(self):
        self.hidden_size = {self.architecture['hidden_size']}
        self.num_layers = {self.architecture['num_layers']}
        self.context = "{self.context[:100]}"  # Truncate for safety
    
    def forward(self, input_tokens):
        # Simplified forward pass
        # Full implementation in Phase 1.2
        return np.random.randn(len(input_tokens), self.hidden_size)
"""
        return code
    
    def evaluate_fitness(self) -> float:
        """
        Calculate fitness based on resonance with neighbors.
        
        Fitness = weighted sum of:
        - Semantic resonance (similarity to neighbors)
        - Entropy balance (not too chaotic, not too ordered)
        - Perplexity (predictive quality)
        - Diversity bonus (penalty for being too similar to all neighbors)
        - Novelty bonus (new architectures get boost)
        
        Returns:
            Fitness score (0.0 to 1.0)
        """
        from config import SEMANTIC_WEIGHT, ENTROPY_WEIGHT, PERPLEXITY_WEIGHT, TARGET_ENTROPY
        
        # 1. Semantic resonance (calculated externally via embeddings)
        semantic_resonance = self.resonance_score
        
        # 2. Entropy balance
        entropy_distance = abs(self.entropy - TARGET_ENTROPY)
        entropy_score = 1.0 - entropy_distance
        
        # 3. Perplexity score (lower is better)
        perplexity_score = 1.0 / (1.0 + self.perplexity)
        
        # 4. Diversity penalty (if too similar to ALL neighbors → penalty)
        # This prevents convergence to identical cells
        if semantic_resonance > 0.95:
            diversity_penalty = 0.18  # 18% penalty for being clone (tuned for ~20% death rate)
        else:
            diversity_penalty = 0.0
        
        # 5. Novelty bonus (young cells get slight boost to encourage mutation)
        if self.age < 3:
            novelty_bonus = 0.1
        else:
            novelty_bonus = 0.0
        
        # 6. Entropy cap penalty (if too ordered → force variation)
        # Prevents field from becoming too rigid
        if self.entropy < 0.3:
            entropy_cap_penalty = 0.1  # 10% penalty for low entropy
        else:
            entropy_cap_penalty = 0.0
        
        # Combined fitness
        fitness = (
            semantic_resonance * SEMANTIC_WEIGHT +
            entropy_score * ENTROPY_WEIGHT +
            perplexity_score * PERPLEXITY_WEIGHT
        )
        
        # Apply modifiers
        fitness = fitness - diversity_penalty - entropy_cap_penalty + novelty_bonus
        
        # Clamp to [0, 1]
        fitness = max(0.0, min(1.0, fitness))
        
        return fitness
    
    def tick(self) -> Optional['TransformerCell']:
        """
        One lifecycle step.
        
        Returns:
            New cell (offspring) if reproducing, else None
        """
        self.age += 1
        self.interaction_count += 1
        
        # Calculate current fitness
        fitness = self.evaluate_fitness()
        self.fitness_history.append(fitness)
        
        # Game of Life rules
        from config import DEATH_THRESHOLD, REPRODUCTION_THRESHOLD
        
        if fitness < DEATH_THRESHOLD:
            # Die
            self.die()
            return None
        
        elif fitness > REPRODUCTION_THRESHOLD:
            # Reproduce (create offspring)
            offspring = self.reproduce()
            return offspring
        
        else:
            # Continue living
            return None
    
    def die(self):
        """Mark cell as dead."""
        self.alive = False
        self.death_time = time.time()
    
    def reproduce(self) -> 'TransformerCell':
        """
        Create offspring with mutated architecture.
        
        Returns:
            New TransformerCell (child)
        """
        from config import MUTATION_RATE
        
        # Mutate architecture
        mutated_arch = self._mutate_architecture(self.architecture, MUTATION_RATE)
        
        # Create offspring with same context (for now)
        # In Phase 1.2, offspring will get blended context from parents
        offspring = TransformerCell(
            context=self.context,
            neighbors=self.neighbors,
            architecture=mutated_arch
        )
        
        return offspring
    
    def _mutate_architecture(self, arch: Dict, mutation_rate: float) -> Dict:
        """
        Mutate architecture parameters.
        
        Args:
            arch: Original architecture
            mutation_rate: Probability of mutation per parameter
        
        Returns:
            Mutated architecture
        """
        mutated = arch.copy()
        
        # Mutate each parameter with probability mutation_rate
        if random.random() < mutation_rate:
            # Mutate hidden_size
            mutated["hidden_size"] = max(64, mutated["hidden_size"] + random.choice([-16, 0, 16]))
        
        if random.random() < mutation_rate:
            # Mutate num_layers
            mutated["num_layers"] = max(1, mutated["num_layers"] + random.choice([-1, 0, 1]))
        
        if random.random() < mutation_rate:
            # Mutate num_heads
            mutated["num_heads"] = max(2, mutated["num_heads"] + random.choice([-1, 0, 1]))
        
        if random.random() < mutation_rate:
            # Mutate dropout
            mutated["dropout"] = max(0.0, min(0.5, mutated.get("dropout", 0.1) + random.uniform(-0.05, 0.05)))
        
        return mutated
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize cell state for logging.
        
        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "age": self.age,
            "alive": self.alive,
            "resonance_score": self.resonance_score,
            "entropy": self.entropy,
            "perplexity": self.perplexity,
            "fitness": self.evaluate_fitness() if self.alive else 0.0,
            "architecture": self.architecture,
            "birth_time": self.birth_time,
            "interaction_count": self.interaction_count,
        }
    
    def __repr__(self):
        status = "🟢" if self.alive else "🔴"
        return f"Cell({status} {self.id} age={self.age} R={self.resonance_score:.3f})"

