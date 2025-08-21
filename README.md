# Modular RAG System with Table Integration
A comprehensive, educational implementation of a RAG pipeline that handles both all sorts of documents. Built with Streamlit, Docling, Crawl4AI, OpenAI, and semantic search to demonstrate modern knowledge management systems for nanofabrication facilities.

## 🎯 Overview
This project demonstrates how to build a complete RAG system that can intelligently search across all sorts of documents. Each module handles a specific aspect of the pipeline, making it easy to learn, modify, and extend for real-world applications.

### What is RAG?
RAG (Retrieval-Augmented Generation) is a technique that combines:
- **Retrieval**: Finding relevant information from a knowledge base
- **Generation**: Using that information to generate accurate, contextual responses

### System Architecture
Text Documents → Text Chunking → Embeddings ↘
                                            → Combined Knowledge Base → Vector Search → LLM Response
Table Data → Table Extraction → Embeddings ↗

## 📁 Project Structure
```
├── README.md                           # This comprehensive guide
├── app.py                             # 🌐 Streamlit web interface
├── chunking.py                        # 🔀 Text and table processing
├── embedding_generator.py             # 🧠 Vector embedding generation
├── vector_search.py                   # 🔍 Semantic similarity search
├── openai_services.py                 # 🤖 OpenAI API integration
├── main.py                            # 💬 Command-line interface
├── wiki_table.py                      # 📊 Table extraction from wikis
├── hybrid_search.py                   # 🔬 Experimental hybrid search
├── multi_page_scrape1.csv             # 📄 Input: scraped text documents
├── all_pages_tables_data.csv          # 📊 Input: extracted table data
├── chunked_pages.csv                  # 🔄 Processed: combined chunks
└── chunked_pages_with_embeddings.csv  # 🎯 Final: vectorized knowledge base
```

## 🧩 Module Architecture

### **1. `wiki_table.py` - Table Extraction Engine**
**Purpose:** Extract structured data from wiki pages using Docling's advanced table processing

```python
def table_to_markdown(table)
def ultra_clean_text_for_csv(text_content)
def get_page_name_from_url(url)
```

**What it does:**
- **Advanced Table Detection**: Uses Docling's DocumentConverter to identify and extract tables from web pages
- **Intelligent Cleaning**: Converts complex table structures to clean markdown format
- **Metadata Preservation**: Maintains source URLs, page names, and table numbering
- **Error Handling**: Gracefully handles pages without tables or conversion errors
- **CSV Generation**: Creates structured output for downstream processing

**Table Processing Pipeline:**
1. **URL Processing**: Fetches content from wiki URLs
2. **Table Detection**: Identifies table structures using AI models
3. **Content Extraction**: Converts tables to clean markdown format
4. **Data Cleaning**: Removes special characters, normalizes spacing
5. **Metadata Addition**: Adds source tracking and table numbering


---

### **2. `chunking.py` - Unified Content Processing**
**Purpose:** Intelligent processing of both text documents and table data into searchable chunks

```python
def process_text_content(input_df, text_splitter)
def process_table_content(tables_df)
def combine_chunks(text_chunks, table_chunks)
```

**What it does:**
- **Dual Processing Strategy**: Handles text and tables with different chunking approaches
- **Smart Text Splitting**: Uses LangChain's CharacterTextSplitter for semantic boundaries
- **Table Preservation**: Keeps complete tables as single chunks to maintain structure
- **Content Type Tracking**: Labels chunks as "text" or "table" for downstream processing
- **Unified Output**: Combines both content types into a single searchable dataset

**Chunking Strategies:**
- **Text Documents**: Split into 1000-character chunks with 2-character overlap
- **Table Data**: Each table becomes exactly one chunk (no splitting)
- **Metadata Preservation**: Maintains source URLs, titles, and chunk relationships

**Processing Flow:**
```python
# Text Processing
text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=1000,
    chunk_overlap=2
)

# Table Processing (no splitting)
table_chunk = {
    "content": complete_table_markdown,
    "content_type": "table",
    "chunk_number": 1,
    "total_chunks": 1
}
```

---

### **3. `embedding_generator.py` - Vector Embedding Pipeline**
**Purpose:** Convert all chunks (text and tables) into searchable vector representations

```python
def embed_chunks_with_openai(chunks_df, client)
def create_metadata_structure(row)
def handle_embedding_errors(chunk_data, error)
```

**What it does:**
- **Universal Embedding**: Creates vectors for both text and table content using the same model
- **Batch Processing**: Efficiently processes large datasets with rate limiting
- **Error Recovery**: Gracefully handles API failures and continues processing
- **Metadata Enrichment**: Preserves all chunk information in structured metadata
- **Progress Tracking**: Provides detailed progress information during processing

