# Demo de Gradio con ChromaDB

Esta es una demostración de búsqueda semántica utilizando ChromaDB como base de datos vectorial y Gradio para la interfaz web. Este proyecto muestra cómo construir una aplicación de búsqueda semántica simple pero potente que comprende el significado del texto en lugar de solo coincidir con palabras clave.

## 🚀 Características

- **Búsqueda Semántica**: Encuentra documentos basados en el significado, no solo en palabras clave.
- **Interfaz Web Interactiva**: Interfaz de Gradio fácil de usar.
- **Gestión de Documentos**: Añade, busca y gestiona documentos.
- **Resultados en Tiempo Real**: Búsqueda instantánea con puntuaciones de similitud.
- **Datos de Muestra**: Ejemplos precargados para empezar rápidamente.
- **Categorías Personalizadas**: Organiza documentos con categorías y temas.

## 🛠️ Instalación

### Prerrequisitos

- Python 3.8 o superior
- Gestor de paquetes pip

### Configuración

1.  **Clona el repositorio**:
    ```bash
    git clone https://github.com/yourusername/chroma_gradio_demo.git
    cd chroma_gradio_demo
    ```

2.  **Crea un entorno virtual** (recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instala las dependencias**:
    ```bash
    pip install -r requirements.txt
    ```
    > **Nota**: El paquete `llama-cpp-python` (una dependencia clave para el soporte de modelos GGUF) puede requerir un compilador de C++ y otras herramientas de compilación. Por favor, consulta la [documentación oficial de llama-cpp-python](https://github.com/abetlen/llama-cpp-python#installation) para obtener instrucciones detalladas de instalación si encuentras problemas durante este paso.

## 🎯 Uso

### Ejecutando la Aplicación

Inicia la interfaz de Gradio:

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:7865` (o el puerto especificado por la variable de entorno `GRADIO_SERVER_PORT`).

### Usando la Interfaz

1.  **Cargar Datos de Muestra**: Haz clic en "Cargar documentos de ejemplo" para poblar la base de datos con documentos de ejemplo.
2.  **Buscar Documentos**: Introduce consultas en lenguaje natural para encontrar documentos relevantes.
3.  **Añadir Documentos Personalizados**: Añade tus propios documentos con categorías y temas.
4.  **Gestionar Colección**: Visualiza estadísticas y limpia la base de datos cuando sea necesario.

### Búsquedas de Ejemplo

Prueba estas consultas de búsqueda semántica:

- "inteligencia artificial y aprendizaje automático"
- "construyendo interfaces web para modelos de IA"
- "almacenamiento y búsqueda de datos de texto"
- "lenguajes de programación para ciencia de datos"

## 📁 Estructura del Proyecto

```
chroma_gradio_demo/
├── app.py                 # Archivo principal de la aplicación (UI de Gradio, API, lógica de embedding usando LlamaCppEmbeddingFunction)
├── requirements.txt       # Dependencias de Python
├── README.md              # Este archivo
├── .env.example           # Plantilla de variables de entorno
├── .gitignore             # Reglas de Git ignore
├── utils/                 # Funciones de utilidad
│   ├── __init__.py
│   ├── document_processor.py
├── data/                  # Directorio de datos de muestra
│   └── sample_documents.json
├── tests/                 # Archivos de prueba
│   ├── __init__.py
│   └── test_search.py
└── chroma_db/             # Almacenamiento de ChromaDB (creado automáticamente)
```

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` copiando `.env.example` y luego personalízalo para tu configuración:

```bash
cp .env.example .env
```

Edita el archivo `.env`. Variables clave (consulta `app.py` y `.env.example` para los valores predeterminados y la lista completa):

- `GGUF_MODEL_REPO`: ID del repositorio de Hugging Face para el modelo de embedding GGUF (ej., "leliuga/all-MiniLM-L6-v2-GGUF").
- `GGUF_MODEL_FILE`: Nombre específico del archivo del modelo GGUF dentro del repositorio (ej., "all-MiniLM-L6-v2.Q4_K_M.gguf").
- `CHROMA_DB_PATH`: Ruta del sistema de archivos para la persistencia de ChromaDB (predeterminado: "./chroma_db").
- `CHROMA_COLLECTION_NAME`: Nombre de la colección dentro de ChromaDB (predeterminado: "documents_gguf").
- `GRADIO_SERVER_PORT`: Puerto para la interfaz web de Gradio (predeterminado: 7865).
- `GRADIO_SHARE`: Establece en `true` para crear un enlace público de Gradio share (predeterminado: `false`).

### Configuración Avanzada

Puedes modificar el modelo de embedding y la configuración de ChromaDB en `app.py`:

```python
# El modelo de embedding (LlamaCppEmbeddingFunction) se configura usando las variables de entorno GGUF_MODEL_REPO
# y GGUF_MODEL_FILE, como se define en app.py.
# Consulta la sección 'Variables de Entorno' más arriba para más detalles.

# Modificar la configuración de ChromaDB
self.client = chromadb.PersistentClient(
    path="./custom_db_path",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)
```

## 🧪 Pruebas

Ejecuta la suite de pruebas:

```bash
python -m pytest tests/
```

## 📊 Cómo Funciona

### 1. Procesamiento de Documentos
- Los documentos de texto se convierten en embeddings usando un modelo GGUF (ej., `all-MiniLM-L6-v2-GGUF`) mediante la biblioteca `llama-cpp-python`, gestionado por `LlamaCppEmbeddingFunction` en `app.py`.
- Los documentos se almacenan en ChromaDB con metadatos (categorías, temas).

### 2. Búsqueda Semántica
- Las consultas de búsqueda se convierten en embeddings usando el mismo modelo.
- ChromaDB realiza una búsqueda de similitud usando la distancia del coseno.
- Los resultados se clasifican por similitud semántica.

### 3. Base de Datos Vectorial
- ChromaDB almacena embeddings eficientemente para una rápida recuperación.
- Soporta filtrado por metadatos y capacidades de búsqueda híbrida.

## 🔍 Referencia de API

### Clase SemanticSearchDemo

#### Métodos

- `add_documents(texts, metadatas)`: Añade documentos a la colección.
- `search_documents(query, n_results)`: Busca documentos similares.
- `get_collection_stats()`: Obtiene estadísticas de la colección.
- `clear_collection()`: Elimina todos los documentos.

#### Ejemplo de Uso

```python
from app import SemanticSearchDemo

# Inicializar
demo = SemanticSearchDemo()

# Añadir documentos
texts = ["El texto de tu documento aquí"]
metadatas = [{"category": "ejemplo", "topic": "demo"}]
demo.add_documents(texts, metadatas)

# Buscar
results = demo.search_documents("tu consulta de búsqueda", n_results=5)
documents, distances, metadatas = results
```

## 🤝 Contribuciones

1.  Haz un fork del repositorio.
2.  Crea una rama para tu nueva característica (`git checkout -b feature/amazing-feature`).
3.  Confirma tus cambios (`git commit -m 'Añade una característica increíble'`).
4.  Empuja a la rama (`git push origin feature/amazing-feature`).
5.  Abre un Pull Request.

## 📝 Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- [ChromaDB](https://www.trychroma.com/) por la base de datos vectorial.
- [Gradio](https://gradio.app/) por el framework de la interfaz web.
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) por la inferencia eficiente de modelos GGUF y embeddings de texto.
- [Hugging Face](https://huggingface.co/) por los modelos preentrenados.

## 🐛 Solución de Problemas

### Problemas Comunes

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
