"""
Embedding utilities for the ChromaDB Gradio Demo.
Handles different embedding models and configurations.
"""

import logging
from typing import List, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manages different embedding models and providers."""
    
    AVAILABLE_MODELS = {
        'sentence_transformers': {
            'all-MiniLM-L6-v2': {
                'dimensions': 384,
                'description': 'Fast and efficient, good for general use',
                'size': '~80MB'
            },
            'all-mpnet-base-v2': {
                'dimensions': 768,
                'description': 'Higher quality embeddings, slower',
                'size': '~420MB'
            },
            'paraphrase-multilingual-MiniLM-L12-v2': {
                'dimensions': 384,
                'description': 'Multilingual support',
                'size': '~420MB'
            }
        },
        'openai': {
            'text-embedding-ada-002': {
                'dimensions': 1536,
                'description': 'OpenAI embedding model (requires API key)',
                'size': 'API-based'
            }
        }
    }
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', provider: str = 'sentence_transformers'):
        self.model_name = model_name
        self.provider = provider
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the specified embedding model."""
        try:
            if self.provider == 'sentence_transformers':
                if not SENTENCE_TRANSFORMERS_AVAILABLE:
                    raise ImportError("sentence-transformers not available")
                
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded SentenceTransformer model: {self.model_name}")
                
            elif self.provider == 'openai':
                if not OPENAI_AVAILABLE:
                    raise ImportError("openai not available")
                
                # OpenAI client will be initialized when needed
                logger.info(f"OpenAI embedding model configured: {self.model_name}")
                
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings."""
        if not texts:
            return np.array([])
        
        try:
            if self.provider == 'sentence_transformers':
                return self.model.encode(texts, convert_to_numpy=True)
                
            elif self.provider == 'openai':
                return self._encode_openai(texts)
                
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            raise
    
    def _encode_openai(self, texts: List[str]) -> np.ndarray:
        """Encode texts using OpenAI API."""
        try:
            client = openai.OpenAI()
            
            embeddings = []
            for text in texts:
                response = client.embeddings.create(
                    model=self.model_name,
                    input=text
                )
                embeddings.append(response.data[0].embedding)
            
            return np.array(embeddings)
            
        except Exception as e:
            logger.error(f"Error with OpenAI embeddings: {e}")
            raise
    
    def get_model_info(self) -> dict:
        """Get information about the current model."""
        if self.provider in self.AVAILABLE_MODELS:
            if self.model_name in self.AVAILABLE_MODELS[self.provider]:
                return self.AVAILABLE_MODELS[self.provider][self.model_name]
        
        return {
            'dimensions': 'Unknown',
            'description': f'{self.provider} model: {self.model_name}',
            'size': 'Unknown'
        }
    
    @classmethod
    def list_available_models(cls) -> dict:
        """List all available embedding models."""
        return cls.AVAILABLE_MODELS
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            # Normalize embeddings
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def batch_similarity(self, query_embedding: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
        """Calculate similarities between a query and multiple embeddings."""
        try:
            # Normalize query embedding
            query_norm = np.linalg.norm(query_embedding)
            if query_norm == 0:
                return np.zeros(len(embeddings))
            
            query_normalized = query_embedding / query_norm
            
            # Normalize document embeddings
            doc_norms = np.linalg.norm(embeddings, axis=1)
            doc_norms[doc_norms == 0] = 1  # Avoid division by zero
            embeddings_normalized = embeddings / doc_norms[:, np.newaxis]
            
            # Calculate cosine similarities
            similarities = np.dot(embeddings_normalized, query_normalized)
            return similarities
            
        except Exception as e:
            logger.error(f"Error calculating batch similarities: {e}")
            return np.zeros(len(embeddings))

def get_embedding_model(model_name: str = 'all-MiniLM-L6-v2') -> EmbeddingManager:
    """Factory function to get an embedding model."""
    if model_name in EmbeddingManager.AVAILABLE_MODELS['sentence_transformers']:
        return EmbeddingManager(model_name, 'sentence_transformers')
    elif model_name in EmbeddingManager.AVAILABLE_MODELS['openai']:
        return EmbeddingManager(model_name, 'openai')
    else:
        logger.warning(f"Unknown model {model_name}, falling back to default")
        return EmbeddingManager()

def compare_embeddings(text1: str, text2: str, model_name: str = 'all-MiniLM-L6-v2') -> float:
    """Compare similarity between two texts."""
    try:
        embedding_manager = get_embedding_model(model_name)
        embeddings = embedding_manager.encode([text1, text2])
        
        if len(embeddings) == 2:
            return embedding_manager.similarity(embeddings[0], embeddings[1])
        else:
            return 0.0
            
    except Exception as e:
        logger.error(f"Error comparing embeddings: {e}")
        return 0.0
