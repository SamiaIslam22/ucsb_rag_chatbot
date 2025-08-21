import streamlit as st
import pandas as pd
import json
import sys
import os

# Add the parent directory to sys.path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from the correct backend modules
from backend.ai_services.vector_search import vector_similarity_search, client
from backend.ai_services.openai_services import generate_response_with_context

def load_data():
    """Load the embedded data"""
    try:
        # Get the project root directory (go up from frontend to project root)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
        content_type = source.get('content_type', 'text')
        
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
        
        with st.expander(f"{icon} {i}. {source['title']} - {display_type} (Score: {source['score']:.3f})"):
            # Show the URL as a clickable link
            st.markdown(f"**🔗 Source:** [{source['url']}]({source['url']})")
            st.markdown(f"**📍 Chunk:** {source['chunk']}")
            
            # Display content based on type
            if content_type == 'table_row':
                st.markdown("**📊 Table Row Data:**")
                try:
                    # Try to parse as JSON for table row data
                    if 'content' in source:
                        raw_content = source['content']
                        if raw_content.startswith('{') and raw_content.endswith('}'):
                            table_data = json.loads(raw_content)
                            # Create a nice table display
                            for key, value in table_data.items():
                                if value and str(value).strip():
                                    st.markdown(f"• **{key}**: {value}")
                        else:
                            st.markdown(raw_content)
                    else:
                        st.markdown("No content available")
                except:
                    # Fallback to raw content
                    st.markdown(source.get('content', 'No content available'))
                    
            elif content_type == 'table':
                st.markdown("**📋 Complete Table:**")
                raw_content = source.get('content', 'No content available')
                st.code(raw_content, language='markdown')
                
            elif content_type == 'text':
                st.markdown("**📄 Text Content:**")
                st.markdown(source.get('content', 'No content available'))
                
            else:
                st.markdown("**📝 Content:**")
                st.markdown(source.get('content', 'No content available'))

def main():
    st.set_page_config(
        page_title="UCSB Nanofab RAG Chatbot",
        page_icon="🔬",
        layout="wide"
    )
    
    st.title("🔬 UCSB Nanofab Knowledge Assistant")
    st.markdown("Ask questions about nanofabrication processes, equipment, and procedures!")
    
    # Load data
    with st.spinner("Loading knowledge base..."):
        df = load_data()
    
    if df is None:
        st.stop()
    
    st.success(f"Knowledge base loaded with {len(df)} chunks!")
    
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
                # Search for relevant chunks
                retrieved_chunks = vector_similarity_search(prompt, df, client, k=5)
                
                if retrieved_chunks:
                    # Generate response
                    response, sources = generate_response_with_context(prompt, retrieved_chunks, client)
                    
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
    
    # Sidebar with info
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This chatbot can help you with:
        - Equipment procedures and SOPs
        - Process recipes and parameters  
        - Safety protocols
        - Troubleshooting guides
        - Equipment specifications
        """)
        
        st.header("📊 Stats")
        if df is not None:
            st.metric("Knowledge Chunks", len(df))
            content_types = df['content_type'].nunique() if 'content_type' in df.columns else 0
            st.metric("Content Types", content_types)
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()