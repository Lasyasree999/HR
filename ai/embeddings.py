"""
HireGenius AI — Embedding Service
====================================
HuggingFace SentenceTransformers embeddings using all-MiniLM-L6-v2.
Generates 384-dimensional dense vectors for semantic search.
"""

import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Global singleton for the embedding model
_embed_model = None


def get_embedding_model():
    """
    Lazy-load the SentenceTransformer embedding model.
    Uses all-MiniLM-L6-v2 (384-dim, fast, high quality).
    """
    global _embed_model
    if _embed_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model: all-MiniLM-L6-v2...")
            _embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise RuntimeError(f"Embedding model initialization failed: {str(e)}")
    return _embed_model


def generate_embedding(text: str) -> np.ndarray:
    """
    Generate a single embedding vector for a text string.

    Args:
        text: Input text to embed.

    Returns:
        384-dimensional numpy array.
    """
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return np.array(embedding, dtype=np.float32)


def generate_embeddings(texts: List[str], batch_size: int = 32) -> np.ndarray:
    """
    Generate embeddings for multiple texts in batches.

    Args:
        texts: List of text strings to embed.
        batch_size: Number of texts per batch.

    Returns:
        2D numpy array of shape (len(texts), 384).
    """
    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True
    )
    return np.array(embeddings, dtype=np.float32)


def compute_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts.

    Args:
        text1: First text.
        text2: Second text.

    Returns:
        Similarity score between 0 and 1.
    """
    emb1 = generate_embedding(text1)
    emb2 = generate_embedding(text2)
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return float(max(0.0, min(1.0, similarity)))


def compute_similarity_batch(query: str, documents: List[str]) -> List[float]:
    """
    Compute cosine similarity between a query and multiple documents.

    Args:
        query: Query text.
        documents: List of document texts.

    Returns:
        List of similarity scores.
    """
    query_emb = generate_embedding(query)
    doc_embs = generate_embeddings(documents)

    # Cosine similarity (embeddings are already normalized)
    similarities = np.dot(doc_embs, query_emb)
    return [float(max(0.0, min(1.0, s))) for s in similarities]
