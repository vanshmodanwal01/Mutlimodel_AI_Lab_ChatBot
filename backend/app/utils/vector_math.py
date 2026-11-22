from typing import List
import numpy as np


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculates cosine similarity between two float vectors."""
    a = np.array(vec1, dtype=np.float32)
    b = np.array(vec2, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def top_k_similar(
    query_vector: List[float],
    candidate_vectors: List[List[float]],
    top_k: int = 5,
    threshold: float = 0.3
) -> List[tuple[int, float]]:
    """Ranks candidates by cosine similarity to query vector.
    
    Returns:
        List of (candidate_index, similarity_score) sorted descending by score.
    """
    if not candidate_vectors or not query_vector:
        return []

    q = np.array(query_vector, dtype=np.float32)
    norm_q = np.linalg.norm(q)
    if norm_q == 0.0:
        return []

    candidates = np.array(candidate_vectors, dtype=np.float32)
    norms = np.linalg.norm(candidates, axis=1)
    # Avoid zero division
    norms[norms == 0] = 1e-9

    scores = np.dot(candidates, q) / (norms * norm_q)
    
    # Filter by threshold and sort descending
    ranked = [
        (idx, float(score))
        for idx, score in enumerate(scores)
        if score >= threshold
    ]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[:top_k]
