import gradio as gr
import chromadb
from chromadb.config import Settings
import pandas as pd
import os
from typing import List, Tuple
import logging
from sentence_transformers import SentenceTransformer
import numpy as np
import random
import json
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticSearchDemo:
    def __init__(self):
        """Initialize the semantic search demo with ChromaDB and embedding model."""
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.setup_chroma()
        self.load_embedding_model()
        
    def setup_chroma(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Create ChromaDB client
            self.client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def load_embedding_model(self):
        """Load the sentence transformer model for embeddings."""
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def add_documents(self, texts: List[str], metadatas: List[dict] = None) -> str:
        """Add documents to the ChromaDB collection."""
        try:
            if not texts:
                return "No se proporcionaron documentos"
            
            # Generate unique IDs for documents
            ids = [f"doc_{uuid.uuid4().hex}" for _ in range(len(texts))]
            
            # Add documents to collection
            self.collection.add(
                documents=texts,
                metadatas=metadatas or [{"source": f"document_{i}"} for i in range(len(texts))],
                ids=ids
            )
            
            count = self.collection.count()
            return f"Se añadieron {len(texts)} documentos exitosamente. Documentos totales en la colección: {count}"
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return f"Error adding documents: {str(e)}"
    
    def search_documents(self, query: str, n_results: int = 5) -> Tuple[List[str], List[float], List[dict]]:
        """Search for similar documents using semantic search."""
        try:
            if not query.strip():
                return [], [], []
            
            # Perform search
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count())
            )
            
            documents = results['documents'][0] if results['documents'] else []
            distances = results['distances'][0] if results['distances'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            
            return documents, distances, metadatas
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return [], [], []
    
    def get_collection_stats(self) -> str:
        """Get statistics about the current collection."""
        try:
            if self.collection is None:
                return "Error: La colección no ha sido inicializada."
            count = self.collection.count()
            collection_name = self.collection.name
            return f"Colección Activa: '{collection_name}'\nDocumentos en la colección: {count}"
        except Exception as e:
            return f"Error al obtener estadísticas: {str(e)}"
    
    def clear_collection(self) -> str:
        """Clear all documents from the collection."""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection("documents")
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            return "Colección vaciada exitosamente"
        except Exception as e:
            return f"Error al vaciar la colección: {str(e)}"

    def add_sample_data(self):
        logger.info("Solicitud para añadir datos de ejemplo desde JSON recibida.")
        if self.collection is None:
            logger.error("Error: La colección no está inicializada.")
            return "Error: La colección no está inicializada. Intenta reiniciar.", self.get_collection_stats()

        json_file_path = "data/sample_documents.json"
        batch_size = 50
        
        docs_to_add = []
        metadatas_to_add = []
        ids_to_add = []

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sample_entries = data.get("documents", [])
            if not sample_entries:
                logger.info("El archivo JSON no contiene documentos o está mal formateado.")
                return "No se encontraron documentos en el archivo JSON.", self.get_collection_stats()

            for i, entry in enumerate(sample_entries):
                text = entry.get("text")
                if not text:
                    logger.warning(f"Entrada {i} en JSON no tiene campo 'text', saltando.")
                    continue
                
                docs_to_add.append(text)
                metadatas_to_add.append({
                    "category": entry.get("category", "desconocido"),
                    "topic": entry.get("topic", "desconocido"),
                    "difficulty": entry.get("difficulty", "desconocido"),
                    "source": "json_sample"
                })
                ids_to_add.append(f"json_doc_{i}")
            
            logger.info(f"Cargados {len(docs_to_add)} documentos desde {json_file_path}. Procediendo a añadir en lotes de {batch_size}.")

        except FileNotFoundError:
            logger.error(f"Error: No se encontró el archivo {json_file_path}")
            return f"Error: No se encontró el archivo {json_file_path}", self.get_collection_stats()
        except json.JSONDecodeError:
            logger.error(f"Error: El archivo {json_file_path} no es un JSON válido.")
            return f"Error: El archivo {json_file_path} no es un JSON válido.", self.get_collection_stats()
        except Exception as e:
            logger.error(f"Error inesperado al leer o procesar {json_file_path}: {e}")
            return f"Error inesperado al procesar {json_file_path}: {e}", self.get_collection_stats()

        if not docs_to_add:
             logger.info("No hay documentos para añadir después de procesar el JSON.")
             return "No hay documentos válidos para añadir desde el JSON.", self.get_collection_stats()

        total_docs_successfully_processed = 0
        num_batches = (len(docs_to_add) + batch_size - 1) // batch_size

        for i in range(num_batches):
            start_index = i * batch_size
            end_index = start_index + batch_size
            batch_docs = docs_to_add[start_index:end_index]
            batch_metadatas = metadatas_to_add[start_index:end_index]
            batch_ids = ids_to_add[start_index:end_index]

            logger.info(f"Procesando lote {i+1}/{num_batches} ({len(batch_docs)} documentos del JSON)...")
            try:
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                total_docs_successfully_processed += len(batch_docs)
                logger.info(f"Lote {i+1} (JSON) procesado. {len(batch_docs)} docs añadidos. Total en colección: {self.collection.count()}")
            except Exception as e:
                logger.error(f"Error al añadir el lote {i+1} (JSON) a ChromaDB: {e}")
        
        summary_message = f"Carga desde JSON completada. {total_docs_successfully_processed}/{len(docs_to_add)} documentos procesados."
        if total_docs_successfully_processed == 0 and len(docs_to_add) > 0:
            summary_message = "Error: No se pudo añadir ningún documento desde JSON. Revise los logs."
        elif total_docs_successfully_processed < len(docs_to_add) and total_docs_successfully_processed > 0:
            summary_message += " Algunos lotes pudieron fallar. Revise los logs."
        elif total_docs_successfully_processed == len(docs_to_add):
             summary_message = f"Todos los {len(docs_to_add)} documentos del JSON fueron procesados y añadidos exitosamente."

        logger.info(summary_message)
        return summary_message, self.get_collection_stats()

def search_interface(query: str, num_results: int):
    """Interface function for Gradio search."""
    if not query.strip():
        return "Por favor, ingresa una consulta de búsqueda", ""
    
    documents, distances, metadatas = demo.search_documents(query, num_results)
    
    if not documents:
        return "No se encontraron resultados", ""
    
    # Format results
    results_text = f"Se encontraron {len(documents)} resultados para: '{query}'\n\n"
    
    for i, (doc, distance, metadata) in enumerate(zip(documents, distances, metadatas)):
        similarity = 1 - distance  # Convert distance to similarity
        results_text += f"**Resultado {i+1}** (Similitud: {similarity:.3f})\n"
        results_text += f"Categoría: {metadata.get('category', 'N/A')} | Tópico: {metadata.get('topic', 'N/A')}\n"
        results_text += f"{doc}\n\n"
    
    stats = demo.get_collection_stats()
    return results_text, stats

def add_custom_document(text: str, category: str, topic: str):
    """Add a custom document to the collection."""
    if not text.strip():
        return "Por favor, ingresa el texto del documento", demo.get_collection_stats()
    
    metadata = {"category": category or "personalizado", "topic": topic or "general"}
    result = demo.add_documents([text], [metadata])
    return result, demo.get_collection_stats()

def clear_all_documents():
    """Clear all documents from the collection."""
    result = demo.clear_collection()
    return result, demo.get_collection_stats()

# Initialize the demo
demo = SemanticSearchDemo()

# Create Gradio interface
with gr.Blocks(title="Demostración de Búsqueda Semántica con ChromaDB", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🔍 Demostración de Búsqueda Semántica con ChromaDB
    
    Busca documentos usando consultas en lenguaje natural.
    """)
    
    with gr.Tab("Buscar Documentos"):
        gr.Markdown("### Buscar a través de la colección de documentos")
        
        with gr.Row():
            with gr.Column(scale=3):
                search_query = gr.Textbox(
                    label="Consulta de Búsqueda",
                    placeholder="Ingresa tu consulta de búsqueda (por ejemplo, 'algoritmos de aprendizaje automático')",
                    lines=2
                )
            with gr.Column(scale=1):
                num_results = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=5,
                    step=1,
                    label="Número de Resultados"
                )
        
        search_button = gr.Button("Buscar", variant="primary")
        
        with gr.Row():
            search_results = gr.Textbox(
                label="Resultados de la Búsqueda",
                lines=15,
                max_lines=20
            )
            collection_stats = gr.Textbox(label="Estadísticas de la Colección", lines=3)
        
        search_button.click(
            search_interface,
            inputs=[search_query, num_results],
            outputs=[search_results, collection_stats]
        )
    
    with gr.Tab("Gestionar Colección"):
        gr.Markdown("¿Estás seguro de que quieres vaciar la colección? Esta acción no se puede deshacer.")
        manage_collection_stats_display = gr.Textbox(
            label="Estado Actual de la Colección", 
            value=demo.get_collection_stats, 
            interactive=False, 
            lines=3
        )
        gr.Markdown("---")        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Añadir Datos de Ejemplo")
                add_sample_button = gr.Button("Añadir Datos de Ejemplo", variant="secondary")
                sample_result = gr.Textbox(label="Resultado", lines=2)
                
                add_sample_button.click(
                    demo.add_sample_data,
                    outputs=[sample_result, manage_collection_stats_display]
                )
            
            with gr.Column():
                gr.Markdown("#### Vaciar Colección")
                clear_button = gr.Button("Vaciar Colección", variant="stop")
                clear_result = gr.Textbox(label="Resultado", lines=2)
                
                clear_button.click(
                    clear_all_documents,
                    outputs=[clear_result, manage_collection_stats_display]
                )
        
        gr.Markdown("#### Añadir Documento Personalizado")
        with gr.Row():
            with gr.Column(scale=3):
                custom_text = gr.Textbox(
                    label="Texto del Documento",
                    placeholder="Ingresa el texto de tu documento...",
                    lines=4
                )
            with gr.Column(scale=1):
                custom_category = gr.Textbox(
                    label="Categoría",
                    placeholder="por ejemplo, tecnología, ciencia",
                    lines=1
                )
                custom_topic = gr.Textbox(
                    label="Tópico",
                    placeholder="por ejemplo, inteligencia artificial, programación",
                    lines=1
                )
        
        add_button = gr.Button("Añadir Documento", variant="primary")
        add_result = gr.Textbox(label="Resultado", lines=2)
        
        add_button.click(
            add_custom_document,
            inputs=[custom_text, custom_category, custom_topic],
            outputs=[add_result, manage_collection_stats_display]
        )
    
    with gr.Tab("Acerca de"):
        gr.Markdown("""
        ## Acerca de Esta Demostración
        
        Esta aplicación demuestra la búsqueda semántica utilizando:
        
        - **ChromaDB**: Una base de datos de embeddings de código abierto para almacenar y consultar vectores.
        - **Sentence Transformers**: Para generar embeddings de texto utilizando el modelo `all-MiniLM-L6-v2`.
        - **Gradio**: Para crear la interfaz web.
        
        ### Cómo Funciona
        
        1. **Almacenamiento de Documentos**: Los documentos de texto se convierten en embeddings y se almacenan en ChromaDB.
        2. **Búsqueda Semántica**: Cuando buscas, tu consulta también se convierte en un embedding.
        3. **Coincidencia de Similitud**: ChromaDB encuentra los embeddings de documentos más similares utilizando la similitud del coseno.
        4. **Resultados**: Los documentos se clasifican por similitud semántica con tu consulta.
        
        ### Características
        
        - Añadir documentos personalizados con categorías y tópicos.
        - Buscar con consultas en lenguaje natural.
        - Ver puntuaciones de similitud para los resultados.
        - Gestionar la colección de documentos.
        
        ### Consultas de Ejemplo para Probar
        
        - "inteligencia artificial y aprendizaje automático"
        - "construcción de interfaces web para modelos de IA"
        - "almacenamiento y búsqueda de datos de texto"
        - "lenguajes de programación para ciencia de datos"
        """)
    
    # Load initial stats
    app.load(lambda: demo.get_collection_stats(), outputs=collection_stats)

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        debug=True
    )
