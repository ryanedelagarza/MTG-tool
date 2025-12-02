import streamlit as st
import pandas as pd
import csv
import requests
import time
import os
from typing import Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from io import StringIO
import tempfile

# Load environment variables
load_dotenv()  # For local development

# Helper function to get API key from either .env or Streamlit secrets
def get_api_key():
    """Get API key from Streamlit secrets or environment variable"""
    try:
        # Try Streamlit secrets first (for cloud deployment)
        return st.secrets.get("GEMINI_API_KEY")
    except:
        # Fall back to environment variable (for local development)
        return os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Card Collection Manager", page_icon="📋", layout="wide")

st.title("📋 Card Collection Manager")
st.markdown("""
Upload your Magic: The Gathering card collection CSV and enhance it with data from Scryfall API.

**✨ Smart Processing**: The tool automatically adds missing columns and fetches card data. 
All you need is a CSV with card names!

**🤖 AI Verification**: Optional Gemini AI verification for data accuracy and consistency.
""")

# Initialize session state
if 'cleaned_csv' not in st.session_state:
    st.session_state.cleaned_csv = None
if 'cleaned_csv_name' not in st.session_state:
    st.session_state.cleaned_csv_name = None

class MagicCardUpdater:
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.scryfall_api = "https://api.scryfall.com/cards/named"
        
        # Initialize Gemini if API key provided
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.gemini_model = None
    
    def search_scryfall(self, card_name: str) -> Optional[Dict]:
        """Search Scryfall API for card information"""
        try:
            params = {'fuzzy': card_name}
            response = requests.get(self.scryfall_api, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None
    
    def extract_card_data(self, card_data: Dict) -> Dict:
        """Extract relevant information from Scryfall response"""
        card_text = card_data.get('oracle_text', '')
        card_text = card_text.replace('\n', ' | ')
        
        extracted = {
            'colors': ', '.join(card_data.get('colors', [])) or 'Colorless',
            'mana_cost': card_data.get('mana_cost', ''),
            'card_text': card_text,
            'power_toughness': ''
        }
        
        if 'power' in card_data and 'toughness' in card_data:
            power = card_data['power']
            toughness = card_data['toughness']
            extracted['power_toughness'] = f"{power}.{toughness}"
        
        return extracted
    
    def verify_with_gemini(self, card_name: str, card_data: Dict, progress_callback=None) -> bool:
        """Use Gemini to verify the card information accuracy"""
        if not self.gemini_model:
            return True
        
        try:
            prompt = f"""You are verifying Magic: The Gathering card data for consistency and completeness.

IMPORTANT CONTEXT:
- This card may be from a Universe Beyond set (like Avatar: The Last Airbender, Warhammer 40K, Doctor Who, etc.)
- Universe Beyond cards are official MTG cards but feature characters/themes from other franchises
- Focus on verifying the DATA CONSISTENCY, not whether the card name sounds like a traditional MTG card

Card Name: {card_name}
Colors: {card_data['colors']}
Mana Cost: {card_data['mana_cost']}
Card Text: {card_data['card_text']}
Power/Toughness: {card_data['power_toughness']}

VERIFICATION CHECKLIST:
1. Does the mana cost format look valid?
2. Do the colors match what's in the mana cost?
3. If there's a Power/Toughness, does it make sense?
4. Does the card text contain valid MTG mechanics and formatting?
5. Is there any obvious data corruption or formatting errors?

Respond with 'VERIFIED' if the data looks consistent and properly formatted, or 'CONCERN: [specific issue]' only if there's a clear data quality problem."""

            response = self.gemini_model.generate_content(prompt)
            result = response.text.strip()
            
            if progress_callback:
                if 'VERIFIED' in result:
                    progress_callback("✓ Gemini verification passed")
                else:
                    progress_callback(f"⚠️ Gemini flagged issue: {result}")
            
            return 'VERIFIED' in result
        except Exception as e:
            if progress_callback:
                progress_callback(f"⚠️ Gemini verification failed: {e}")
            return True
    
    def update_csv(self, csv_content: str, progress_callback=None) -> str:
        """Process CSV content and return updated CSV"""
        # Read the CSV
        csv_file = StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        rows = list(reader)
        
        # Ensure Name column exists (required)
        if 'Name' not in fieldnames and 'Card Name' not in fieldnames:
            raise ValueError("CSV must have either 'Name' or 'Card Name' column")
        
        # Ensure required columns exist (will be auto-populated)
        required_cols = ['Card color(s)', 'Card Text', 'Mana Cost', 'Power/Toughness']
        added_cols = []
        for col in required_cols:
            if col not in fieldnames:
                fieldnames.append(col)
                added_cols.append(col)
        
        if added_cols and progress_callback:
            progress_callback(f"✨ Auto-added missing columns: {', '.join(added_cols)}")
        
        total_rows = len(rows)
        updated_count = 0
        
        # Process each row
        for idx, row in enumerate(rows, 1):
            card_name = row.get('Name', '').strip()
            
            if not card_name:
                if progress_callback:
                    progress_callback(f"Row {idx}/{total_rows}: Empty card name, skipping...")
                continue
            
            # Check if row needs updating
            needs_update = any(not row.get(col, '').strip() for col in required_cols)
            
            if not needs_update:
                if progress_callback:
                    progress_callback(f"Row {idx}/{total_rows}: '{card_name}' - Already complete ✓")
                continue
            
            if progress_callback:
                progress_callback(f"Row {idx}/{total_rows}: Processing '{card_name}'...")
            
            # Search Scryfall
            card_data = self.search_scryfall(card_name)
            
            if not card_data:
                if progress_callback:
                    progress_callback(f"  ❌ Could not find card data for '{card_name}'")
                continue
            
            # Extract information
            extracted = self.extract_card_data(card_data)
            
            # Update only empty fields
            for csv_col, data_key in [
                ('Card color(s)', 'colors'),
                ('Card Text', 'card_text'),
                ('Mana Cost', 'mana_cost'),
                ('Power/Toughness', 'power_toughness')
            ]:
                if not row.get(csv_col, '').strip():
                    row[csv_col] = extracted[data_key]
            
            # Verify with Gemini
            self.verify_with_gemini(card_name, extracted, progress_callback)
            
            if progress_callback:
                progress_callback(f"  ✅ Updated '{card_name}' successfully")
            updated_count += 1
            
            # Rate limiting
            time.sleep(0.1)
        
        # Write to string
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
        if progress_callback:
            progress_callback(f"\n✅ Complete! Updated {updated_count} cards out of {total_rows} total cards")
        
        return output.getvalue()


# Main UI
col1, col2 = st.columns([2, 1])

with col1:
    st.header("1️⃣ Upload Your Card Collection")
    
    st.info("💡 **Tip**: Your CSV only needs a 'Name' column. Missing columns will be auto-added and populated!")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your MTG card collection CSV. Minimum requirement: A 'Name' or 'Card Name' column with card names."
    )
    
    if uploaded_file is not None:
        # Display preview
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Loaded {len(df)} cards from {uploaded_file.name}")
        
        with st.expander("📊 Preview Data (first 10 rows)"):
            st.dataframe(df.head(10), use_container_width=True)
        
        # Process button
        st.header("2️⃣ Process Card Data")
        
        use_gemini = st.checkbox(
            "Use Gemini AI for verification",
            value=True,
            help="Enable AI-powered verification of card data (requires GEMINI_API_KEY in .env)"
        )
        
        if st.button("🚀 Process Card Collection", type="primary", use_container_width=True):
            # Get API key if needed
            api_key = None
            if use_gemini:
                api_key = get_api_key()
                if not api_key:
                    st.error("❌ GEMINI_API_KEY not found! Please add it to Streamlit secrets or .env file!")
                    st.stop()
            
            # Create updater
            updater = MagicCardUpdater(api_key if use_gemini else None)
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.expander("📝 Processing Log", expanded=True)
            log_text = log_container.empty()
            logs = []
            
            def log_callback(message):
                logs.append(message)
                log_text.text('\n'.join(logs[-20:]))  # Show last 20 messages
            
            # Reset file pointer
            uploaded_file.seek(0)
            csv_content = uploaded_file.read().decode('utf-8')
            
            # Process
            with st.spinner("Processing cards..."):
                try:
                    result_csv = updater.update_csv(csv_content, log_callback)
                    
                    # Store in session state
                    st.session_state.cleaned_csv = result_csv
                    st.session_state.cleaned_csv_name = f"cleaned_{uploaded_file.name}"
                    
                    progress_bar.progress(100)
                    status_text.success("✅ Processing complete!")
                    
                    st.success("🎉 Card collection processed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error processing cards: {e}")
                    st.stop()

