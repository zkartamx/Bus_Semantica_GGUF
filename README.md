# ChromaDB Gradio Demo

A semantic search demonstration using ChromaDB as a vector database and Gradio for the web interface. This project showcases how to build a simple but powerful semantic search application that understands the meaning of text rather than just matching keywords.

## 🚀 Features

- **Semantic Search**: Find documents based on meaning, not just keywords
- **Interactive Web Interface**: Easy-to-use Gradio interface
- **Document Management**: Add, search, and manage documents
- **Real-time Results**: Instant search with similarity scores
- **Sample Data**: Pre-loaded examples to get started quickly
- **Custom Categories**: Organize documents with categories and topics

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/chroma_gradio_demo.git
   cd chroma_gradio_demo
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Usage

### Running the Application

Start the Gradio interface:

```bash
python app.py
```

The application will be available at `http://localhost:7860`

### Using the Interface

1. **Load Sample Data**: Click "Load Sample Documents" to populate the database with example documents
2. **Search Documents**: Enter natural language queries to find relevant documents
3. **Add Custom Documents**: Add your own documents with categories and topics
4. **Manage Collection**: View statistics and clear the database when needed

### Example Searches

Try these semantic search queries:

- "artificial intelligence and machine learning"
- "building web interfaces for AI models"
- "storing and searching text data"
- "programming languages for data science"

## 📁 Project Structure

```
chroma_gradio_demo/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── utils/               # Utility functions
│   ├── __init__.py
│   ├── document_processor.py
│   └── embeddings.py
├── data/                # Sample data directory
│   └── sample_documents.json
├── tests/               # Test files
│   ├── __init__.py
│   └── test_search.py
└── chroma_db/           # ChromaDB storage (created automatically)
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Available configuration options:

- `CHROMA_DB_PATH`: Path to ChromaDB storage (default: "./chroma_db")
- `EMBEDDING_MODEL`: Sentence transformer model name (default: "all-MiniLM-L6-v2")
- `GRADIO_PORT`: Port for Gradio interface (default: 7860)

### Advanced Configuration

You can modify the embedding model and ChromaDB settings in `app.py`:

```python
# Change embedding model
self.embedding_model = SentenceTransformer('your-preferred-model')

# Modify ChromaDB settings
self.client = chromadb.PersistentClient(
    path="./custom_db_path",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)
```

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/
```

## 📊 How It Works

### 1. Document Processing
- Text documents are processed and converted to embeddings using Sentence Transformers
- Documents are stored in ChromaDB with metadata (categories, topics)

### 2. Semantic Search
- Search queries are converted to embeddings using the same model
- ChromaDB performs similarity search using cosine distance
- Results are ranked by semantic similarity

### 3. Vector Database
- ChromaDB stores embeddings efficiently for fast retrieval
- Supports metadata filtering and hybrid search capabilities

## 🔍 API Reference

### SemanticSearchDemo Class

#### Methods

- `add_documents(texts, metadatas)`: Add documents to the collection
- `search_documents(query, n_results)`: Search for similar documents
- `get_collection_stats()`: Get collection statistics
- `clear_collection()`: Clear all documents

#### Example Usage

```python
from app import SemanticSearchDemo

# Initialize
demo = SemanticSearchDemo()

# Add documents
texts = ["Your document text here"]
metadatas = [{"category": "example", "topic": "demo"}]
demo.add_documents(texts, metadatas)

# Search
results = demo.search_documents("your search query", n_results=5)
documents, distances, metadatas = results
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ChromaDB](https://www.trychroma.com/) for the vector database
- [Gradio](https://gradio.app/) for the web interface framework
- [Sentence Transformers](https://www.sbert.net/) for text embeddings
- [Hugging Face](https://huggingface.co/) for the pre-trained models

## 🐛 Troubleshooting

### Common Issues

1. **Installation Problems**:
   - Make sure you have Python 3.8+
   - Use a virtual environment to avoid conflicts
   - Update pip: `pip install --upgrade pip`

2. **Memory Issues**:
   - The embedding model requires ~100MB of RAM
   - For large document collections, consider using a smaller model

3. **Port Conflicts**:
   - Change the port in the `app.launch()` call
   - Or set the `GRADIO_PORT` environment variable

### Getting Help

- Check the [Issues](https://github.com/yourusername/chroma_gradio_demo/issues) page
- Create a new issue with detailed error information
- Include your Python version and operating system

## 🔮 Future Enhancements

- [ ] Support for PDF and DOCX file uploads
- [ ] Multiple embedding model options
- [ ] Advanced filtering and search options
- [ ] Export/import functionality for collections
- [ ] Integration with external APIs
- [ ] Batch document processing
- [ ] Search analytics and insights
