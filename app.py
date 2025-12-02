import streamlit as st

# Page configuration
st.set_page_config(
    page_title="MTG Deck Builder",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page
st.title("🃏 Magic: The Gathering Deck Builder")
st.markdown("""
Welcome to the MTG Deck Builder application! This tool helps you manage your card collection and build optimized decks.

### 📋 Available Tools:
- **Card Collection Manager**: Clean and update your card collection data using Scryfall API and Gemini AI
- **Deck Builder**: Build optimized Commander and Standard decks from your collection

### 🚀 Getting Started:
1. Navigate to **Card Collection Manager** to clean/update your CSV data
2. Go to **Deck Builder** to create decks using your collection

Use the sidebar to navigate between pages.
""")

# Sidebar instructions
st.sidebar.title("Navigation")
st.sidebar.info("""
**Card Collection Manager**: Upload and clean your MTG card collection CSV

**Deck Builder**: Generate optimized decks from your collection
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔑 API Configuration")
st.sidebar.markdown("Ensure your `.env` file contains your `GEMINI_API_KEY`")

