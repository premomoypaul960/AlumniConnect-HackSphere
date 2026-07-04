import streamlit as st
import pandas as pd
import os
from google import genai
from streamlit_option_menu import option_menu
import time
from datetime import date

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AlumniConnect", layout="wide")

# --- SESSION STATE (LOGIN MEMORY) - MUST BE HERE! ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# --- CUSTOM CSS FOR MODERN UI & ANIMATIONS ---
custom_css = """
<style>
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .viewerBadge_container {display: none !important;}
    [data-testid="stViewerBadge"] {display: none !important;}
    
    /* 1. GLOBAL FADE-IN ANIMATION FOR ALL PAGES */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    div.block-container {
        animation: fadeUp 0.6s ease-out;
    }
    
    /* ... (rest of your CSS) ... */
