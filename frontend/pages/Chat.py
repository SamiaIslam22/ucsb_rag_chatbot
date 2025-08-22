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

def init_theme():
    """Initialize theme in session state if not exists"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

def toggle_theme():
    """Toggle between dark and light mode"""
    st.session_state.dark_mode = not st.session_state.dark_mode

def load_data():
    """Load the embedded data"""
    try:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_dir = os.path.dirname(current_dir)
        project_root = os.path.dirname(frontend_dir)
        embeddings_path = os.path.join(project_root, "csv_dataframes", "embeddings", "chunked_pages_with_embeddings.csv")
        
        if not os.path.exists(embeddings_path):
            alt_paths = [
                "csv_dataframes/embeddings/chunked_pages_with_embeddings.csv",
                "../csv_dataframes/embeddings/chunked_pages_with_embeddings.csv",
                "../../csv_dataframes/embeddings/chunked_pages_with_embeddings.csv"
            ]
            
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
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
            df_with_embeddings['content_type'] = 'text'
            
            for idx, row in df_with_embeddings.iterrows():
                title = str(row.get('title', '')).lower()
                content = str(row.get('content', ''))
                
                if 'table' in title and 'row' in title:
                    df_with_embeddings.at[idx, 'content_type'] = 'table_row'
                elif 'table' in title:
                    df_with_embeddings.at[idx, 'content_type'] = 'table'
                elif content.startswith('{') and content.endswith('}'):
                    df_with_embeddings.at[idx, 'content_type'] = 'table_row'
        
        return df_with_embeddings
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def display_sources(sources):
    """Display sources with proper formatting based on content type"""
    for i, source in enumerate(sources, 1):
        if isinstance(source, dict):
            content_type = source.get('content_type', 'text')
            title = source.get('title', 'Unknown')
            url = source.get('url', '')
            content = source.get('content', 'No content available')
            score = source.get('score', 0.0)
        else:
            continue
        
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
        
        # Display in expander
        with st.expander(f"{icon} Source {i}: {title} ({display_type}, Score: {score:.3f})"):
            if url:
                st.markdown(f"**🔗 Source:** [{url}]({url})")
            
            # Display content based on type
            if content_type == 'table_row':
                st.markdown("**📊 Table Row Data:**")
                try:
                    if content and content != 'No content available' and str(content).strip():
                        if str(content).startswith('{') and str(content).endswith('}'):
                            table_data = json.loads(content)
                            for key, value in table_data.items():
                                if key not in ['url', 'title', 'chunk_number', 'character_count', 'total_chunks']:
                                    clean_key = str(key).replace('_', ' ').title()
                                    if value is not None and str(value).strip():
                                        st.markdown(f"**{clean_key}:** {value}")
                        else:
                            st.markdown(str(content))
                    else:
                        st.markdown("No content available")
                except json.JSONDecodeError:
                    st.markdown(str(content))
                    
            elif content_type == 'table':
                st.markdown("**📋 Complete Table:**")
                if content and content != 'No content available' and str(content).strip():
                    st.code(content, language='markdown')
                else:
                    st.markdown("No content available")
                
            elif content_type == 'text':
                st.markdown("**📄 Text Content:**")
                if content and content != 'No content available' and str(content).strip():
                    content_str = str(content)
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
        chunk_data = {
            'url': chunk.get('url', ''),
            'title': chunk.get('title', ''),
            'content': chunk.get('content', ''),
            'chunk_number': chunk.get('chunk', 1),
            'content_type': chunk.get('content_type', 'text'),
            'metadata': chunk.get('metadata', {})
        }
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
    
    # Initialize theme
    init_theme()
    
    # Theme toggle in top right
    col1, col2, col3 = st.columns([8, 1, 1])
    with col3:
        if st.session_state.dark_mode:
            if st.button("🌞", key="theme_toggle", help="Switch to light mode", use_container_width=True):
                toggle_theme()
                st.rerun()
        else:
            if st.button("🌙", key="theme_toggle", help="Switch to dark mode", use_container_width=True):
                toggle_theme()
                st.rerun()
    
    # Apply theme-based CSS
    if st.session_state.dark_mode:
        # Dark mode CSS
        st.markdown("""
        <style>
            /* Dark mode background */
            .stApp {
                background-color: #1a1a1a;
            }
            
            /* Main header styling - dark */
            .main-header {
                background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 2rem;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 2rem;
            }
            
            /* Sidebar background gradient - dark */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
            }
            
            /* Sidebar text color */
            [data-testid="stSidebar"] * {
                color: white;
            }
            
            /* Navigation font size */
            [data-testid="stSidebar"] a {
                font-size: 32px !important;
                font-weight: 700 !important;
                padding: 1rem 1.5rem !important;
                margin: 0.5rem 0 !important;
            }
            
            [data-testid="stSidebar"] a:hover {
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                transform: translateX(5px);
            }
            
            /* Search tips boxes - dark */
            .search-tip {
                background: rgba(255,255,255,0.05);
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                border-left: 4px solid rgba(255,255,255,0.3);
            }
            
            /* Sidebar button styling - dark */
            [data-testid="stSidebar"] .stButton > button {
                background: rgba(255,255,255,0.1);
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 20px;
                width: 100%;
            }
            
            [data-testid="stSidebar"] .stButton > button:hover {
                background: rgba(255,255,255,0.2);
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Light mode CSS (original)
        st.markdown("""
        <style>
            /* Main header styling */
            .main-header {
                background: linear-gradient(90deg, #FFE135 0%, #4A90E2 100%);
                color: white;
                padding: 2rem;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 2rem;
            }
            
            /* Sidebar background gradient */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #FFE135 0%, #4A90E2 100%);
            }
            
            /* Sidebar text color and size */
            [data-testid="stSidebar"] * {
                color: white;
            }
            
            /* HUGE navigation font size */
            [data-testid="stSidebar"] a {
                font-size: 32px !important;
                font-weight: 700 !important;
                padding: 1rem 1.5rem !important;
                margin: 0.5rem 0 !important;
            }
            
            [data-testid="stSidebar"] a:hover {
                background: rgba(255,255,255,0.2);
                border-radius: 10px;
                transform: translateX(5px);
            }
            
            /* Search tips boxes */
            .search-tip {
                background: rgba(255,255,255,0.1);
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                border-left: 4px solid rgba(255,255,255,0.5);
            }
            
            /* Sidebar button styling */
            [data-testid="stSidebar"] .stButton > button {
                background: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 20px;
                width: 100%;
            }
            
            [data-testid="stSidebar"] .stButton > button:hover {
                background: rgba(255,255,255,0.3);
            }
        </style>
        """, unsafe_allow_html=True)
    
    # Header with styled div
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
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base..."):
                try:
                    retrieved_chunks = vector_similarity_search(prompt, df, client, k=5)
                    
                    if retrieved_chunks:
                        converted_chunks = convert_chunks_for_openai_service(retrieved_chunks)
                        
                        try:
                            result = generate_response_with_context(prompt, converted_chunks, client)
                            
                            if isinstance(result, tuple) and len(result) == 2:
                                response, openai_sources = result
                                sources = retrieved_chunks
                            else:
                                response = result
                                sources = retrieved_chunks
                                
                        except Exception as e:
                            st.error(f"Error generating response: {e}")
                            response = "Sorry, I encountered an error generating a response."
                            sources = retrieved_chunks
                        
                        st.markdown(response)
                        
                        with st.expander("📚 Sources"):
                            display_sources(sources)
                        
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
    
    # Sidebar with styled tips
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
        
        if st.button("🗑️ Clear Chat History", key="clear_chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()