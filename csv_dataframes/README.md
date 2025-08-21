# 🌐 Extraction Module
### UCSB Wiki Content Extraction Pipeline

This module handles the complete extraction of content from [UCSB Nanofab Wiki pages](https://wiki.nanofab.ucsb.edu/wiki/Special:AllPages), processing text, tables, and images into structured CSV datasets for the RAG pipeline.

## 📁 Module Structure

```
extraction/
├── __pycache__/                    # Python cache files
├── __init__.py                     # Package initialization
├── wiki_texts.py                   # 📝 Text content extraction
├── wiki_table.py                   # 📊 Table extraction and markdown conversion
├── wiki_images.py                  # 🖼️ Image analysis with AI descriptions
└── README.md                       # 📖 This documentation
```

## 🚀 Execution Order

Run the extraction modules in this sequence:

1. **wiki_texts.py** - Extract text content from wiki pages
2. **wiki_table.py** - Extract and process tables into markdown
3. **wiki_images.py** - Extract and analyze images with AI

## 📄 Module Descriptions

### 1. **wiki_texts.py** - Text Content Extraction

**Purpose**: Scrapes textual content from UCSB wiki pages using advanced web crawling

**Key Functions**:
```python
def extract_title_from_url(url)           # Converts URLs to clean page titles
async def scrape(url)                     # Scrapes individual wiki page
async def run_all_scrapes(urls)           # Processes multiple URLs efficiently
```

**What it extracts**:
- Main content area (`div#mw-content-text`)
- Page titles from URLs
- Clean markdown-formatted text
- Procedure descriptions and equipment documentation

**Configuration**:
- Uses Crawl4AI with CSS selectors for precise content targeting
- Excludes navigation, footer, external links, and social media
- Bypasses cache for fresh content extraction
- Handles errors gracefully and continues processing

**Output**: `csv_dataframes/raw/wiki_texts.csv`

---

### 2. **wiki_table.py** - Table Extraction Engine

**Purpose**: Extracts equipment tables and protocol data using Docling's advanced table processing

**Key Functions**:
```python
def table_to_markdown(table)              # Converts tables to clean markdown
def ultra_clean_text_for_csv(text_content) # Cleans and normalizes content
def get_page_name_from_url(url)           # Extracts page names from URLs
```

**What it extracts**:
- Equipment specification tables
- Process parameter tables
- Protocol data tables
- Chemical inventory lists
- Staff directory information

**Processing Pipeline**:
1. **URL Processing**: Fetches content from UCSB nanofab wiki URLs
2. **Table Detection**: Uses Docling's DocumentConverter to identify tables
3. **Content Conversion**: Converts complex table structures to clean markdown
4. **Individual Storage**: Saves each table as separate `.md` file in `csv_dataframes/raw/scratch/`
5. **Data Cleaning**: Removes special characters, normalizes spacing
6. **Metadata Addition**: Adds source tracking and categorization

**Output**: 
- `csv_dataframes/raw/wiki_tables.csv` (aggregated table data)
- `csv_dataframes/raw/scratch/*.md` (individual table markdown files)

---

### 3. **wiki_images.py** - AI-Powered Image Analysis

**Purpose**: Extracts, analyzes, and catalogs images with AI-generated descriptions

**Key Functions**:
```python
def normalize_mediawiki_image_url(url)    # Converts thumbnails to original images
async def download_image_as_data_url(url, client_http) # Downloads and encodes images
def summarize_image_with_context(data_url, context_text, alt, caption) # AI analysis
async def main()                          # Main orchestrator
```

**What it extracts**:
- Equipment photos and diagrams
- Process flow images
- Safety procedure visuals
- Facility layout images
- Technical schematics

**AI Analysis Features**:
- Uses OpenAI's gpt-4o-mini vision model
- Incorporates page context for better understanding
- Processes alt text and captions
- Generates detailed technical descriptions
- Filters out UI elements and logos

**Image Processing Pipeline**:
1. **Integration**: Uses `wiki_texts.py` output for page context
2. **Discovery**: Identifies all images on wiki pages
3. **Normalization**: Converts MediaWiki thumbnails to original URLs
4. **Download**: Fetches and converts images to base64 data URLs
5. **AI Analysis**: Generates context-aware descriptions
6. **Deduplication**: Removes duplicate images across pages

**Output**: `csv_dataframes/raw/wiki_images.csv`

## 📊 CSV Output Specifications

### **wiki_texts.csv**
Contains extracted text content from UCSB wiki pages.

| Column | Description | Example |
|--------|-------------|---------|
| `title` | Clean page title | "ICP Etch 1 Panasonic E646V" |
| `url` | Source wiki URL | "https://wiki.nanofab.ucsb.edu/wiki/ICP_Etch_1..." |
| `markdown` | Extracted content in markdown format | "# Equipment Overview\nThe Panasonic..." |

**Content Types**:
- Equipment operation procedures
- Safety protocols and guidelines
- Process recipes and parameters
- Troubleshooting guides
- Facility policies and procedures

---

### **wiki_tables.csv**
Contains structured table data from equipment and protocol pages.

| Column | Description | Example |
|--------|-------------|---------|
| `page_name` | Source page identifier | "Dry_Etching_Recipes" |
| `page_url` | Full source URL | "https://wiki.nanofab.ucsb.edu/wiki/Dry_Etching_Recipes" |
| `has_tables` | Table presence indicator | "yes" / "no" / "error" |
| `table_count` | Number of tables found | 3 |
| `table_1_content` | First table in markdown | "\| Parameter \| Value \|..." |
| `table_2_content` | Second table in markdown | "\| Chemical \| Concentration \|..." |
| `table_3_content` | Third table in markdown | "\| Step \| Time \| Temperature \|..." |

**Table Types Extracted**:
- **Equipment Specifications**: Power, temperature, pressure parameters
- **Process Recipes**: Step-by-step protocols with timing and conditions
- **Chemical Lists**: Inventory with concentrations and safety data
- **Staff Directories**: Contact information and expertise areas
- **Publication Lists**: Research papers and documentation references

**Individual Markdown Files** (`csv_dataframes/raw/scratch/`):
- `Dry_Etching_Recipes_table_1.md` - Equipment recipe tables
- `Lithography_Recipes_table_1-5.md` - Lithography process protocols
- `Staff_List_table_1-4.md` - Staff directory and contact information
- `Ovens_Overview_table_1.md` - Oven specifications and procedures
- `Stocked_Chemical_List_table_1.md` - Chemical inventory data

---

### **wiki_images.csv**
Contains image metadata with AI-generated descriptions.

| Column | Description | Example |
|--------|-------------|---------|
| `index` | Sequential identifier | 1, 2, 3... |
| `page_url` | Source wiki page | "https://wiki.nanofab.ucsb.edu/wiki/SEM_Training" |
| `image_url` | Direct image URL | "https://wiki.nanofab.ucsb.edu/w/images/..." |
| `title` | Page title context | "SEM Training and Operation" |
| `alt` | Image alt text | "SEM control panel overview" |
| `caption` | Image caption | "Main control interface showing..." |
| `summary` | AI-generated description | "This image shows the scanning electron microscope control panel with various knobs and displays for adjusting beam parameters..." |

**Image Categories**:
- **Equipment Photos**: Front panels, internal components, sample holders
- **Process Diagrams**: Flow charts, schematic drawings, layout plans
- **Safety Images**: Warning signs, protective equipment, emergency procedures
- **Result Images**: Sample outputs, measurement data, quality examples
- **Training Materials**: Step-by-step visual guides, before/after comparisons

## 🔧 Configuration & Customization

### **URL Lists**
Each module contains predefined lists of UCSB wiki URLs:
```python
wiki_links = [
    "https://wiki.nanofab.ucsb.edu/wiki/Wet_Benches#HF.2FTMAH_Processing_Bench",
    "https://wiki.nanofab.ucsb.edu/wiki/Autostep_200_Mask_Making_Guidance",
    # ... additional URLs
]
```

### **Content Filtering**
- **Text Extraction**: Targets `div#mw-content-text` for main content
- **Table Detection**: Uses Docling's AI models for accurate table identification
- **Image Filtering**: Removes UI elements, logos, and decorative images

### **API Requirements**
```env
OPENAI_API_KEY=your_openai_api_key_here  # Required for wiki_images.py
```

## 🚀 Usage Instructions

### **Individual Module Execution**

**Extract Text Content**:
```bash
cd backend/extraction/
python wiki_texts.py
```

**Extract Tables**:
```bash
python wiki_table.py
```

**Analyze Images**:
```bash
python wiki_images.py
```

### **Automated Execution**
Run all extraction modules through the main orchestrator:
```bash
cd backend/
python main.py
```

## 📈 Output Statistics

**Typical Extraction Results**:
- **Text Pages**: 10-15 comprehensive wiki pages
- **Table Data**: 20-30 structured tables with equipment and protocol data
- **Images**: 50-100 technical images with AI-generated descriptions
- **Processing Time**: 5-10 minutes for complete extraction pipeline

## 🔍 Quality Assurance

### **Data Validation**
- **Text Content**: Validates markdown formatting and content completeness
- **Table Structure**: Ensures proper table parsing and markdown conversion
- **Image Analysis**: Verifies AI description quality and context relevance

### **Error Handling**
- **Network Issues**: Graceful timeout and retry mechanisms
- **Content Parsing**: Continues processing even if individual pages fail
- **API Limits**: Rate limiting and error recovery for OpenAI calls

## 🔄 Integration with RAG Pipeline

The extracted CSV files serve as input for the next pipeline stages:

```
extraction/ outputs → chunking/ → ai_services/ → frontend/
     ↓                    ↓           ↓            ↓
Raw CSV files    →   Processed   →  Vector    →   User
(text, tables,        chunks        embeddings     interface
 images)
```

## 🤝 Contributing

When adding new extraction capabilities:

1. **Follow naming conventions**: `wiki_[content_type].py`
2. **Implement error handling**: Graceful failure recovery
3. **Add progress reporting**: User-friendly status updates
4. **Document CSV schema**: Clear column descriptions
5. **Test with sample URLs**: Verify extraction quality

---

**This extraction module transforms the UCSB Nanofab Wiki into a structured, searchable knowledge base ready for AI-powered question answering!** 🎯