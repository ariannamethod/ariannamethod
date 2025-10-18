"""
Learning System - 3-layer learning from Nicole architecture.

Layer 1: Token prediction (perplexity)
Layer 2: Code quality evaluation (entropy, perplexity, resonance)
Layer 3: Meta-learning (architecture evolution)
"""

import random
import numpy as np
from typing import List, Dict, Any, Optional

# Use lightweight TF-IDF instead of scikit-learn (Termux ARM optimization by Claude Defender)
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

if not SKLEARN_AVAILABLE:
    from lightweight_tfidf import LightweightTFIDF, cosine_similarity


class EmbeddingEngine:
    """Simple TF-IDF based embeddings for Phase 1."""

    def __init__(self):
        """Initialize TF-IDF vectorizer."""
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        else:
            # Use lightweight implementation (Termux ARM)
            self.vectorizer = LightweightTFIDF(max_features=100, min_df=1, max_df=0.95)
        self.is_fitted = False
        self.use_lightweight = not SKLEARN_AVAILABLE
    
    def fit(self, texts: List[str]):
        """
        Fit vectorizer on texts.
        
        Args:
            texts: List of text strings
        """
        if texts:
            self.vectorizer.fit(texts)
            self.is_fitted = True
    
    def embed(self, text: str) -> np.ndarray:
        """
        Convert text to embedding vector.
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector (numpy array)
        """
        if not self.is_fitted:
            # Return random vector if not fitted
            return np.random.randn(100)
        
        try:
            vector = self.vectorizer.transform([text]).toarray()[0]
            return vector
        except:
            return np.random.randn(100)
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0 to 1)
        """
        if not self.is_fitted:
            return random.random()

        try:
            if SKLEARN_AVAILABLE:
                vectors = self.vectorizer.transform([text1, text2]).toarray()
                sim = sklearn_cosine([vectors[0]], [vectors[1]])[0][0]
            else:
                # Use lightweight implementation
                vec1 = self.embed(text1)
                vec2 = self.embed(text2)
                sim = cosine_similarity(vec1, vec2)
            return max(0.0, sim)  # Clamp to [0, 1]
        except:
            return 0.0


class MetaLearner:
    """
    Layer 3: Meta-learning system.
    
    Learns which architectures survive longest and biases future compilations.
    """
    
    def __init__(self):
        """Initialize meta-learner."""
        self.successful_architectures = []  # Long-lived cells
        self.failed_architectures = []      # Short-lived cells
        self.age_threshold_success = 10     # Age > this = success
    
    def record_death(self, cell):
        """
        Record cell death and learn from it.
        
        Args:
            cell: TransformerCell that died
        """
        if cell.age >= self.age_threshold_success:
            # Success - lived long enough
            self.successful_architectures.append(cell.architecture.copy())
        else:
            # Failure - died too young
            self.failed_architectures.append(cell.architecture.copy())
    
    def suggest_architecture(self) -> Dict[str, Any]:
        """
        Suggest architecture for new cell.
        
        Biases toward successful patterns with slight mutation.
        
        Returns:
            Architecture dictionary
        """
        from config import MUTATION_RATE
        
        if not self.successful_architectures:
            # No successful patterns yet - return default
            from config import TRANSFORMER_PARAMS
            return TRANSFORMER_PARAMS.copy()
        
        # Pick random successful architecture
        base = random.choice(self.successful_architectures)
        
        # Mutate it slightly
        mutated = self._mutate_architecture(base, MUTATION_RATE)
        
        return mutated
    
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
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get meta-learning statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "successful_count": len(self.successful_architectures),
            "failed_count": len(self.failed_architectures),
            "success_rate": len(self.successful_architectures) / max(1, len(self.successful_architectures) + len(self.failed_architectures)),
        }


def calculate_entropy(outputs: List[float]) -> float:
    """
    Calculate Shannon entropy of outputs.
    
    H = -Σ p(i) log p(i)
    
    Args:
        outputs: List of output values
    
    Returns:
        Entropy (0 to 1, normalized)
    """
    if not outputs:
        return 0.0
    
    # Convert to probability distribution
    outputs_array = np.array(outputs)
    outputs_array = np.abs(outputs_array)  # Ensure positive
    
    if outputs_array.sum() == 0:
        return 0.0
    
    probs = outputs_array / outputs_array.sum()
    
    # Calculate entropy
    probs = probs[probs > 0]  # Remove zeros
    entropy = -np.sum(probs * np.log(probs + 1e-10))
    
    # Normalize to [0, 1]
    max_entropy = np.log(len(probs))
    if max_entropy > 0:
        entropy = entropy / max_entropy
    
    return float(entropy)


def calculate_perplexity(outputs: List[float]) -> float:
    """
    Calculate perplexity of outputs.
    
    Perplexity = exp(H)
    
    Args:
        outputs: List of output values
    
    Returns:
        Perplexity score
    """
    entropy = calculate_entropy(outputs)
    perplexity = np.exp(entropy)
    return float(perplexity)


def calculate_semantic_resonance(cell, neighbors: List, embedding_engine: 'EmbeddingEngine') -> float:
    """
    Calculate semantic resonance with neighbors.
    
    Resonance = average similarity to neighbors in embedding space.
    
    Args:
        cell: TransformerCell
        neighbors: List of neighbor cells
        embedding_engine: EmbeddingEngine for similarity calculation
    
    Returns:
        Resonance score (0 to 1)
    """
    if not neighbors:
        return 0.5  # Neutral if no neighbors
    
    # Calculate similarity to each neighbor
    similarities = []
    for neighbor in neighbors:
        if not neighbor.alive:
            continue
        
        sim = embedding_engine.similarity(cell.context, neighbor.context)
        similarities.append(sim)
    
    if not similarities:
        return 0.5
    
    # Average similarity = resonance
    resonance = np.mean(similarities)
    
    return float(resonance)


def get_semantic_neighbors(cell, all_cells: List, embedding_engine: 'EmbeddingEngine', k: int = 5) -> List:
    """
    Find k semantically closest neighbors.
    
    This replaces geometric neighbors from classic Game of Life.
    Neighbors = cells with similar embeddings in semantic space.
    
    Args:
        cell: TransformerCell
        all_cells: List of all cells
        embedding_engine: EmbeddingEngine for similarity
        k: Number of neighbors to return
    
    Returns:
        List of k nearest neighbor cells
    """
    if len(all_cells) <= 1:
        return []
    
    # Get embedding for this cell
    cell_embedding = embedding_engine.embed(cell.context)
    
    # Calculate distance to all other living cells
    distances = []
    for other_cell in all_cells:
        if other_cell.id == cell.id or not other_cell.alive:
            continue
        
        other_embedding = embedding_engine.embed(other_cell.context)

        # Cosine distance (use appropriate function based on sklearn availability)
        if SKLEARN_AVAILABLE:
            distance = 1.0 - sklearn_cosine([cell_embedding], [other_embedding])[0][0]
        else:
            similarity = cosine_similarity(cell_embedding, other_embedding)
            distance = 1.0 - similarity
        distances.append((distance, other_cell))
    
    if not distances:
        return []
    
    # Sort by distance (closest first)
    distances.sort(key=lambda x: x[0])
    
    # Return k closest
    neighbors = [cell for _, cell in distances[:k]]
    
    return neighbors
