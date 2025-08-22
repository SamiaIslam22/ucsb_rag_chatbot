import streamlit as st

st.set_page_config(
    page_title="UCSB Nanofab - Home",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Custom CSS for better styling
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
        /* SUPER AGGRESSIVE font size for navigation only */
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
        
        /* Even more nuclear approach */
        .stSidebar * {
            font-size: 24px !important;
            font-weight: bold !important;
        }
        
        /* Hover effects */
        [data-testid="stSidebar"] a:hover,
        [data-testid="stSidebar"] div[role="button"]:hover {
            background: rgba(255,255,255,0.2) !important;
            transform: translateX(8px) !important;
        }
        
        /* All other styles remain the same for main content */
        
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(90deg, #FFE135 0%, #4A90E2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .feature-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #4A90E2;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stats-card {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin: 0.3rem 0;
        }
        
        .cta-button {
            background: linear-gradient(90deg, #00b894 0%, #00a085 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 25px;
            text-align: center;
            font-weight: bold;
            margin: 1rem 0;
            text-decoration: none;
            display: block;
        }
        
        .extraction-section {
            background: #f1f3f4;
            padding: 2rem;
            border-radius: 15px;
            margin: 2rem 0;
        }
        
        .purpose-section {
            background: linear-gradient(135deg, #87CEEB 0%, #4A90E2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin: 2rem 0;
            font-family: 'Calibri', 'Segoe UI', sans-serif;
        }
        
        .acknowledgment-section {
            background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin: 2rem 0;
        }
        
        .icon-header {
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Header
    st.markdown("""
    <div class="main-header">
        <div class="icon-header">🔬</div>
        <h1>UCSB Nanofab Knowledge Assistant</h1>
        <h3>Intelligent AI for UCSB Nanofabrication Facility</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome section with better layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        ## 🚀 Welcome to the UCSB Nanofab Knowledge Assistant
        
        This AI-powered chatbot provides **instant access** to comprehensive information extracted from the **UCSB Nanofabrication Facility's complete wiki knowledge base**. Our system has processed and indexed all content from the official UCSB wiki to provide expert guidance on equipment, processes, and procedures.
        """)
        
        st.markdown("""
        <div class="cta-button">
            💡 Ready to explore? Click "🔍 Search" in the sidebar to get started!
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Stats cards
        st.markdown("""
        <div class="stats-card">
            <h2>100+</h2>
            <p>Wiki Pages Processed</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="stats-card">
            <h2>📊 📋 📄</h2>
            <p>Multiple Content Types</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="stats-card">
            <h2>🔍</h2>
            <p>Real-time AI Search</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Data extraction section with better formatting
    st.markdown("""
    <div class="extraction-section">
        <h2>📊 What We Extracted from UCSB Wiki</h2>
        <p><strong>Source:</strong> <a href="https://wiki.nanofab.ucsb.edu/wiki/Special:AllPages" target="_blank">https://wiki.nanofab.ucsb.edu/wiki/Special:AllPages</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Four columns for extraction categories
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>⚙️ Equipment Documentation</h3>
            <ul>
                <li>Complete operation manuals & SOPs</li>
                <li>Equipment specifications</li>
                <li>Maintenance procedures</li>
                <li>Safety protocols</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🧪 Process Knowledge</h3>
            <ul>
                <li>Process recipes & parameters</li>
                <li>Material compatibility</li>
                <li>Step-by-step procedures</li>
                <li>Optimization techniques</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🛡️ Safety & Protocols</h3>
            <ul>
                <li>Laboratory safety procedures</li>
                <li>Chemical handling guidelines</li>
                <li>PPE requirements</li>
                <li>Emergency protocols</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <h3>📚 Research & Education</h3>
            <ul>
                <li>Technical backgrounds</li>
                <li>Best practices</li>
                <li>Research methodologies</li>
                <li>Educational resources</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Purpose section with colored background
    st.markdown("""
    <div class="purpose-section">
        <h2>🎯 Purpose & Motivation</h2>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 1rem;">
            <div>
                <h3>🤔 Why This System Exists</h3>
                <p>The UCSB Nanofabrication Facility houses extensive knowledge across hundreds of wiki pages, containing critical information for students, researchers, faculty, and industry partners. However, finding specific information quickly across this vast knowledge base can be challenging.</p>
            </div>
            <div>
                <h3>💡 Our Solution</h3>
                <p>This AI-powered assistant transforms how users interact with nanofab knowledge through intelligent search, instant access, source transparency, and comprehensive coverage across all content types simultaneously.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Example questions in a nice grid
    st.markdown("## 💡 Try These Example Questions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🔧 Equipment Questions</h4>
            <ul>
                <li>"What are the specifications for the Oxford RIE system?"</li>
                <li>"How do I clean the SEM sample holder?"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🧪 Process Questions</h4>
            <ul>
                <li>"What safety procedures are required for the furnace?"</li>
                <li>"What's the recipe for silicon etching?"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Key Features with icons
    st.markdown("## ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🧠 AI-Powered Search</h3>
            <p>Advanced semantic search using state-of-the-art embeddings and retrieval systems.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📚 Source Citations</h3>
            <p>Every answer includes direct links to original UCSB wiki pages for verification.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 Specialized Knowledge</h3>
            <p>Trained specifically on UCSB Nanofab content and procedures.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Acknowledgments section with gradient background
    st.markdown("""
    <div class="acknowledgment-section">
        <h2>🙏 Acknowledgments</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Dr. Demis D. John
        **Director, UCSB Nanofabrication Facility**
        
        For granting permission to extract and utilize the comprehensive UCSB Nanofab wiki content for this educational and research project.
        """)
    
    with col2:
        st.markdown("""
        ### Dr. Samantha Roberts
        **Director, ASRC Nanofabrication Facility**
        
        For providing invaluable mentorship in data science, Python programming, and backend development. Her technical architecture guidance shaped this project's implementation.
        """)
    
    st.markdown("""
    ### 🔬 Research Impact
    This project demonstrates the potential for AI-powered knowledge management systems in specialized research environments, making complex technical documentation more accessible through intelligent search and contextual response generation.
    """)
    
    # Technical details in collapsible section
    with st.expander("⚙️ Technical Details & Architecture"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Technology Stack:**
            - **Frontend:** Streamlit with custom CSS
            - **Backend:** Python with OpenAI APIs
            - **Search:** Vector similarity search
            - **Embeddings:** OpenAI text-embedding-3-small
            """)
        
        with col2:
            st.markdown("""
            **Data Pipeline:**
            1. Automated wiki extraction
            2. Content chunking & preprocessing
            3. Vector embedding generation
            4. Semantic search implementation
            5. Response generation with citations
            """)

if __name__ == "__main__":
    main()