"""
Vector Store using FAISS
Stores and retrieves embeddings for semantic search
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from loguru import logger


class VectorStore:
    """FAISS-based vector store for semantic memory"""
    
    def __init__(
        self,
        store_path: str = "./data/memory_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        dimension: int = 384
    ):
        """
        Initialize vector store
        
        Args:
            store_path: Directory to persist index
            embedding_model: SentenceTransformer model name
            dimension: Embedding dimension
        """
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        self.dimension = dimension
        self.index_path = self.store_path / "faiss.index"
        self.metadata_path = self.store_path / "metadata.pkl"
        
        # Load embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        
        # Initialize or load FAISS index
        if self.index_path.exists():
            logger.info("Loading existing FAISS index")
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            logger.info("Creating new FAISS index")
            self.index = faiss.IndexFlatL2(dimension)
            self.metadata = []
        
        logger.info(f"Vector store initialized with {self.index.ntotal} vectors")
    
    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Add text to vector store
        
        Args:
            text: Text to embed and store
            metadata: Additional metadata to store
        
        Returns:
            Index ID of added vector
        """
        try:
            # Generate embedding
            embedding = self.embedder.encode([text])[0]
            embedding = np.array([embedding], dtype='float32')
            
            # Add to index
            self.index.add(embedding)
            
            # Store metadata
            meta = {
                "text": text,
                "id": len(self.metadata),
                **(metadata or {})
            }
            self.metadata.append(meta)
            
            logger.debug(f"Added text to vector store (ID: {meta['id']})")
            return meta['id']
            
        except Exception as e:
            logger.error(f"Failed to add text to vector store: {e}")
            raise
    
    def search(
        self,
        query: str,
        k: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar texts
        
        Args:
            query: Search query
            k: Number of results to return
            threshold: Similarity threshold (0-1, lower is more similar for L2)
        
        Returns:
            List of matching documents with metadata
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("Vector store is empty")
                return []
            
            # Generate query embedding
            query_embedding = self.embedder.encode([query])[0]
            query_embedding = np.array([query_embedding], dtype='float32')
            
            # Search
            distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
            
            # Filter by threshold and format results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if dist < threshold and idx < len(self.metadata):
                    result = self.metadata[idx].copy()
                    result['similarity_score'] = float(1 / (1 + dist))  # Convert distance to similarity
                    result['distance'] = float(dist)
                    results.append(result)
            
            logger.info(f"Found {len(results)} similar documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def save(self):
        """Persist index and metadata to disk"""
        try:
            faiss.write_index(self.index, str(self.index_path))
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            logger.info(f"Vector store saved ({self.index.ntotal} vectors)")
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")
            raise
    
    def clear(self):
        """Clear all vectors from store"""
        self.index.reset()
        self.metadata = []
        self.save()
        logger.info("Vector store cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics"""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "metadata_count": len(self.metadata)
        }