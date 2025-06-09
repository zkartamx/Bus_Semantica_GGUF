"""
Tests for the semantic search functionality.
"""

import unittest
import tempfile
import shutil
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import our modules
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import SemanticSearchDemo
from utils.document_processor import DocumentProcessor, chunk_text, preprocess_text
from utils.embeddings import EmbeddingManager, compare_embeddings

class TestSemanticSearch(unittest.TestCase):
    """Test cases for semantic search functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the embedding model to avoid downloading during tests
        with patch('sentence_transformers.SentenceTransformer'):
            self.demo = SemanticSearchDemo()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_documents(self):
        """Test adding documents to the collection."""
        texts = ["Test document 1", "Test document 2"]
        metadatas = [{"category": "test"}, {"category": "test"}]
        
        result = self.demo.add_documents(texts, metadatas)
        self.assertIn("Successfully added", result)
    
    def test_search_documents(self):
        """Test searching documents."""
        # Add some test documents first
        texts = ["Python programming language", "Machine learning algorithms"]
        self.demo.add_documents(texts)
        
        # Mock the collection query method
        mock_results = {
            'documents': [["Python programming language"]],
            'distances': [[0.1]],
            'metadatas': [[{"source": "test"}]]
        }
        
        with patch.object(self.demo.collection, 'query', return_value=mock_results):
            documents, distances, metadatas = self.demo.search_documents("programming", 1)
            
            self.assertEqual(len(documents), 1)
            self.assertEqual(documents[0], "Python programming language")
    
    def test_empty_search(self):
        """Test searching with empty query."""
        documents, distances, metadatas = self.demo.search_documents("", 5)
        self.assertEqual(len(documents), 0)
    
    def test_collection_stats(self):
        """Test getting collection statistics."""
        stats = self.demo.get_collection_stats()
        self.assertIn("Collection contains", stats)

class TestDocumentProcessor(unittest.TestCase):
    """Test cases for document processing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = DocumentProcessor()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_process_text_file(self):
        """Test processing a text file."""
        # Create a test text file
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("This is a test document.\n\nThis is another paragraph.")
        
        documents, metadatas = self.processor.process_text_file(test_file)
        
        self.assertEqual(len(documents), 2)
        self.assertEqual(documents[0], "This is a test document.")
        self.assertEqual(documents[1], "This is another paragraph.")
        self.assertEqual(len(metadatas), 2)
    
    def test_process_json_file(self):
        """Test processing a JSON file."""
        # Create a test JSON file
        test_file = os.path.join(self.temp_dir, "test.json")
        test_data = {
            "documents": [
                {"text": "Document 1", "category": "test"},
                {"text": "Document 2", "category": "test"}
            ]
        }
        
        import json
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        documents, metadatas = self.processor.process_json_file(test_file)
        
        self.assertEqual(len(documents), 2)
        self.assertEqual(documents[0], "Document 1")
        self.assertEqual(metadatas[0]["category"], "test")
    
    def test_chunk_text(self):
        """Test text chunking functionality."""
        long_text = "This is a very long text. " * 50
        chunks = chunk_text(long_text, chunk_size=100, overlap=20)
        
        self.assertGreater(len(chunks), 1)
        self.assertLessEqual(len(chunks[0]), 100)
    
    def test_preprocess_text(self):
        """Test text preprocessing."""
        text = "  This   is   a   test   text.  "
        processed = preprocess_text(text)
        
        self.assertEqual(processed, "This is a test text.")
    
    def test_preprocess_short_text(self):
        """Test preprocessing very short text."""
        text = "Hi"
        processed = preprocess_text(text)
        
        self.assertEqual(processed, "")

class TestEmbeddingManager(unittest.TestCase):
    """Test cases for embedding management."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the SentenceTransformer to avoid downloading models
        with patch('sentence_transformers.SentenceTransformer') as mock_st:
            mock_model = MagicMock()
            mock_model.encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            mock_st.return_value = mock_model
            
            self.embedding_manager = EmbeddingManager()
    
    def test_model_info(self):
        """Test getting model information."""
        info = self.embedding_manager.get_model_info()
        
        self.assertIn('dimensions', info)
        self.assertIn('description', info)
    
    def test_list_available_models(self):
        """Test listing available models."""
        models = EmbeddingManager.list_available_models()
        
        self.assertIn('sentence_transformers', models)
        self.assertIn('all-MiniLM-L6-v2', models['sentence_transformers'])
    
    def test_compare_embeddings(self):
        """Test embedding comparison."""
        with patch('utils.embeddings.get_embedding_model') as mock_get_model:
            mock_manager = MagicMock()
            mock_manager.encode.return_value = [[0.1, 0.2], [0.3, 0.4]]
            mock_manager.similarity.return_value = 0.8
            mock_get_model.return_value = mock_manager
            
            similarity = compare_embeddings("text1", "text2")
            self.assertEqual(similarity, 0.8)

if __name__ == '__main__':
    # Run tests
    unittest.main()
