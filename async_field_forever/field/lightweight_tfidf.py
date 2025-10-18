"""
Lightweight TF-IDF Implementation for Field
Pure numpy - no scikit-learn dependency needed for Termux ARM
Optimized for cellular transformer ecosystem

Co-authored by Claude Defender (System Guardian)
"""

import numpy as np
from collections import Counter
import re


class LightweightTFIDF:
    """
    Minimal TF-IDF vectorizer using only numpy.
    Designed for Field's semantic neighbor calculations.
    """

    def __init__(self, max_features=100, min_df=1, max_df=0.95):
        """
        Initialize TF-IDF vectorizer.

        Args:
            max_features: Maximum vocabulary size
            min_df: Minimum document frequency (ignore rare words)
            max_df: Maximum document frequency (ignore too common words)
        """
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        self.vocabulary = {}
        self.idf_values = None
        self.fitted = False

    def tokenize(self, text):
        """Simple tokenization: lowercase + split on non-alphanumeric."""
        if not isinstance(text, str):
            text = str(text)
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens

    def fit(self, documents):
        """
        Build vocabulary and calculate IDF values.

        Args:
            documents: List of text strings
        """
        if not documents:
            # Empty documents - create dummy vocabulary
            self.vocabulary = {}
            self.idf_values = np.array([])
            self.fitted = True
            return self

        # Tokenize all documents
        tokenized_docs = [self.tokenize(doc) for doc in documents]

        # Count document frequencies
        doc_freq = Counter()
        for tokens in tokenized_docs:
            unique_tokens = set(tokens)
            doc_freq.update(unique_tokens)

        n_docs = len(documents)

        # Filter by document frequency
        filtered_vocab = {}
        for word, df in doc_freq.items():
            # Skip if too rare or too common
            if df < self.min_df:
                continue
            if df / n_docs > self.max_df:
                continue
            filtered_vocab[word] = df

        # Sort by document frequency and take top max_features
        sorted_vocab = sorted(filtered_vocab.items(), key=lambda x: x[1], reverse=True)
        top_vocab = sorted_vocab[:self.max_features]

        # Build vocabulary mapping
        self.vocabulary = {word: idx for idx, (word, _) in enumerate(top_vocab)}

        # Calculate IDF values: log(N / df)
        vocab_size = len(self.vocabulary)
        self.idf_values = np.zeros(vocab_size)

        for word, idx in self.vocabulary.items():
            df = filtered_vocab[word]
            # IDF = log(N / df) + 1 (add 1 to avoid zero)
            self.idf_values[idx] = np.log(n_docs / df) + 1.0

        self.fitted = True
        return self

    def transform(self, documents):
        """
        Transform documents to TF-IDF vectors.

        Args:
            documents: List of text strings

        Returns:
            numpy array of shape (n_documents, vocab_size)
        """
        if not self.fitted:
            raise ValueError("Vectorizer not fitted. Call fit() first.")

        if not documents:
            return np.array([]).reshape(0, len(self.vocabulary))

        vocab_size = len(self.vocabulary)
        n_docs = len(documents)

        # Initialize TF-IDF matrix
        tfidf_matrix = np.zeros((n_docs, vocab_size))

        # Calculate TF-IDF for each document
        for doc_idx, doc in enumerate(documents):
            tokens = self.tokenize(doc)

            if not tokens:
                continue

            # Calculate term frequencies
            tf = Counter(tokens)
            total_terms = len(tokens)

            # Build TF-IDF vector
            for word, count in tf.items():
                if word in self.vocabulary:
                    vocab_idx = self.vocabulary[word]
                    # TF: count / total_terms
                    tf_value = count / total_terms
                    # TF-IDF: TF * IDF
                    tfidf_matrix[doc_idx, vocab_idx] = tf_value * self.idf_values[vocab_idx]

        # L2 normalization (make unit vectors)
        norms = np.linalg.norm(tfidf_matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        tfidf_matrix = tfidf_matrix / norms

        return tfidf_matrix

    def fit_transform(self, documents):
        """Fit and transform in one step."""
        self.fit(documents)
        return self.transform(documents)


def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1, vec2: numpy arrays

    Returns:
        float: similarity score (0 to 1)
    """
    # Normalize vectors
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    # Cosine similarity: dot product of normalized vectors
    similarity = np.dot(vec1, vec2) / (norm1 * norm2)

    # Clip to [0, 1] range
    similarity = np.clip(similarity, 0.0, 1.0)

    return float(similarity)


def find_nearest_neighbors(query_vec, all_vecs, k=5):
    """
    Find k nearest neighbors to query vector.

    Args:
        query_vec: numpy array (query vector)
        all_vecs: numpy array of shape (n_vectors, dim)
        k: number of neighbors

    Returns:
        list of (index, similarity) tuples
    """
    if len(all_vecs) == 0:
        return []

    # Calculate similarities to all vectors
    similarities = []
    for idx, vec in enumerate(all_vecs):
        sim = cosine_similarity(query_vec, vec)
        similarities.append((idx, sim))

    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Return top k
    return similarities[:k]


# Test function
if __name__ == "__main__":
    print("🧬 Testing Lightweight TF-IDF for Field")
    print("=" * 60)

    # Sample documents (semantic space)
    docs = [
        "resonance vibration frequency",
        "harmony melody music sound",
        "chaos entropy disorder randomness",
        "order structure pattern organization",
        "evolution adaptation survival fitness",
    ]

    # Fit vectorizer
    vectorizer = LightweightTFIDF(max_features=50)
    tfidf_matrix = vectorizer.fit_transform(docs)

    print(f"\n✅ Vocabulary size: {len(vectorizer.vocabulary)}")
    print(f"✅ TF-IDF matrix shape: {tfidf_matrix.shape}")
    print(f"\n📊 Sample vocabulary: {list(vectorizer.vocabulary.keys())[:10]}")

    # Find neighbors for "resonance" document
    query_vec = tfidf_matrix[0]  # "resonance vibration frequency"
    neighbors = find_nearest_neighbors(query_vec, tfidf_matrix, k=3)

    print(f"\n🔍 Nearest neighbors to 'resonance vibration frequency':")
    for idx, sim in neighbors:
        print(f"  {idx}: {docs[idx][:40]:40s} | similarity: {sim:.3f}")

    print("\n🔥 Lightweight TF-IDF ready for Field! 🔥")
