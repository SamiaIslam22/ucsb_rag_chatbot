import streamlit as st
import pandas as pd
import json
import sys
import os
import re

# Add the parent directory to sys.path to import backend modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.append(grandparent_dir)

# Now import from the correct backend modules
from backend.ai_services.vector_search import vector_similarity_search, client
from backend.ai_services.openai_services import generate_response_with_context

def ultra_aggressive_title_cleaning(title):
    """Ultra-aggressive title cleaning to remove all key artifacts and formatting issues"""
    if pd.isna(title) or title is None:
        return "Unknown Page"
    
    clean_title = str(title)
    
    # Remove ALL key-related artifacts (most aggressive patterns first)
    patterns_to_remove = [
        r'key[🔓🔒🔑].*?-',              # key + emoji + anything + dash
        r'key\w*[🔓🔒🔑].*?-',           # key + word + emoji + anything + dash
        r'key\w+-\w*-?',                 # key + word + dash + word + optional dash
        r'key\w*-.*?-',                  # key + anything + dash + anything + dash
        r'^[a-zA-Z]*[🔓🔒🔑].*?-',       # start + any letters + emoji + anything + dash
        r'^[🔓🔒🔑].*?-',                # start + emoji + anything + dash
        r'[🔓🔒🔑].*?-',                 # any emoji + anything + dash
        r'^key.*?-',                     # start + key + anything + dash
        r'key\w*',                       # any remaining "key" + letters
        r'^[a-zA-Z]{1,4}[🔓🔒🔑]',       # short letters + emoji at start
        r'^\w{1,6}_.*?_',                # short word + underscore + anything + underscore at start
    ]
    
    # Apply all removal patterns
    for pattern in patterns_to_remove:
        clean_title = re.sub(pattern, '', clean_title, flags=re.IGNORECASE)
    
    # Clean up formatting artifacts
    clean_title = clean_title.replace('_', ' ')
    clean_title = clean_title.replace('-', ' ')
    clean_title = clean_title.replace('  ', ' ')  # double spaces
    clean_title = re.sub(r'\s+', ' ', clean_title)  # multiple spaces to single
    clean_title = clean_title.strip()
    
    # Remove any remaining special characters at the start
    clean_title = re.sub(r'^[^a-zA-Z0-9]+', '', clean_title)
    
    # If title is still empty, too short, or contains artifacts
    if not clean_title or len(clean_title) < 3 or any(bad in clean_title.lower() for bad in ['key', '🔓', '🔒', '🔑']):
        return "Wiki Page Content"
    
    # Capitalize first letter of each word for better presentation
    clean_title = ' '.join(word.capitalize() for word in clean_title.split())
    
    # Limit length
    if len(clean_title) > 60:
        clean_title = clean_title[:60] + "..."
    
    return clean_title

def extract_title_from_url(url):
    """Extract a clean title from URL as fallback"""
    if not url:
        return "Unknown Source"
    
    try:
        # Get the last part of the URL
        url_parts = url.split('/')
        page_name = url_parts[-1]
        
        # Clean URL encoding
        page_name = page_name.replace('%20', ' ').replace('_', ' ')
        
        # Remove common URL artifacts
        page_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', page_name)
        page_name = re.sub(r'\s+', ' ', page_name).strip()
        
        # Capitalize words
        if page_name:
            page_name = ' '.join(word.capitalize() for word in page_name.split())
            return page_name
        else:
            return "Wiki Page"
    except:
        return "Wiki Content"

def clean_dataframe_titles(df):
    """Clean all titles in the dataframe at source"""
    if 'title' not in df.columns:
        return df
    
    df = df.copy()
    
    # Apply ultra-aggressive cleaning
    df['title'] = df['title'].apply(ultra_aggressive_title_cleaning)
    
    # For titles that are still problematic, use URL extraction
    for idx, row in df.iterrows():
        if (not row['title'] or 
            len(row['title']) < 3 or 
            row['title'] == "Wiki Page Content" or
            any(bad in str(row['title']).lower() for bad in ['key', 'unknown'])):
            
            # Try to extract from URL
            if 'url' in row and pd.notna(row['url']):
                df.at[idx, 'title'] = extract_title_from_url(row['url'])
            else:
                df.at[idx, 'title'] = f"Content Item {idx + 1}"
    
    return df

