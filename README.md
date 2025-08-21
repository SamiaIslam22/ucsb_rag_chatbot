# 🤖 UCSB RAG Chatbot System
### Advanced Modular RAG Implementation with Multi-Document Support and Intelligent Knowledge Management

A comprehensive, production-ready implementation of a RAG (Retrieval-Augmented Generation) pipeline that handles diverse document types, web scraping, and intelligent search across nanofabrication knowledge bases. Specifically designed to process and make searchable the extensive [UCSB wiki pages](https://wiki.nanofab.ucsb.edu/wiki/Special:AllPages) containing critical nanofabrication protocols, equipment manuals, and research procedures. Built with Streamlit, advanced document processing, multiple LLM providers, and semantic search to demonstrate modern AI-powered knowledge management systems for research facilities.

## 🎯 Overview

This project demonstrates how to build a complete, modular RAG system that can intelligently search across multiple document types, web content, and structured data from the [UCSB wiki pages](https://wiki.nanofab.ucsb.edu/wiki/Special:AllPages). Each module handles a specific aspect of the pipeline, making it easy to learn, modify, and extend for real-world applications in research facilities and technical organizations.

### What is RAG?
RAG (Retrieval-Augmented Generation) is a technique that combines:
- **Retrieval**: Finding relevant information from the [UCSB wiki pages](https://wiki.nanofab.ucsb.edu/wiki/Special:AllPages) and other knowledge sources
- **Generation**: Using that information to generate accurate, contextual responses about nanofabrication procedures
- **Intelligence**: Learning from user interactions and improving knowledge discovery over time

### System Architecture
```
📄 UCSB Wiki → 🔄 Processing → 🧠 Embeddings → 🔍 Vector Search → 💬 LLM Response
      ↓             ↓              ↓               ↓              ↓
🌐 Web Content → 📊 Tables → 🎯 Knowledge Base → 🔎 Similarity → ✨ Final Answer
      ↓             ↓              ↓               ↓              ↓
📋 Documents  → 🖼️ Images  → 📚 Chunked Data → 📈 Ranking → 📖 Citations
```

## 📁 Project Structure

```
UCSB_RAG_CHATBOT/
├── README.md                              # 📖 This comprehensive documentation
├── requirements.txt                       # 📦 Python dependencies
├── 📁 venv/                               # 🐍 Virtual environment
├── .env                                   # 🔐 Environment variables
├── .gitignore                            # 🚫 Git ignore patterns
│
├── 📁 backend/                           # 🔧 Core backend services
│   ├── __pycache__/                     # Python cache files
│   ├── main.py                          # 🎯 Main orchestrator and CLI interface
│   │
│   ├── 📁 ai_services/                  # 🧠 AI & LLM Integration
│   │   ├── __pycache__/                 
│   │   ├── __init__.py                  # Package initialization
│   │   ├── embedding_generator.py      # 🎯 Vector embedding generation
│   │   ├── openai_services.py          # 🤖 OpenAI API integration
│   │   └── vector_search.py            # 🔍 Semantic similarity search
│   │
│   ├── 📁 chunking/                     # 🔀 Content Processing
│   │   ├── __pycache__/                 
│   │   ├── __init__.py                  # Package initialization
│   │   └── chunking.py                  # 🔄 Text and table chunking engine
│   │
│   └── 📁 extraction/                   # 🌐 Content Extraction & Scraping
│       ├── __pycache__/                 
│       ├── __init__.py                  # Package initialization
│       ├── wiki_images.py              # 🖼️ Image extraction from UCSB wiki
│       ├── wiki_table.py               # 📊 Table extraction from UCSB wiki
│       └── wiki_texts.py               # 📝 Text extraction from UCSB wiki
│
├── 📁 csv_dataframes/                   # 📊 Processed Data Storage
│   ├── 📁 embeddings/                   # 🧠 Vector embeddings storage
│   │   └── chunked_pages_with_embeddings.csv # 🎯 Final vectorized knowledge base
│   ├── 📁 processed/                    # 🔄 Processed content
│   │   └── chunked_pages.csv            # 📋 Combined processed chunks
│   └── 📁 raw/                          # 📄 Raw extracted data
│       ├── 📁 scratch/                  # 🗂️ Individual table markdown files
│       │   └── [Individual markdown versions of extracted tables]
│       ├── wiki_images.csv              # 🖼️ Extracted image metadata
│       ├── wiki_tables.csv              # 📊 Extracted table data
│       └── wiki_texts.csv               # 📝 Extracted text content
│
├── 📁 database/                         # 🗄️ Database Operations
│   ├── bootstrap.db.py                  # 🚀 Database initialization
│   ├── chunk.csv.py                    # 📊 CSV chunk processing
│   └── search.py                        # 🔍 Database search operations
│
├── 📁 experiments/                      # 🧪 Experimental Features
│   └── hybrid_search.py                # 🔬 Hybrid search experiments
│
└── 📁 frontend/                         # 🎨 User Interface
    └── app.py                           # 🌐 Primary Streamlit web interface
```

## 🧩 Module Architecture

### 1. **backend/extraction/wiki_table.py** - UCSB Wiki Table Extraction Engine
**Purpose**: Extract structured data from [UCSB wiki pages](https://wiki.nanofab.ucsb.edu/wiki/Special:AllPages) using advanced table processing

```python
def table_to_markdown(table)
def ultra_clean_text_for_csv(text_content)
def get_page_name_from_url(url)
```

**What it does**:
- **Advanced Table Detection**: Uses Docling's DocumentConverter to identify and extract tables from UCSB wiki pages
- **Intelligent Cleaning**: Converts complex table structures to clean markdown format
- **Metadata Preservation**: Maintains source URLs, page names, and table numbering
- **Individual File Generation**: Creates separate markdown files in `/csv_dataframes/raw/scratch/` for each table
- **CSV Compilation**: Aggregates all table data into `wiki_tables.csv`

**UCSB Wiki Processing Pipeline**:
- URL Processing: Fetches content from UCSB nanofab wiki URLs
- Table Detection: Identifies equipment tables, protocol tables, and process parameters
- Content Extraction: Converts tables to clean markdown preserving scientific data
- Individual Storage: Saves each table as separate `.md` file in scratch folder
- Data Cleaning: Removes special characters, normalizes spacing for technical content
- Metadata Addition: Adds source tracking and equipment/protocol categorization

### 2. **backend/extraction/wiki_texts.py** - Text Content Extraction Engine
**Purpose**: Extract and process textual content from [UCSB wiki pages](https://wiki.nanofab.ucsb.edu/wiki/Special:AllPages)

```python
def extract_title_from_url(url)
async def scrape(url)
async def run_all_scrapes(urls)
```

**What it does**:
- **URL Title Extraction**: Converts wiki URLs to clean page titles by extracting and formatting the page name
- **Asynchronous Web Scraping**: Uses Crawl4AI to extract content from wiki pages with proper CSS selectors
- **Content Processing**: Focuses on the main content area (`div#mw-content-text`) while excluding navigation and footer elements
- **Batch Processing**: Processes multiple wiki URLs efficiently with async operations
- **CSV Output**: Creates structured `wiki_texts.csv` with title, URL, and markdown content

**Key Features**:
- Uses `CrawlerRunConfig` with content filtering to exclude external links and social media
- Bypasses cache to ensure fresh content extraction
- Handles errors gracefully and continues processing other pages
- Outputs clean markdown format suitable for chunking

### 3. **backend/extraction/wiki_images.py** - Image Metadata and Analysis Engine
**Purpose**: Extract, analyze, and catalog images from [UCSB wiki pages](https://wiki.nanofab.ucsb.edu/wiki/Special:AllPages) with AI-powered descriptions

```python
def normalize_mediawiki_image_url(url: str) -> str
async def download_image_as_data_url(url: str, client_http) -> str
def summarize_image_with_context(data_url: str, context_text: str, alt=None, caption=None) -> str
async def main()
```

**What it does**:
- **MediaWiki Image Processing**: Converts thumbnail URLs to original image URLs for better quality analysis
- **Image Download & Encoding**: Downloads images and converts them to base64 data URLs for AI processing
- **AI-Powered Image Analysis**: Uses OpenAI's vision model (gpt-4o-mini) to generate detailed descriptions
- **Context-Aware Descriptions**: Incorporates page context, alt text, and captions for more accurate analysis
- **Deduplication**: Removes duplicate images and filters out UI elements like logos and sprites
- **CSV Output**: Creates `wiki_images.csv` with comprehensive image metadata and AI-generated summaries

**Key Features**:
- Integrates with `wiki_texts.py` to provide page context for better image understanding
- Handles various image formats (PNG, JPEG, GIF, WebP)
- Clips context to prevent overwhelming the AI model
- Robust error handling for failed downloads or API calls

### 4. **backend/chunking/chunking.py** - Unified Content Processing
**Purpose**: Intelligent processing of all extracted UCSB wiki content (text, tables, images) into searchable chunks

```python
def parse_table_to_rows(table_markdown)
# Main processing logic (no specific functions - direct processing)
```

**What it does**:
- **Multi-Source Processing**: Handles wiki text, equipment tables, and image metadata with different chunking approaches
- **Text Chunking**: Uses LangChain's CharacterTextSplitter (1000 chars, 2 char overlap) for semantic boundaries
- **Table Processing**: Parses markdown tables into structured rows with `parse_table_to_rows()` function
- **Content Type Tracking**: Labels chunks as "text", "table", "table_row", or "image" for downstream processing
- **Unified Output**: Combines all content types into `processed/chunked_pages.csv`

**Processing Strategy**:
- **Text Content**: Loads from `csv_dataframes/raw/wiki_texts.csv` and splits into manageable chunks
- **Table Content**: Loads from `csv_dataframes/raw/wiki_tables.csv`, parses markdown tables into individual rows
- **Image Content**: Loads from `csv_dataframes/raw/wiki_images.csv` and creates single chunks per image
- **Error Handling**: Gracefully skips missing files and continues processing available content

**Data Flow**:
```
raw/wiki_texts.csv + raw/wiki_tables.csv + raw/wiki_images.csv
                            ↓
            Direct processing in chunking.py
                            ↓
              processed/chunked_pages.csv
```

**Key Features**:
- Uses markdown table parsing to extract structured data from equipment tables
- Maintains complete context for each chunk with metadata (URL, title, character count)
- Processes large datasets efficiently with progress reporting
- Creates detailed statistics showing breakdown by content type

### 5. **backend/ai_services/embedding_generator.py** - Vector Embedding Pipeline
**Purpose**: Convert all UCSB wiki chunks (text, tables, and images) into searchable vector representations

```python
def embed_chunks_with_openai(chunks_df, client)
```

**What it does**:
- **Universal Embedding**: Creates vectors for wiki text, equipment tables, and image content using text-embedding-3-small
- **Batch Processing**: Efficiently processes large UCSB wiki datasets with rate limiting (0.1 second delays)
- **Error Recovery**: Gracefully handles API failures and continues processing other chunks
- **Metadata Preservation**: Maintains all equipment and protocol information in structured JSON metadata
- **Output**: Creates `embeddings/chunked_pages_with_embeddings.csv` - the final searchable knowledge base

**Key Features**:
- Uses OpenAI's text-embedding-3-small model (1536 dimensions)
- Preserves content_type information for downstream filtering
- Stores embeddings as JSON arrays for easy loading
- Comprehensive error handling with detailed logging

### 6. **backend/ai_services/vector_search.py** - Semantic Search Engine
**Purpose**: Find relevant UCSB wiki chunks using vector similarity across all content types

```python
def vector_similarity_search(query_text, df, client, k=5)
def embed_query(query_text, client)
def load_chunked_data_from_csv(csv_path)
```

**What it does**:
- **Unified Search**: Searches across wiki text, equipment tables, and image metadata seamlessly
- **Equipment-Aware**: Understands queries about specific tools, protocols, and nanofab procedures
- **Optimized Similarity**: Uses numpy dot product operations for efficiency with OpenAI embeddings
- **Content Type Support**: Handles text, table, table_row, and image chunks with proper type inference
- **Score Transparency**: Provides similarity scores for result analysis in technical contexts

**Key Features**:
- Automatically loads and converts JSON embeddings back to numpy arrays
- Infers content types when missing from older data
- Shows content type distribution for transparency
- Returns top-k results with similarity scores and metadata

### 7. **backend/ai_services/openai_services.py** - Response Generation
**Purpose**: Generate contextual responses using retrieved UCSB wiki chunks as supporting evidence

```python
def format_chunk_for_display(chunk_row)
def generate_response_with_context(user_prompt, retrieved_chunks, client)
# Contains: client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
```

**What it does**:
- **Content-Type Aware Formatting**: Intelligently formats different chunk types (text, table, table_row, image) for optimal display
- **Context Assembly**: Combines retrieved wiki text, equipment tables, and image data into coherent context
- **Advanced Prompt Engineering**: Uses gpt-4o-mini with specialized system prompts for nanofabrication queries
- **Source Attribution**: Returns enhanced source information with similarity scores and content types
- **Multi-Content Integration**: Seamlessly handles mixed content from equipment specifications and procedure text

**Key Features**:
- Formats table row JSON data into readable bullet points
- Handles complete markdown tables with proper formatting
- Uses temperature=0.1 for focused, technical responses
- Supports up to 4000 tokens for comprehensive answers
- Returns both response text and enhanced source metadata

**Content Type Processing**:
- **table_row**: Parses JSON and formats as structured bullet points
- **table**: Displays complete markdown tables in code blocks
- **text**: Shows actual content for procedure descriptions
- **image**: Integrates image analysis summaries into responses

### 8. **backend/main.py** - System Orchestrator and CLI Interface
**Purpose**: Central coordination of all backend components and command-line interface for the RAG system

```python
class NanofabRAGPipeline:
    def step_1_extract_wiki_texts(self)
    def step_2_extract_wiki_tables(self)
    def step_3_extract_wiki_images(self)
    def step_4_process_chunking(self)
    def step_5_generate_embeddings(self)
    def run_complete_pipeline(self)
```

**What it does**:
- **Pipeline Orchestration**: Coordinates the complete RAG pipeline from extraction to embeddings
- **Step-by-Step Execution**: Manages each phase of data processing with proper error handling
- **File Existence Checking**: Skips steps if output files already exist to avoid reprocessing
- **Module Integration**: Imports and executes extraction modules (wiki_texts, wiki_table, wiki_images)
- **Async Coordination**: Handles async operations for image processing and web scraping
- **Logging & Monitoring**: Provides detailed logging for each step with success/failure reporting

**Pipeline Steps**:
1. **Text Extraction**: Runs `wiki_texts.py` to scrape and process wiki content
2. **Table Extraction**: Executes `wiki_table.py` to extract and convert tables to markdown
3. **Image Processing**: Calls `wiki_images.py` for AI-powered image analysis
4. **Content Chunking**: Processes all extracted data through the chunking pipeline
5. **Embedding Generation**: Creates vector embeddings for the final knowledge base

**Key Features**:
- Uses pathlib for robust file path handling
- Implements proper async/await patterns for web scraping operations
- Provides clear status reporting with emojis and detailed error messages
- Supports incremental processing by checking for existing output files

### 9. **frontend/app.py** - Interactive Web Interface
**Purpose**: Provide user-friendly access to the UCSB wiki RAG system through Streamlit

```python
def load_chunked_data(csv_path)
def display_content_type_breakdown(df)
def handle_chat_interface()
def show_source_attribution(sources, df)
```

**What it does**:
- **Intuitive Interface**: Clean, modern web interface for researchers and facility users
- **UCSB Wiki Integration**: Shows breakdown of text vs. table vs. image chunks in knowledge base
- **Real-time Search**: Interactive search across all UCSB nanofab documentation
- **Source Transparency**: Displays exactly which wiki pages, markdown tables, and images informed each response
- **Markdown Table Access**: Direct links to individual table markdown files in the scratch folder

### 10. **database/** - Cloud Database Operations with Neon Tech
**Purpose**: Upload CSV dataframes to cloud database and transform them into organized, queryable database structures

**bootstrap.db.py**:
- **Cloud Database Initialization**: Sets up Neon Tech PostgreSQL database for scalable storage
- **CSV to Database Migration**: Uploads processed CSV dataframes to cloud storage
- **Schema Management**: Creates optimized database structure for vector search and metadata queries
- **Connection Management**: Handles secure connections to Neon Tech cloud infrastructure

**chunk.csv.py**:
- **CSV Processing Pipeline**: Transforms local CSV dataframes into database-ready format
- **Data Validation**: Ensures data integrity before cloud upload
- **Batch Processing**: Efficiently handles large datasets for cloud migration

**search.py**:
- **Cloud-Based Search**: Provides efficient search operations directly against the cloud database
- **Vector Search Optimization**: Leverages Neon Tech's PostgreSQL extensions for vector similarity search
- **Query Performance**: Optimized database queries for fast retrieval across large knowledge bases

**Key Features**:
- **Neon Tech Integration**: Uses Neon Tech's serverless PostgreSQL for scalable cloud storage
- **API Key Required**: Requires your own Neon Tech API credentials for database connection
- **Production Ready**: Enables deployment-ready database infrastructure for the RAG system
- **Vector Support**: Utilizes pgvector extension for efficient similarity search in the cloud
- **Cost Effective**: Serverless architecture scales automatically based on usage

## 🔄 Complete UCSB Wiki Data Flow Architecture

```
📄 UCSB Wiki Pages ([UCSB wiki pages](https://wiki.nanofab.ucsb.edu/wiki/Special:AllPages))
         ↓
🌐 backend/main.py (Orchestrates extraction modules)
         ↓
┌─────────────────┬─────────────────┬─────────────────┐
│ wiki_texts.py   │ wiki_table.py   │ wiki_images.py  │
│       ↓         │       ↓         │       ↓         │
│ wiki_texts.csv  │ wiki_tables.csv │ wiki_images.csv │
└─────────────────┴─────────────────┴─────────────────┘
         ↓                ↓                ↓
📊 Individual table markdown files saved to raw/scratch/
         ↓
🔄 backend/chunking/chunking.py (Processes all content types)
         ↓
📋 processed/chunked_pages.csv (Combined chunks)
         ↓
🧠 backend/ai_services/embedding_generator.py (Vectorization)
         ↓
🎯 embeddings/chunked_pages_with_embeddings.csv (Final knowledge base)
         ↓
❓ User Query → frontend/app.py
         ↓
🔍 backend/ai_services/vector_search.py (Semantic search)
         ↓
📋 Relevant Content (Text + Tables + Images)
         ↓
💬 backend/ai_services/openai_services.py (Response generation)
         ↓
✨ Final AI Response with Source Attribution
```

## 🚀 Getting Started

## 📦 Dependencies & Setup Requirements

### Core Dependencies
```bash
pip install -r requirements.txt
```
**Key packages include:**
- `streamlit` - Web interface framework
- `pandas numpy` - Data processing and manipulation
- `openai` - OpenAI API integration for embeddings and chat
- `python-dotenv` - Environment variable management
- `langchain-text-splitters` - Text chunking for RAG pipeline
- `docling` - Advanced document processing and table extraction
- `beautifulsoup4` - Web scraping and HTML parsing
- `crawl4ai` - Advanced web crawling capabilities

### Cloud Database Setup (Neon Tech)
For production deployment with cloud database:
```bash
pip install psycopg2-binary pgvector
```
**Additional requirements:**
- **Neon Tech Account**: Sign up at [neon.tech](https://neon.tech) for serverless PostgreSQL
- **Database URL**: Get your connection string from Neon Tech dashboard
- **pgvector Extension**: Automatically enabled for vector similarity search

### Environment Setup
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=your_neon_tech_database_url_here
```

### Quick Start Guide

#### Step 1: Extract All UCSB Wiki Content
```bash
cd backend/
python main.py
```
- Orchestrates extraction modules (wiki_texts.py, wiki_table.py, wiki_images.py)
- Extracts content from [UCSB wiki pages](https://wiki.nanofab.ucsb.edu/wiki/Special:AllPages)
- Creates `raw/wiki_texts.csv`, `raw/wiki_tables.csv`, and `raw/wiki_images.csv`
- Saves individual table markdown files to `raw/scratch/` folder
- Processes equipment specifications, process parameters, and protocol tables

#### Step 2: Process and Chunk Content
```bash
cd backend/chunking/
python chunking.py
```
- Combines all extracted UCSB wiki content (text, tables, images)
- Creates unified chunk structure preserving technical information
- Outputs `processed/chunked_pages.csv` with mixed content types

#### Step 3: Generate Vector Embeddings
```bash
cd backend/ai_services/
python embedding_generator.py
```
- Creates vector embeddings for all UCSB wiki chunks
- Processes text content, equipment specifications, and image metadata
- Outputs `embeddings/chunked_pages_with_embeddings.csv` - the final searchable knowledge base

#### Step 4: Launch Web Interface
```bash
cd frontend/
streamlit run app.py
```
- Opens web interface at `http://localhost:8501`
- Provides interactive search across UCSB nanofab knowledge
- Shows source attribution to specific wiki pages and markdown tables

#### Step 5: Run Complete Pipeline (Alternative)
```bash
cd backend/
python main.py
```
- Runs the complete RAG pipeline from the main orchestrator
- Tests system with nanofab-specific queries
- Demonstrates end-to-end functionality

#### Step 6: Setup Cloud Database (Optional)
```bash
cd database/
python bootstrap.db.py
```
- **Cloud Migration**: Uploads CSV dataframes to Neon Tech PostgreSQL database
- **Scalable Storage**: Enables production-ready, serverless database infrastructure
- **Vector Search**: Sets up pgvector extension for efficient similarity search in the cloud
- **API Integration**: Requires Neon Tech API credentials in `.env` file
- **Performance Optimization**: Enables faster search operations for large knowledge bases


## 🔍 Example Use Cases

### Equipment Queries
- *"What are the specifications for the Oxford RIE system?"*
- *"How do I clean the SEM sample holder?"*
- *"What safety procedures are required for the furnace?"*

### Process Queries
- *"What's the recipe for silicon etching?"*
- *"How do I prepare samples for lithography?"*
- *"What are the troubleshooting steps for failed depositions?"*

### Research Queries
- *"Find all protocols related to photoresist processing"*
- *"What equipment can handle 4-inch wafers?"*
- *"Show me all safety procedures for chemical handling"*

## 🔧 Configuration & Customization

The system is designed to be easily adaptable to other research facilities and wiki systems. Key configuration points include:

### Basic Configuration
- **URL patterns** in scraping modules for different wiki structures
- **Content type detection** for facility-specific equipment categorization
- **Embedding models** for domain-specific technical content
- **Search parameters** tuned for scientific and technical queries

### Cloud Database Configuration (Neon Tech)
- **Database Schema**: Customizable table structures for different content types
- **Vector Dimensions**: Configurable embedding dimensions (default: 1536 for OpenAI)
- **Connection Pooling**: Automated connection management for production workloads
- **Backup Strategy**: Neon Tech provides automatic backups and point-in-time recovery
- **Scaling**: Serverless architecture automatically scales based on usage patterns


## 🔍 Troubleshooting Guide

### Common Issues and Solutions

#### Table Extraction Issues
**Problem**: Tables not extracting properly from wiki pages
- **Cause**: Complex table structures or authentication required
- **Solution**: Check URL accessibility, verify table markup
- **Debug**: Examine individual table markdown output files

#### Mixed Content Search Problems
**Problem**: Poor results when searching across text and tables
- **Cause**: Different content types may have different embedding patterns
- **Solution**: Adjust search parameters or implement content type weighting
- **Debug**: Compare similarity scores between content types

#### Embedding Generation Failures
**Problem**: Some chunks fail to generate embeddings
- **Cause**: API rate limits, content too long, or special characters
- **Solution**: Implement retry logic, clean content, check token limits
- **Debug**: Examine failed chunks in detail

#### Cloud Database Issues
**Problem**: Database connection failures or slow query performance
- **Cause**: Network connectivity, API key issues, or database scaling limits
- **Solution**: Verify Neon Tech credentials, check connection string, monitor usage limits
- **Debug**: Test database connectivity separately, review Neon Tech dashboard metrics

#### Memory Issues with Large Datasets
**Problem**: System runs out of memory loading embeddings
- **Cause**: Too many embeddings loaded simultaneously in local processing
- **Solution**: Use cloud database setup with Neon Tech for distributed storage and processing
- **Debug**: Monitor memory usage and migrate to database-based operations for large datasets

## 🤝 Contributing

This project serves as both a practical tool for UCSB nanofab users and an educational resource for learning RAG implementation. Contributions are welcome, especially:

- Additional document processing formats
- Improved search algorithms for technical content
- Enhanced user interface components
- Integration with other research facility systems

## 📖 Acknowledgments & Citation

### Project Development

```
This UCSB RAG Chatbot System was developed with guidance and mentorship from Dr. Samantha Roberts (@srobertsphd), director of ASRC Nanofab, advancing AI-powered knowledge management for scientific research and nanofabrication facilities.
```
### Data Source Permission
```
We gratefully acknowledge Dr. Demis D. John, director of UCSB Nanofab, for granting permission to scrape and process the UCSB wiki pages for this educational and research project.
```

## Research Applications
```
This project demonstrates the potential for AI-powered knowledge management systems in specialized research environments, making complex technical documentation more accessible through intelligent search and contextual response generation.
```
---

**Happy Learning and Research! 🎉**

This modular RAG system demonstrates how modern AI can make complex technical knowledge from the [UCSB wiki pages](https://wiki.nanofab.ucsb.edu/wiki/Special:AllPages) more accessible through intelligent search and contextual response generation. Perfect for understanding both the technical implementation and practical applications of retrieval-augmented generation systems in research environments.