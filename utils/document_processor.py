"""
Document processing utilities for the ChromaDB Gradio Demo.
Handles various document formats and text preprocessing.
"""

import os
import json
from typing import List, Dict, Tuple
import logging
from pathlib import Path

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles processing of various document formats."""
    
    def __init__(self):
        self.supported_formats = ['.txt', '.json']
        if PDF_AVAILABLE:
            self.supported_formats.append('.pdf')
        if DOCX_AVAILABLE:
            self.supported_formats.append('.docx')
    
    def process_text_file(self, file_path: str) -> Tuple[List[str], List[Dict]]:
        """Process a plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            
            if not content:
                return [], []
            
            # Split into paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            # Create metadata
            filename = Path(file_path).stem
            metadatas = [
                {
                    "source": filename,
                    "type": "text",
                    "paragraph": i + 1
                }
                for i in range(len(paragraphs))
            ]
            
            return paragraphs, metadatas
            
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            return [], []
    
    def process_json_file(self, file_path: str) -> Tuple[List[str], List[Dict]]:
        """Process a JSON file with documents."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            documents = []
            metadatas = []
            
            if isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, str):
                        documents.append(item)
                        metadatas.append({
                            "source": Path(file_path).stem,
                            "type": "json",
                            "index": i
                        })
                    elif isinstance(item, dict):
                        text = item.get('text', item.get('content', ''))
                        if text:
                            documents.append(text)
                            metadata = {
                                "source": Path(file_path).stem,
                                "type": "json",
                                "index": i
                            }
                            # Add any additional metadata from the item
                            for key, value in item.items():
                                if key not in ['text', 'content'] and isinstance(value, (str, int, float, bool)):
                                    metadata[key] = value
                            metadatas.append(metadata)
            
            elif isinstance(data, dict):
                if 'documents' in data:
                    docs_data = data['documents']
                    if isinstance(docs_data, list):
                        return self._process_document_list(docs_data, Path(file_path).stem)
                
                # Single document
                text = data.get('text', data.get('content', ''))
                if text:
                    documents.append(text)
                    metadata = {
                        "source": Path(file_path).stem,
                        "type": "json"
                    }
                    for key, value in data.items():
                        if key not in ['text', 'content'] and isinstance(value, (str, int, float, bool)):
                            metadata[key] = value
                    metadatas.append(metadata)
            
            return documents, metadatas
            
        except Exception as e:
            logger.error(f"Error processing JSON file {file_path}: {e}")
            return [], []
    
    def process_pdf_file(self, file_path: str) -> Tuple[List[str], List[Dict]]:
        """Process a PDF file."""
        if not PDF_AVAILABLE:
            logger.error("PyPDF2 not available. Install with: pip install PyPDF2")
            return [], []
        
        try:
            documents = []
            metadatas = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text().strip()
                    if text:
                        documents.append(text)
                        metadatas.append({
                            "source": Path(file_path).stem,
                            "type": "pdf",
                            "page": page_num + 1
                        })
            
            return documents, metadatas
            
        except Exception as e:
            logger.error(f"Error processing PDF file {file_path}: {e}")
            return [], []
    
    def process_docx_file(self, file_path: str) -> Tuple[List[str], List[Dict]]:
        """Process a DOCX file."""
        if not DOCX_AVAILABLE:
            logger.error("python-docx not available. Install with: pip install python-docx")
            return [], []
        
        try:
            documents = []
            metadatas = []
            
            doc = Document(file_path)
            
            for i, paragraph in enumerate(doc.paragraphs):
                text = paragraph.text.strip()
                if text:
                    documents.append(text)
                    metadatas.append({
                        "source": Path(file_path).stem,
                        "type": "docx",
                        "paragraph": i + 1
                    })
            
            return documents, metadatas
            
        except Exception as e:
            logger.error(f"Error processing DOCX file {file_path}: {e}")
            return [], []
    
    def process_file(self, file_path: str) -> Tuple[List[str], List[Dict]]:
        """Process a file based on its extension."""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return [], []
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.txt':
            return self.process_text_file(file_path)
        elif file_ext == '.json':
            return self.process_json_file(file_path)
        elif file_ext == '.pdf':
            return self.process_pdf_file(file_path)
        elif file_ext == '.docx':
            return self.process_docx_file(file_path)
        else:
            logger.error(f"Unsupported file format: {file_ext}")
            return [], []
    
    def process_directory(self, directory_path: str) -> Tuple[List[str], List[Dict]]:
        """Process all supported files in a directory."""
        if not os.path.exists(directory_path):
            logger.error(f"Directory not found: {directory_path}")
            return [], []
        
        all_documents = []
        all_metadatas = []
        
        for file_path in Path(directory_path).rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                documents, metadatas = self.process_file(str(file_path))
                all_documents.extend(documents)
                all_metadatas.extend(metadatas)
        
        return all_documents, all_metadatas
    
    def _process_document_list(self, docs_data: List, source: str) -> Tuple[List[str], List[Dict]]:
        """Helper method to process a list of documents."""
        documents = []
        metadatas = []
        
        for i, item in enumerate(docs_data):
            if isinstance(item, str):
                documents.append(item)
                metadatas.append({
                    "source": source,
                    "type": "json",
                    "index": i
                })
            elif isinstance(item, dict):
                text = item.get('text', item.get('content', ''))
                if text:
                    documents.append(text)
                    metadata = {
                        "source": source,
                        "type": "json",
                        "index": i
                    }
                    for key, value in item.items():
                        if key not in ['text', 'content'] and isinstance(value, (str, int, float, bool)):
                            metadata[key] = value
                    metadatas.append(metadata)
        
        return documents, metadatas

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            for i in range(end, max(start + chunk_size // 2, end - 100), -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

def preprocess_text(text: str) -> str:
    """Basic text preprocessing."""
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove very short texts
    if len(text.strip()) < 10:
        return ""
    
    return text.strip()