def load_data():
    """Load the embedded data"""
    try:
        # Get the project root directory (go up from pages to frontend to project root)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_dir = os.path.dirname(current_dir)
        project_root = os.path.dirname(frontend_dir)
        embeddings_path = os.path.join(project_root, "csv_dataframes", "embeddings", "chunked_pages_with_embeddings.csv")
        
        # Check if file exists
        if not os.path.exists(embeddings_path):
            st.error(f"File not found at: {embeddings_path}")
            st.error(f"Current working directory: {os.getcwd()}")
            st.error(f"Project root: {project_root}")
            
            # Try alternative paths
            alt_paths = [
                "csv_dataframes/embeddings/chunked_pages_with_embeddings.csv",
                "../csv_dataframes/embeddings/chunked_pages_with_embeddings.csv",
                "../../csv_dataframes/embeddings/chunked_pages_with_embeddings.csv"
            ]
            
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    st.info(f"Found file at alternative path: {alt_path}")
                    embeddings_path = alt_path
                    break
            else:
                return None
            
        df = pd.read_csv(embeddings_path)
        
        # Convert JSON string embeddings back to lists
        df['embedding_vectors'] = df['vectors'].apply(
            lambda x: json.loads(x) if pd.notna(x) and x != 'None' else None
        )
        
        # Filter out rows without embeddings
        df_with_embeddings = df[df['embedding_vectors'].notna()].copy()
        
        # Ensure content_type column exists
        if 'content_type' not in df_with_embeddings.columns:
            df_with_embeddings['content_type'] = 'text'  # Default to text
            
            # Try to infer content types
            for idx, row in df_with_embeddings.iterrows():
                title = str(row.get('title', '')).lower()
                content = str(row.get('content', ''))
                
                if 'table' in title and 'row' in title:
                    df_with_embeddings.at[idx, 'content_type'] = 'table_row'
                elif 'table' in title:
                    df_with_embeddings.at[idx, 'content_type'] = 'table'
                elif content.startswith('{') and content.endswith('}'):
                    df_with_embeddings.at[idx, 'content_type'] = 'table_row'
        
        # CLEAN TITLES AT SOURCE - This is the key fix!
        df_with_embeddings = clean_dataframe_titles(df_with_embeddings)
        
        return df_with_embeddings
    except FileNotFoundError:
        st.error("Embeddings file not found! Please run the main pipeline first.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def display_sources(sources):
    """Display sources with proper formatting based on content type"""
    for i, source in enumerate(sources, 1):
        # Handle both dictionary and tuple formats
        if isinstance(source, tuple) and len(source) == 2:
            score, chunk_data = source
            content_type = chunk_data.get('content_type', 'text')
            title = chunk_data.get('title', 'Unknown')
            url = chunk_data.get('url', '')
            content = chunk_data.get('content', 'No content available')
        else:
            content_type = source.get('content_type', 'text')
            title = source.get('title', 'Unknown')
            url = source.get('url', '')
            content = source.get('content', 'No content available')
            score = source.get('score', 0.0)
        
        # ENHANCED TITLE CLEANING - Additional safety net
        clean_title = ultra_aggressive_title_cleaning(title)
        
        # If title is still problematic, extract from URL
        if (clean_title == "Wiki Page Content" or 
            len(clean_title) < 3 or 
            any(bad in clean_title.lower() for bad in ['key', 'unknown'])):
            clean_title = extract_title_from_url(url)
        
        # Set icon and display type based on content type
        if content_type == 'table_row':
            icon = '📊'
            display_type = 'Table Row'
        elif content_type == 'table':
            icon = '📋'
            display_type = 'Complete Table'
        elif content_type == 'text':
            icon = '📄'
            display_type = 'Text Content'
        else:
            icon = '📝'
            display_type = 'Content'
        
        # Clean source title display
        with st.expander(f"{icon} Source {i}: {clean_title} ({display_type}, Score: {score:.3f})"):
            # Show the URL as a clickable link
            if url:
                st.markdown(f"**🔗 Source:** [{url}]({url})")
            
            # Display content based on type
            if content_type == 'table_row':
                st.markdown("**📊 Table Row Data:**")
                try:
                    # Try to parse as JSON for table row data
                    if content and content != 'No content available' and str(content).strip():
                        if str(content).startswith('{') and str(content).endswith('}'):
                            table_data = json.loads(content)
                            # Create a formatted table display with all data
                            for key, value in table_data.items():
                                # Clean up key names for better display
                                clean_key = str(key).replace('_', ' ').title()
                                # Show all key-value pairs, even if empty
                                if value is not None and str(value).strip():
                                    st.markdown(f"**{clean_key}:** {value}")
                                else:
                                    st.markdown(f"**{clean_key}:** *(empty)*")
                        else:
                            st.markdown(str(content))
                    else:
                        st.markdown("No content available")
                except json.JSONDecodeError:
                    # Fallback to raw content
                    st.markdown(str(content))
                    
            elif content_type == 'table':
                st.markdown("**📋 Complete Table:**")
                if content and content != 'No content available' and str(content).strip():
                    # Better table formatting
                    content_str = str(content)
                    
                    # Clean up the table content
                    lines = content_str.split('\n')
                    cleaned_lines = []
                    
                    for line in lines:
                        # Skip lines that are just dashes (table separators)
                        if line.strip() and not line.strip().replace('|', '').replace('-', '').replace(' ', ''):
                            continue
                        # Skip lines with [LINEBREAK] markers
                        if '[LINEBREAK]' in line:
                            continue
                        # Keep non-empty lines
                        if line.strip():
                            cleaned_lines.append(line)
                    
                    cleaned_content = '\n'.join(cleaned_lines)
                    
                    # Display as a formatted code block for better readability
                    if cleaned_content.strip():
                        st.code(cleaned_content, language='markdown')
                    else:
                        st.markdown("No content available")
                else:
                    st.markdown("No content available")
                
            elif content_type == 'text':
                st.markdown("**📄 Text Content:**")
                if content and content != 'No content available' and str(content).strip():
                    content_str = str(content)
                    # Limit text display to avoid overwhelming - but show more
                    if len(content_str) > 500:
                        st.markdown(content_str[:500] + "...")
                        with st.expander("Show full content"):
                            st.markdown(content_str)
                    else:
                        st.markdown(content_str)
                else:
                    st.markdown("No content available")
                
            else:
                st.markdown("**📝 Content:**")
                if content and content != 'No content available' and str(content).strip():
                    st.markdown(str(content))
                else:
                    st.markdown("No content available")

def convert_chunks_for_openai_service(retrieved_chunks):
    """Convert our new format back to the format expected by openai_services.py"""
    converted_chunks = []
    for chunk in retrieved_chunks:
        # Convert back to the tuple format (similarity_score, chunk_data)
        chunk_data = {
            'url': chunk.get('url', ''),
            'title': chunk.get('title', ''),
            'content': chunk.get('content', ''),
            'chunk_number': chunk.get('chunk', 1),
            'content_type': chunk.get('content_type', 'text'),
            'metadata': chunk.get('metadata', {})
        }
        
        # Create tuple in the format (similarity_score, chunk_data)
        converted_chunk = (chunk.get('score', 0.0), chunk_data)
        converted_chunks.append(converted_chunk)
    
    return converted_chunks

def main():
    st.set_page_config(
        page_title="Search - UCSB Nanofab",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling including sidebar
    st.markdown("""
    <style>
        /* Hide the ugly keyboard arrow */
        [data-testid="collapsedControl"],
        button[title="Close sidebar"],
        button[title="Open sidebar"],
        .css-1rs6os.edgvbvh3,
        .css-1vq4p4l.e1fqkh3o0 {
            display: none !important;
        }
        
        /* Custom clean arrow toggle */
        .stApp::before {
            content: "›";
            position: fixed;
            top: 1rem;
            left: 1rem;
            z-index: 999;
            font-size: 1.8rem;
            color: #666;
            font-weight: 300;
            cursor: pointer;
            padding: 0.3rem 0.5rem;
            background: rgba(255,255,255,0.9);
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            transition: all 0.2s ease;
            font-family: system-ui, -apple-system, sans-serif;
        }
        
        .stApp::before:hover {
            color: #333;
            background: white;
            border-color: #ccc;
        }
        
        /* GLOBAL FONT FAMILY - Apply Calibri to EVERYTHING */
        *, *::before, *::after {
            font-family: 'Calibri', 'Segoe UI', 'Arial', sans-serif !important;
        }
        
        /* Apply to all HTML elements */
        html, body, div, span, applet, object, iframe,
        h1, h2, h3, h4, h5, h6, p, blockquote, pre,
        a, abbr, acronym, address, big, cite, code,
        del, dfn, em, img, ins, kbd, q, s, samp,
        small, strike, strong, sub, sup, tt, var,
        b, u, i, center,
        dl, dt, dd, ol, ul, li,
        fieldset, form, label, legend,
        table, caption, tbody, tfoot, thead, tr, th, td,
        article, aside, canvas, details, embed, 
        figure, figcaption, footer, header, hgroup, 
        menu, nav, output, ruby, section, summary,
        time, mark, audio, video,
        button, input, select, textarea {
            font-family: 'Calibri', 'Segoe UI', 'Arial', sans-serif !important;
        }
        
        /* Specifically target Streamlit components */
        .stApp, .stApp * {
            font-family: 'Calibri', 'Segoe UI', 'Arial', sans-serif !important;
        }
        
        /* Target sidebar specifically */
        [data-testid="stSidebar"], [data-testid="stSidebar"] * {
            font-family: 'Calibri', 'Segoe UI', 'Arial', sans-serif !important;
        }
        
        /* Target main content */
        .main, .main * {
            font-family: 'Calibri', 'Segoe UI', 'Arial', sans-serif !important;
        }
        
        /* Target chat interface */
        .stChatMessage, .stChatMessage * {
            font-family: 'Calibri', 'Segoe UI', 'Arial', sans-serif !important;
        }
        
        /* Target chat input */
        .stChatInput, .stChatInput * {
            font-family: 'Calibri', 'Segoe UI', 'Arial', sans-serif !important;
        }
        
        /* CONSISTENT NAVIGATION SIDEBAR STYLING - Same as Home page */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #FFE135 0%, #4A90E2 100%) !important;
        }
        
        [data-testid="stSidebar"] * {
            font-size: 22px !important;
            font-weight: bold !important;
            color: white !important;
        }
        
        /* Target navigation links specifically */
        [data-testid="stSidebar"] a,
        [data-testid="stSidebar"] div[role="button"],
        [data-testid="stSidebar"] .css-1vq4p4l {
            font-size: 24px !important;
            font-weight: 700 !important;
            color: white !important;
            padding: 1rem 1.5rem !important;
            margin: 0.5rem 0 !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
        }
        
        /* Navigation hover effects */
        [data-testid="stSidebar"] a:hover,
        [data-testid="stSidebar"] div[role="button"]:hover {
            background: rgba(255,255,255,0.2) !important;
            transform: translateX(8px) !important;
        }
        
        /* Even more nuclear approach for navigation */
        .stSidebar * {
            font-size: 24px !important;
            font-weight: bold !important;
        }
        
        /* SEARCH PAGE SPECIFIC SIDEBAR CONTENT STYLING */
        /* Override font size for sidebar content (not navigation) */
        [data-testid="stSidebar"] .search-tip,
        [data-testid="stSidebar"] .search-tip *,
        [data-testid="stSidebar"] .markdown-text-container,
        [data-testid="stSidebar"] .markdown-text-container * {
            font-size: 14px !important;
            font-weight: normal !important;
        }
        
        /* Sidebar section headers should be slightly larger */
        [data-testid="stSidebar"] .search-tip h2,
        [data-testid="stSidebar"] .search-tip h4 {
            font-size: 16px !important;
            font-weight: bold !important;
        }
        
        /* Style sidebar headers */
        .sidebar h2 {
            color: white !important;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 0.5rem;
        }
        
        /* Style sidebar text */
        .sidebar .markdown-text-container {
            color: white !important;
        }
        
        /* Style sidebar button */
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,0.2) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.3) !important;
            border-radius: 20px !important;
            width: 100% !important;
            font-weight: bold !important;
            font-size: 16px !important;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.3) !important;
            border-color: white !important;
        }
        
        /* Search tips styling */
        .search-tip {
            background: rgba(255,255,255,0.1);
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid rgba(255,255,255,0.5);
        }
        
        /* Main content area */
        .main-header {
            background: linear-gradient(90deg, #FFE135 0%, #4A90E2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* Chat input styling */
        .stChatInput {
            border-radius: 25px;
        }
        
        /* Source expander styling */
        .streamlit-expanderHeader {
            background: #f8f9fa;
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with styling
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Search UCSB Nanofab Knowledge</h1>
        <p>Ask questions about nanofabrication processes, equipment, and procedures!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading knowledge base..."):
        df = load_data()
    
    if df is None:
        st.error("⚠️ Could not load the knowledge base. Please ensure the data files are available.")
        st.stop()
    
    st.success(f"✅ Knowledge base loaded with {len(df)} chunks!")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📚 Sources"):
                    display_sources(message["sources"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about nanofabrication..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base..."):
                try:
                    # Search for relevant chunks
                    retrieved_chunks = vector_similarity_search(prompt, df, client, k=5)
                    
                    if retrieved_chunks:
                        # Convert chunks to format expected by openai_services
                        converted_chunks = convert_chunks_for_openai_service(retrieved_chunks)
                        
                        # Generate response - FIXED: Handle the return value properly
                        try:
                            result = generate_response_with_context(prompt, converted_chunks, client)
                            
                            # Check if it returns a tuple or just a string
                            if isinstance(result, tuple) and len(result) == 2:
                                response, openai_sources = result
                                # Use our original retrieved_chunks for display since they have the right format
                                sources = retrieved_chunks
                            else:
                                # If it just returns a response string, create sources from our chunks
                                response = result
                                sources = retrieved_chunks
                                
                        except Exception as e:
                            st.error(f"Error generating response: {e}")
                            response = "Sorry, I encountered an error generating a response."
                            sources = retrieved_chunks
                        
                        st.markdown(response)
                        
                        # Show sources with enhanced display
                        with st.expander("📚 Sources"):
                            display_sources(sources)
                        
                        # Add assistant message
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response,
                            "sources": sources
                        })
                    else:
                        error_msg = "I couldn't find relevant information to answer your question."
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        
                except Exception as e:
                    st.error(f"Error in search or response generation: {e}")
                    error_msg = "Sorry, I encountered an error processing your question."
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown("""
        <div class="search-tip">
            <h2>🔍 Search Tips</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="search-tip">
            <h4>🎯 Try asking about:</h4>
            <ul>
                <li>Equipment specifications</li>
                <li>Process procedures</li>
                <li>Safety protocols</li>
                <li>Troubleshooting steps</li>
                <li>Material properties</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="search-tip">
            <h4>💡 Example questions:</h4>
            <ul>
                <li>"What are the specifications for the Oxford RIE?"</li>
                <li>"How do I clean the SEM sample holder?"</li>
                <li>"What safety procedures are required for the furnace?"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Chat History", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()