**Embedding Specifications:**
- **Model**: `text-embedding-3-small` (1536 dimensions)
- **Consistency**: Same model for all content types ensures comparable vectors
- **Rate Limiting**: 0.1-second delays between API calls to respect limits
- **Error Handling**: Continues processing even if individual chunks fail

**Metadata Structure:**
```python
metadata = {
    'url': chunk_source_url,
    'title': document_title,
    'chunk_number': position_in_document,
    'total_chunks': total_document_chunks,
    'character_count': chunk_length,
    'content_type': 'text' or 'table'
}
```


---

### **4. `vector_search.py` - Semantic Search Engine**
**Purpose:** Find relevant chunks using vector similarity across both text and table data

```python
def cosine_similarity_openai(query_vector, chunk_vectors)
def vector_similarity_search(query_text, df, client, k=5)
def embed_query(query_text, client)
```

**What it does:**
- **Unified Search**: Searches across both text and table content seamlessly
- **Optimized Similarity**: Leverages OpenAI's pre-normalized embeddings for efficiency
- **Ranking Intelligence**: Returns top-k most relevant chunks regardless of content type
- **Score Transparency**: Provides similarity scores for result analysis
- **Error Resilience**: Handles embedding failures gracefully

**Search Mathematics:**
```python
# Optimized for OpenAI embeddings (pre-normalized)
similarity = np.dot(chunk_vectors, query_vector)
# Equivalent to cosine similarity for normalized vectors
```

**Search Pipeline:**
1. **Query Embedding**: Convert user question to vector
2. **Similarity Calculation**: Compare against all chunk vectors
3. **Content-Agnostic Ranking**: Rank by relevance regardless of text/table
4. **Top-K Selection**: Return most relevant chunks with metadata


---

### **5. `openai_services.py` - LLM Response Generation**
**Purpose:** Generate contextual responses using retrieved chunks as supporting evidence

```python
def generate_response_with_context(user_prompt, retrieved_chunks, client)
def build_context_from_chunks(retrieved_chunks)
def create_source_metadata(retrieved_chunks)
```

**What it does:**
- **Context Assembly**: Combines retrieved text and table chunks into coherent context
- **Prompt Engineering**: Crafts effective prompts for RAG-based responses
- **Source Attribution**: Tracks which chunks contributed to the response
- **Mixed Content Handling**: Seamlessly works with both text and tabular information
- **Error Management**: Provides fallback responses for API failures

**Response Generation Flow:**
```python
# Context Construction
context_parts = []
for score, chunk_row in retrieved_chunks:
    context_parts.append(f"Source {i}:\n{chunk_row['content']}\n")

# Prompt Engineering
system_prompt = """Use the provided context to answer accurately.
Context may include both text passages and structured table data."""

# LLM Configuration
response = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0.1,  # Focused responses
    max_tokens=4000   # Comprehensive answers
)
```


---

### **6. `app.py` - Interactive Web Interface**
**Purpose:** Provide user-friendly access to the RAG system through Streamlit

```python
def load_chunked_data(csv_path)
def display_content_type_breakdown(df)
def handle_chat_interface()
def show_source_attribution(sources, df)
```

**What it does:**
- **Intuitive Interface**: Clean, modern web interface for non-technical users
- **Content Type Awareness**: Shows breakdown of text vs. table chunks in knowledge base
- **Real-time Search**: Interactive search with immediate results
- **Source Transparency**: Displays exactly which documents/tables informed each response
- **Session Management**: Maintains chat history and conversation context

**Interface Features:**
- **Smart Sidebar**: Knowledge base statistics and search configuration
- **Content Type Labels**: Shows whether responses come from text or tables
- **Similarity Scores**: Transparency into search quality and relevance
- **Source Links**: Direct access to original documents and tables
- **Chat History**: Persistent conversation with source tracking


---

### **7. `main.py` - Command-Line Orchestration**
**Purpose:** Demonstrate complete pipeline execution and testing

```python
def load_chunked_data_from_csv(csv_path)
def complete_rag_pipeline(query, df, client, k=5)
def run_test_queries(test_queries)
```

**What it does:**
- **Pipeline Demonstration**: Shows end-to-end RAG execution
- **Testing Framework**: Provides structured testing of system capabilities
- **Performance Monitoring**: Tracks search and response quality
- **Debug Information**: Detailed logging of search and retrieval process

**Educational Flow:**
```python
# Step 1: Load processed knowledge base
df = load_chunked_data_from_csv("chunked_pages_with_embeddings.csv")

# Step 2: Execute search pipeline
retrieved_chunks = vector_similarity_search(query, df, client, k)

# Step 3: Generate contextual response
response = generate_response_with_context(query, retrieved_chunks, client)

# Step 4: Display results and metrics
```

---

## 🔄 Complete Data Flow Architecture

