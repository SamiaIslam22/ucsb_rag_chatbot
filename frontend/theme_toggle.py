# theme_toggle.py - Save this as a separate file in your frontend folder
import streamlit as st

def init_theme():
    """Initialize theme in session state if not exists"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

def toggle_theme():
    """Toggle between dark and light mode"""
    st.session_state.dark_mode = not st.session_state.dark_mode

def render_theme_toggle():
    """Render the theme toggle switch in the top right"""
    init_theme()
    
    # Create columns to position toggle on the right
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col3:
        if st.session_state.dark_mode:
            if st.button("🌞", key="theme_toggle", help="Switch to light mode"):
                toggle_theme()
                st.rerun()
        else:
            if st.button("🌙", key="theme_toggle", help="Switch to dark mode"):
                toggle_theme()
                st.rerun()

def get_theme_css():
    """Return CSS based on current theme"""
    init_theme()
    
    if st.session_state.dark_mode:
        # Dark mode CSS
        return """
        <style>
            /* Dark mode theme */
            .stApp {
                background-color: #1a1a1a;
                color: #ffffff;
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
            
            /* Feature cards - dark */
            .feature-card {
                background: #2d2d2d;
                color: #ffffff;
                padding: 1.5rem;
                border-radius: 10px;
                border-left: 4px solid #3498db;
                margin: 1rem 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            
            /* Stats cards - dark */
            .stats-card {
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 1rem;
                border-radius: 10px;
                text-align: center;
                margin: 0.3rem 0;
            }
            
            /* Search tips - dark */
            .search-tip {
                background: rgba(255,255,255,0.05);
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                border-left: 4px solid rgba(255,255,255,0.3);
            }
            
            /* Extraction section - dark */
            .extraction-section {
                background: #2d2d2d;
                color: #ffffff;
                padding: 2rem;
                border-radius: 15px;
                margin: 2rem 0;
            }
            
            /* Purpose section - dark */
            .purpose-section {
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin: 2rem 0;
            }
            
            /* Acknowledgment section - dark */
            .acknowledgment-section {
                background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin: 2rem 0;
            }
            
            /* Dark mode for chat messages */
            .stChatMessage {
                background-color: #2d2d2d;
            }
            
            /* Dark mode for expanders */
            .streamlit-expanderHeader {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            
            /* Dark mode for buttons */
            .stButton > button {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444;
            }
            
            /* Dark mode for text input */
            .stTextInput > div > div > input {
                background-color: #2d2d2d;
                color: #ffffff;
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
            
            /* Sidebar button styling */
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
            
            /* CTA button - dark */
            .cta-button {
                background: linear-gradient(90deg, #34495e 0%, #2c3e50 100%);
                color: white;
                padding: 1rem 2rem;
                border-radius: 25px;
                text-align: center;
                font-weight: bold;
                margin: 1rem 0;
                text-decoration: none;
                display: block;
            }
        </style>
        """
    else:
        # Light mode CSS (your original)
        return """
        <style>
            /* Light mode theme */
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
            
            /* Feature cards */
            .feature-card {
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 10px;
                border-left: 4px solid #4A90E2;
                margin: 1rem 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            /* Stats cards */
            .stats-card {
                background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
                color: white;
                padding: 1rem;
                border-radius: 10px;
                text-align: center;
                margin: 0.3rem 0;
            }
            
            /* CTA button */
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
            
            /* Extraction section */
            .extraction-section {
                background: #f1f3f4;
                padding: 2rem;
                border-radius: 15px;
                margin: 2rem 0;
            }
            
            /* Purpose section */
            .purpose-section {
                background: linear-gradient(135deg, #87CEEB 0%, #4A90E2 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin: 2rem 0;
            }
            
            /* Acknowledgment section */
            .acknowledgment-section {
                background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin: 2rem 0;
            }
            
            /* Icon header */
            .icon-header {
                font-size: 2.5rem;
                text-align: center;
                margin-bottom: 1rem;
            }
        </style>
        """