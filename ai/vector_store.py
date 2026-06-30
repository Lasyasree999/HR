"""
HireGenius AI — FAISS Vector Store Manager
=============================================
Manages FAISS indexes for resume, job, and policy knowledge bases.
Supports create, add, search, persist, and load operations.
"""

import os
import json
import logging
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import numpy as np
import faiss

from config import get_settings
from ai.embeddings import generate_embedding, generate_embeddings

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorStoreManager:
    """
    Manages FAISS vector indexes for different knowledge bases.
    Each index stores document embeddings and associated metadata.
    """

    def __init__(self, index_name: str, dimension: int = 384):
        """
        Initialize a FAISS vector store.

        Args:
            index_name: Name of the index (e.g., 'resume_index', 'job_index', 'policy_index').
            dimension: Embedding dimension (384 for all-MiniLM-L6-v2).
        """
        self.index_name = index_name
        self.dimension = dimension
        self.index_dir = settings.FAISS_INDEX_PATH / index_name
        self.index_file = self.index_dir / "index.faiss"
        self.metadata_file = self.index_dir / "metadata.json"
        self.index: Optional[faiss.IndexFlatIP] = None
        self.metadata: List[Dict[str, Any]] = []

        # Ensure directory exists
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Load existing index or create new one
        self._load_or_create()

    def _load_or_create(self):
        """Load existing FAISS index from disk or create a new one."""
        if self.index_file.exists() and self.metadata_file.exists():
            try:
                self.index = faiss.read_index(str(self.index_file))
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                logger.info(
                    f"Loaded FAISS index '{self.index_name}' with {self.index.ntotal} vectors"
                )
            except Exception as e:
                logger.warning(f"Failed to load index '{self.index_name}': {e}. Creating new.")
                self._create_new()
        else:
            self._create_new()

    def _create_new(self):
        """Create a new empty FAISS index using Inner Product (cosine similarity)."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        logger.info(f"Created new FAISS index '{self.index_name}' (dim={self.dimension})")

    def add_document(self, text: str, metadata: Dict[str, Any]) -> int:
        """
        Add a single document to the vector store.

        Args:
            text: Document text to embed and store.
            metadata: Associated metadata (e.g., candidate_id, file_name).

        Returns:
            Index position of the added document.
        """
        embedding = generate_embedding(text)
        embedding = embedding.reshape(1, -1)
        self.index.add(embedding)
        self.metadata.append(metadata)
        position = self.index.ntotal - 1
        logger.debug(f"Added document to '{self.index_name}' at position {position}")
        return position

    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Add multiple documents to the vector store in batch.

        Args:
            texts: List of document texts.
            metadatas: List of metadata dicts (must match texts length).

        Returns:
            List of index positions.
        """
        if len(texts) != len(metadatas):
            raise ValueError("texts and metadatas must have the same length")

        embeddings = generate_embeddings(texts)
        start_pos = self.index.ntotal
        self.index.add(embeddings)
        self.metadata.extend(metadatas)
        positions = list(range(start_pos, self.index.ntotal))
        logger.info(f"Added {len(texts)} documents to '{self.index_name}'")
        return positions

    def search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search the vector store for similar documents.

        Args:
            query: Search query text.
            top_k: Number of top results to return.

        Returns:
            List of dicts with 'score', 'metadata', and 'rank'.
        """
        if self.index.ntotal == 0:
            logger.warning(f"Search on empty index '{self.index_name}'")
            return []

        query_embedding = generate_embedding(query).reshape(1, -1)
        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))

        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            result = {
                "rank": rank + 1,
                "score": float(score),
                "metadata": self.metadata[idx] if idx < len(self.metadata) else {},
            }
            results.append(result)

        return results

    def save(self):
        """Persist the FAISS index and metadata to disk."""
        try:
            faiss.write_index(self.index, str(self.index_file))
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2, default=str)
            logger.info(
                f"Saved FAISS index '{self.index_name}' ({self.index.ntotal} vectors)"
            )
        except Exception as e:
            logger.error(f"Failed to save index '{self.index_name}': {e}")
            raise

    def clear(self):
        """Clear all data from the index."""
        self._create_new()
        self.save()
        logger.info(f"Cleared FAISS index '{self.index_name}'")

    @property
    def count(self) -> int:
        """Number of vectors in the index."""
        return self.index.ntotal if self.index else 0


# ============================================================
# Singleton instances for the three knowledge bases
# ============================================================

_resume_store: Optional[VectorStoreManager] = None
_job_store: Optional[VectorStoreManager] = None
_policy_store: Optional[VectorStoreManager] = None


def get_resume_store() -> VectorStoreManager:
    """Get the resume vector store singleton."""
    global _resume_store
    if _resume_store is None:
        _resume_store = VectorStoreManager("resume_index")
    return _resume_store


def get_job_store() -> VectorStoreManager:
    """Get the job description vector store singleton."""
    global _job_store
    if _job_store is None:
        _job_store = VectorStoreManager("job_index")
    return _job_store


def get_policy_store() -> VectorStoreManager:
    """Get the policy document vector store singleton."""
    global _policy_store
    if _policy_store is None:
        _policy_store = VectorStoreManager("policy_index")
    return _policy_store