```
📄 Text Documents (multi_page_scrape1.csv)     📊 Wiki Tables (URLs)
         ↓                                           ↓
📁 chunking.py: Text Processing              📊 wiki_table.py: Table Extraction
         ↓                                           ↓
📑 Text Chunks (1000 chars each)             📋 Table Chunks (complete tables)
         ↓                                           ↓
         ↘️                                         ↙️
           🔄 chunking.py: Combine Content Types
                        ↓
           📊 chunked_pages.csv (Mixed Content)
                        ↓
           🧠 embedding_generator.py: Vectorization
                        ↓
           🔢 chunked_pages_with_embeddings.csv
                        ↓
❓ User Query → 🧠 openai_services.py: Query Embedding
                        ↓
           🔍 vector_search.py: Similarity Search
                        ↓
           📋 Top-K Relevant Chunks (Text + Tables)
                        ↓
           💬 openai_services.py: Response Generation
                        ↓
           ✨ Final AI Response with Source Attribution
```

## 🚀 Getting Started

### Prerequisites
```bash
# Install core dependencies
pip install streamlit pandas numpy openai python-dotenv
pip install langchain-text-splitters docling crawl4AI

# Or if docling installation issues:
pip install git+https://github.com/DS4SD/docling.git
```

### Environment Setup
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Quick Start Guide

#### **Step 1: Extract Table Data**
```bash
python wiki_table.py
```
- Extracts tables from predefined wiki URLs
- Creates `all_pages_tables_data.csv`
- Processes 10+ wiki pages for table content

#### **Step 2: Process All Content**
```bash
python chunking.py
```
- Combines text documents and table data
- Creates unified chunk structure
- Outputs `chunked_pages.csv` with mixed content types

#### **Step 3: Generate Embeddings**
```bash
python embedding_generator.py
```
- Creates vector embeddings for all chunks
- Processes both text and table content
- Outputs `chunked_pages_with_embeddings.csv`

#### **Step 4: Launch Interface**
```bash
streamlit run app.py
```
- Opens web interface at `http://localhost:8501`
- Provides interactive search and chat
- Shows source attribution and content types

#### **Step 5: Test System**
```bash
python main.py
```
- Runs command-line testing
- Demonstrates pipeline execution
- Shows search quality metrics

## 📚 Educational Learning Path

### **Level 1: Understanding Mixed Content Processing**
1. **Start with `wiki_table.py`**
   - Learn table extraction from web content
   - Understand structured data processing
   - Practice content cleaning and normalization

2. **Explore `chunking.py`**
   - See how different content types require different strategies
   - Learn about preserving table structure vs. enabling search
   - Understand content type classification

### **Level 2: Vector Search and AI Integration**
3. **Study `embedding_generator.py`**
   - Learn how to vectorize mixed content types
   - Understand batch processing and error handling
   - Practice API integration patterns

4. **Examine `vector_search.py`**
   - Learn content-agnostic similarity search
   - Understand ranking across different data types
   - Practice efficient vector operations

### **Level 3: Response Generation and User Interface**
5. **Analyze `openai_services.py`**
   - Learn context assembly from mixed sources
   - Understand prompt engineering for RAG
   - Practice LLM integration and error handling

6. **Run `app.py`**
   - See modern AI interface design
   - Learn real-time data processing
   - Understand user experience for AI systems


## 🔍 Troubleshooting Guide

### **Common Issues and Solutions**

#### **Table Extraction Issues**
**Problem**: Tables not extracting properly from wiki pages
- **Cause**: Complex table structures or authentication required
- **Solution**: Check URL accessibility, verify table markup
- **Debug**: Examine individual table markdown output files

#### **Mixed Content Search Problems**
**Problem**: Poor results when searching across text and tables
- **Cause**: Different content types may have different embedding patterns
- **Solution**: Adjust search parameters or implement content type weighting
- **Debug**: Compare similarity scores between content types

#### **Embedding Generation Failures**
**Problem**: Some chunks fail to generate embeddings
- **Cause**: API rate limits, content too long, or special characters
- **Solution**: Implement retry logic, clean content, check token limits
- **Debug**: Examine failed chunks in detail

#### **Memory Issues with Large Datasets**
**Problem**: System runs out of memory loading embeddings
- **Cause**: Too many embeddings loaded simultaneously
- **Solution**: Implement lazy loading or use database storage
- **Debug**: Monitor memory usage during loading



**Happy Learning! 🎉**

*This modular RAG system demonstrates how modern AI can make complex technical knowledge more accessible through intelligent search and contextual response generation. Perfect for understanding both the technical implementation and practical applications of retrieval-augmented generation systems.*

**Dr. Samantha Roberts** ([@srobertsphd](https://github.com/srobertsphd))
**Developed with guidance from Dr. Samantha Roberts (@srobertsphd) - advancing AI-powered knowledge management for scientific research.**