with col2:
    st.header("📥 Download Results")
    
    if st.session_state.cleaned_csv:
        st.success("✅ Cleaned data ready!")
        
        # Download button
        st.download_button(
            label="💾 Download Cleaned CSV",
            data=st.session_state.cleaned_csv,
            file_name=st.session_state.cleaned_csv_name,
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
        
        # Option to use in deck builder
        st.info("💡 You can now use this cleaned data in the **Deck Builder** page!")
        
        # Preview cleaned data
        with st.expander("👁️ Preview Cleaned Data"):
            cleaned_df = pd.read_csv(StringIO(st.session_state.cleaned_csv))
            st.dataframe(cleaned_df.head(10), use_container_width=True)
    else:
        st.info("Upload and process a CSV file to download the cleaned results.")

# Help section
st.markdown("---")
with st.expander("ℹ️ Help & Information"):
    st.markdown("""
    ### How to use:
    1. **Upload CSV**: Select your MTG card collection CSV file
    2. **Enable AI Verification** (optional): Use Gemini AI to verify card data accuracy
    3. **Process**: Click "Process Card Collection" to enhance your data with Scryfall API
    4. **Download**: Save the cleaned CSV or use it directly in the Deck Builder
    
    ### Required CSV Format:
    - **Required**: Must have a `Name` or `Card Name` column with card names
    - **Auto-Added**: If missing, these columns will be automatically added and populated:
      - `Card color(s)` - Card colors (e.g., Red, Blue)
      - `Card Text` - Oracle text from Scryfall
      - `Mana Cost` - Mana cost in MTG format
      - `Power/Toughness` - For creatures
    - **Optional**: `Is Fancy` - Mark special/premium versions
    
    ### What this tool does:
    - ✨ **Automatically adds missing columns** to your CSV
    - 🔍 Fetches missing card data from Scryfall API
    - 📝 Standardizes card text and formatting
    - 🤖 Verifies data accuracy with AI (optional)
    - 💾 Preserves your existing data (only fills in missing fields)
    
    ### Example Minimal CSV:
    ```csv
    Name
    Sol Ring
    Lightning Bolt
    Forest
    ```
    This is all you need! The script will fetch and add all other data automatically.
    """)

