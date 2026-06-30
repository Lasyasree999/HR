"""
HireGenius AI — LlamaIndex RAG Engine
========================================
Retrieval-Augmented Generation pipelines using LlamaIndex,
FAISS vector stores, and Groq LLM for intelligent querying
across resume, job, and policy knowledge bases.
"""

import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

from config import get_settings
from ai.groq_client import get_groq_client

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGEngine:
    """
    RAG (Retrieval-Augmented Generation) engine using LlamaIndex.
    Provides query capabilities over vectorized knowledge bases
    with context-augmented Groq LLM generation.
    """

    def __init__(self):
        """Initialize the RAG engine with LlamaIndex components."""
        self.groq = get_groq_client()
        self._resume_index = None
        self._job_index = None
        self._policy_index = None

    def _get_llamaindex_components(self):
        """Lazy-load LlamaIndex components to avoid slow startup."""
        try:
            from llama_index.core import (
                VectorStoreIndex,
                StorageContext,
                Document,
                Settings as LlamaSettings,
            )
            from llama_index.vector_stores.faiss import FaissVectorStore
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            from llama_index.llms.groq import Groq as LlamaGroq
            import faiss

            return {
                "VectorStoreIndex": VectorStoreIndex,
                "StorageContext": StorageContext,
                "Document": Document,
                "LlamaSettings": LlamaSettings,
                "FaissVectorStore": FaissVectorStore,
                "HuggingFaceEmbedding": HuggingFaceEmbedding,
                "LlamaGroq": LlamaGroq,
                "faiss": faiss,
            }
        except ImportError as e:
            logger.error(f"LlamaIndex components not available: {e}")
            raise RuntimeError(
                "LlamaIndex packages not installed. Run: pip install llama-index "
                "llama-index-vector-stores-faiss llama-index-llms-groq "
                "llama-index-embeddings-huggingface"
            )

    def _setup_llamaindex_settings(self, components: dict):
        """Configure global LlamaIndex settings with our models."""
        LlamaSettings = components["LlamaSettings"]
        HuggingFaceEmbedding = components["HuggingFaceEmbedding"]
        LlamaGroq = components["LlamaGroq"]

        LlamaSettings.embed_model = HuggingFaceEmbedding(
            model_name=settings.HF_EMBEDDING_MODEL
        )
        LlamaSettings.llm = LlamaGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
        )
        LlamaSettings.chunk_size = 512
        LlamaSettings.chunk_overlap = 50

    def build_index_from_texts(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        index_name: str,
    ):
        """
        Build a LlamaIndex VectorStoreIndex from a list of texts.

        Args:
            texts: List of document texts.
            metadatas: List of metadata dicts.
            index_name: Name for the FAISS index directory.
        """
        components = self._get_llamaindex_components()
        self._setup_llamaindex_settings(components)

        Document = components["Document"]
        VectorStoreIndex = components["VectorStoreIndex"]
        StorageContext = components["StorageContext"]
        FaissVectorStore = components["FaissVectorStore"]
        faiss = components["faiss"]

        # Create FAISS index
        faiss_index = faiss.IndexFlatIP(settings.EMBEDDING_DIMENSION)
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Create documents with metadata
        documents = []
        for i, (text, meta) in enumerate(zip(texts, metadatas)):
            doc = Document(text=text, metadata=meta)
            documents.append(doc)

        # Build index
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
        )

        # Persist
        index_dir = settings.FAISS_INDEX_PATH / f"{index_name}_llamaindex"
        index_dir.mkdir(parents=True, exist_ok=True)
        index.storage_context.persist(persist_dir=str(index_dir))

        logger.info(f"Built LlamaIndex index '{index_name}' with {len(documents)} documents")
        return index

    def query(
        self,
        query_text: str,
        index_name: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Query a knowledge base using RAG.
        Falls back to direct Groq generation if LlamaIndex index is unavailable.

        Args:
            query_text: User question/query.
            index_name: Which knowledge base to query.
            top_k: Number of context documents to retrieve.

        Returns:
            Dict with 'answer', 'sources', and 'confidence'.
        """
        # Try LlamaIndex RAG first
        try:
            return self._query_with_llamaindex(query_text, index_name, top_k)
        except Exception as e:
            logger.warning(f"LlamaIndex query failed, falling back to vector search: {e}")

        # Fallback: use our own FAISS + Groq
        return self._query_with_faiss_groq(query_text, index_name, top_k)

    def _query_with_llamaindex(
        self,
        query_text: str,
        index_name: str,
        top_k: int,
    ) -> Dict[str, Any]:
        """Query using LlamaIndex's built-in RAG pipeline."""
        components = self._get_llamaindex_components()
        self._setup_llamaindex_settings(components)

        VectorStoreIndex = components["VectorStoreIndex"]
        StorageContext = components["StorageContext"]
        FaissVectorStore = components["FaissVectorStore"]

        index_dir = settings.FAISS_INDEX_PATH / f"{index_name}_llamaindex"
        if not index_dir.exists():
            raise FileNotFoundError(f"LlamaIndex index not found: {index_dir}")

        # Load persisted index
        vector_store = FaissVectorStore.from_persist_dir(str(index_dir))
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            persist_dir=str(index_dir),
        )
        index = VectorStoreIndex(
            storage_context=storage_context,
        )

        # Query
        query_engine = index.as_query_engine(similarity_top_k=top_k)
        response = query_engine.query(query_text)

        sources = []
        if response.source_nodes:
            for node in response.source_nodes:
                sources.append({
                    "text": node.text[:200],
                    "score": float(node.score) if node.score else 0.0,
                    "metadata": node.metadata,
                })

        return {
            "answer": str(response),
            "sources": sources,
            "confidence": sources[0]["score"] if sources else 0.0,
        }

    def _query_with_faiss_groq(
        self,
        query_text: str,
        index_name: str,
        top_k: int,
    ) -> Dict[str, Any]:
        """
        Fallback RAG: use our FAISS VectorStoreManager + Groq.
        Retrieves relevant context and augments the prompt.
        """
        from ai.vector_store import get_resume_store, get_job_store, get_policy_store

        # Select the right store
        store_map = {
            "resume_index": get_resume_store,
            "job_index": get_job_store,
            "policy_index": get_policy_store,
        }

        store_getter = store_map.get(index_name)
        if not store_getter:
            raise ValueError(f"Unknown index: {index_name}")

        store = store_getter()
        results = store.search(query_text, top_k=top_k)

        if not results:
            # No context available, generate directly
            answer = self.groq.generate(
                prompt=query_text,
                system_prompt="You are an AI recruitment assistant. Answer the question helpfully.",
            )
            return {"answer": answer, "sources": [], "confidence": 0.0}

        # Build context from search results
        context_parts = []
        sources = []
        for r in results:
            meta = r.get("metadata", {})
            text = meta.get("text", meta.get("content", str(meta)))
            context_parts.append(text[:500])
            sources.append({
                "text": text[:200],
                "score": r["score"],
                "metadata": meta,
            })

        context = "\n\n---\n\n".join(context_parts)

        # Augmented generation
        prompt = f"""Based on the following context, answer the user's question.

CONTEXT:
{context}

QUESTION: {query_text}

Provide a comprehensive, helpful answer based on the context above. If the context doesn't contain
enough information, say so and provide what you can."""

        answer = self.groq.generate(
            prompt=prompt,
            system_prompt="You are an AI recruitment intelligence assistant. "
                         "Use the provided context to give accurate, detailed answers.",
            temperature=0.3,
        )

        return {
            "answer": answer,
            "sources": sources,
            "confidence": results[0]["score"] if results else 0.0,
        }


# Singleton
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get or create the singleton RAG engine instance."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
