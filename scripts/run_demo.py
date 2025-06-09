#!/usr/bin/env python3
"""
Script to run the ChromaDB Gradio Demo with various options.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run ChromaDB Gradio Demo")
    parser.add_argument("--port", type=int, default=7860, help="Port to run Gradio on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to run Gradio on")
    parser.add_argument("--share", action="store_true", help="Create public Gradio link")
    parser.add_argument("--load-sample", action="store_true", help="Load sample data on startup")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Embedding model to use")
    parser.add_argument("--db-path", default="./chroma_db", help="Path to ChromaDB storage")
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ["GRADIO_PORT"] = str(args.port)
    os.environ["EMBEDDING_MODEL"] = args.model
    os.environ["CHROMA_DB_PATH"] = args.db_path
    
    if args.share:
        os.environ["GRADIO_SHARE"] = "true"
    
    # Check if required packages are installed
    try:
        import chromadb
        import gradio
        import sentence_transformers
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        sys.exit(1)
    
    # Run the application
    print(f"Starting ChromaDB Gradio Demo...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Model: {args.model}")
    print(f"DB Path: {args.db_path}")
    
    try:
        # Import and run the app
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from app import app
        
        app.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            debug=True
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error running demo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
