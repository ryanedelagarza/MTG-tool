import streamlit as st
import pandas as pd
import csv
import os
from typing import List, Dict, Optional
import google.generativeai as genai
from datetime import datetime
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

st.title("ðŸƒ Magic: The Gathering Deck Builder")
st.markdown("""
Build optimized Commander and Standard decks from your card collection using AI-powered strategy analysis.
""")

# Initialize session state
if 'generated_deck' not in st.session_state:
    st.session_state.generated_deck = None
if 'deck_filename' not in st.session_state:
    st.session_state.deck_filename = None


class MagicDeckBuilder:
    def __init__(self, api_key: str):
        """Initialize the deck builder with Gemini API"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Knowledge base directories
        self.knowledge_base = {
            'commander': 'knowledge/commander',
            'standard': 'knowledge/standard',
            'general': 'knowledge/general'
        }
    
    def load_collection_from_string(self, csv_content: str) -> List[Dict]:
        """Load the user's card collection from CSV string"""
        csv_file = StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        cards = list(reader)
        return cards
    
    def load_knowledge_base(self, format_type: str) -> str:
        """Load relevant knowledge base documents from directories"""
        knowledge_content = ""
        files_loaded = 0
        
        # Load general knowledge from directory
        if os.path.exists(self.knowledge_base['general']) and os.path.isdir(self.knowledge_base['general']):
            general_files = [f for f in os.listdir(self.knowledge_base['general']) 
                           if f.endswith(('.txt', '.md'))]
            for filename in general_files:
                filepath = os.path.join(self.knowledge_base['general'], filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    knowledge_content += f"# General: {filename}\n{f.read()}\n\n"
                    files_loaded += 1
        
        # Load format-specific knowledge from directory
        format_key = format_type.lower()
        if format_key in self.knowledge_base and os.path.exists(self.knowledge_base[format_key]):
            if os.path.isdir(self.knowledge_base[format_key]):
                format_files = [f for f in os.listdir(self.knowledge_base[format_key]) 
                              if f.endswith(('.txt', '.md'))]
                for filename in format_files:
                    filepath = os.path.join(self.knowledge_base[format_key], filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        knowledge_content += f"# {format_type.title()}: {filename}\n{f.read()}\n\n"
                        files_loaded += 1
        
        if not knowledge_content:
            knowledge_content = self.create_default_knowledge(format_type)
        
        return knowledge_content, files_loaded
    
    def create_default_knowledge(self, format_type: str) -> str:
        """Create basic knowledge if files don't exist"""
        if format_type.lower() == 'commander':
            return """# Commander Deck Building Basics
- 100 cards total including commander
- Singleton format (only 1 copy of each card except basic lands)
- Typical land count: 36-38
- Ramp cards: 8-12
- Card draw: 8-12
- Removal: 8-12
- Win conditions: 3-5
- Synergy with commander is crucial
"""
        else:
            return """# Standard Deck Building Basics
- 60 cards minimum
- Up to 4 copies of each card (except basic lands)
- Typical land count: 24-26 for 60-card deck
- Mana curve is critical (peak at 2-3 CMC)
- Include removal and interaction
- Clear win condition
"""
    
    def filter_by_colors(self, cards: List[Dict], colors: List[str]) -> List[Dict]:
        """Filter cards by color preference"""
        if not colors or 'Any' in colors:
            return cards
        
        filtered = []
        for card in cards:
            card_colors = card.get('Card color(s)', '').upper()
            
            if 'COLORLESS' in card_colors or not card_colors:
                filtered.append(card)
            else:
                card_color_list = [c.strip() for c in card_colors.split(',')]
                color_map = {
                    'GREEN': 'G', 'RED': 'R', 'BLACK': 'B', 
                    'WHITE': 'W', 'BLUE': 'U'
                }
                
                card_color_codes = [color_map.get(c, c) for c in card_color_list]
                user_color_codes = [c[0].upper() for c in colors]
                
                if all(cc in user_color_codes for cc in card_color_codes):
                    filtered.append(card)
        
        return filtered
    
    def format_collection_for_prompt(self, cards: List[Dict]) -> str:
        """Format card collection for the AI prompt"""
        collection_text = "# USER'S CARD COLLECTION\n\n"
        
        for card in cards:
            card_name = card.get('Card Name', card.get('Name', 'Unknown'))
            colors = card.get('Card color(s)', card.get('Card Color(s)', 'Unknown'))
            mana_cost = card.get('Mana Cost', 'Unknown')
            card_text = card.get('Card Text', 'No text')
            pt = card.get('Power/Toughness', '')
            is_fancy = card.get('Is Fancy', 'No')
            
            collection_text += f"**{card_name}**\n"
            collection_text += f"- Colors: {colors}\n"
            collection_text += f"- Mana Cost: {mana_cost}\n"
            if pt:
                collection_text += f"- Power/Toughness: {pt}\n"
            collection_text += f"- Text: {card_text}\n"
            collection_text += f"- Is Fancy: {is_fancy}\n\n"
        
        return collection_text
    
    def build_system_prompt(self, format_type: str, colors: List[str], 
                           commander: Optional[str], additional_notes: str,
                           knowledge: str) -> str:
        """Build the comprehensive system prompt"""
        
        color_str = ', '.join(colors) if colors else 'Any colors'
        
        prompt = f"""# Role and Objective
You are a skilled assistant with extensive expertise in building Magic: The Gathering {format_type} decks using exclusively the user's personal card collection. You specialize in all deck styles and color combinations.

# Current Deck Parameters
- **Format**: {format_type}
- **Color Preference**: {color_str}
"""
        
        if format_type.lower() == 'commander':
            if commander:
                prompt += f"- **Commander**: {commander} (pre-selected)\n"
            else:
                prompt += f"- **Commander**: Select the best commander from the collection for {color_str}\n"
        
        if additional_notes:
            prompt += f"\n# Additional User Notes\n{additional_notes}\n"
        
        prompt += f"""
# Knowledge Base
{knowledge}

# Instructions

1. **Knowledge Analysis**: 
   - Analyze the provided knowledge documents for best practices in {format_type} deck building
   - Extract key insights relevant to {color_str} strategies

2. **Deck Planning**:
   - Develop a clear plan for card selection, including recommended counts for each card type
   - Provide initial strategic notes relevant to the chosen colors and format
"""
        
        if format_type.lower() == 'commander' and not commander:
            prompt += """   - **FIRST**: Select the best commander from the collection that fits the color preference
   - Explain why this commander was chosen
"""
        
        prompt += """
3. **Deck Construction**:
   - Build a COMPLETE deck strictly from the user's collection
   - You MUST build a full deck using ONLY cards from the provided collection
   - Do NOT include any cards marked as "MISSING FROM COLLECTION"
   - Follow the established plan and selection guidelines
   - Ensure color identity matches requirements
   - If certain optimal cards aren't available, select the best alternatives from the collection

4. **Dual Perspective Review**:
   - Critically review the constructed deck from two distinct perspectives (e.g., competitive play, casual play, synergy focus)
   - Offer detailed feedback from each perspective (limit to 3-4 concise sentences per perspective)

5. **Synthesis and Adjustment**:
   - Integrate feedback and make any necessary deck adjustments
   - Ensure the deck is still using ONLY cards from the collection

6. **Final Presentation**:
   - Present the final card list in the specified format
   - Prioritize inclusion of the user's "fancier" cards where it adds strategic or aesthetic value
   - After the complete decklist, provide a separate "Suggested Upgrades" section listing cards not in the collection that would improve the deck

# Output Format

- **Decklist**: Present a Markdown table with columns: Card Name, Card Type, Is Fancy (Yes/No), and Notes
- **Grouping**: Group cards by typeâ€”Lands, Creatures, Instants, Sorceries, Artifacts, Enchantments, Planeswalkers, Othersâ€”and sort alphabetically within each group
- **Is Fancy**: Indicate 'Yes' if a card is marked as fancy in the collection, otherwise 'No'
- **ALL CARDS MUST BE FROM COLLECTION**: Do not include any cards not in the user's collection in the main decklist
- **Summary**: Show total counts for each card type after the decklist
- **Suggested Upgrades Section**: AFTER the complete decklist and summary, create a separate section titled "## Suggested Upgrades" that lists cards NOT in the collection that would improve the deck, with brief explanations of why they would be beneficial

### Example Markdown Table

| Card Name | Card Type | Is Fancy | Notes |
|-----------|-----------|----------|-------|
| Forest | Land | No | Basic mana |
| Sol Ring | Artifact | Yes | Ramp |
| ... | ... | ... | ... |

### Card Type Summary
- Lands: X
- Creatures: X
- Artifacts: X
- Enchantments: X
- Instants: X
- Sorceries: X
- Planeswalkers: X

# Reasoning Steps
- Think through each phase step by step: analyze knowledge, plan deck structure, select cards from collection, review from multiple perspectives, and adjust accordingly

# Output Verbosity
- Respond with no more than 2 short paragraphs for narrative sections
- For feedback in the Dual Perspective Review, limit to 3-4 concise sentences per perspective
- Decklist and summaries should remain clear and complete

# Stop Conditions
- Task is complete when you have delivered:
  1. A finished, grouped, and annotated Markdown decklist using ONLY cards from the user's collection
  2. A card type summary
  3. A "Suggested Upgrades" section listing cards not in the collection that would improve the deck
"""
        
        return prompt
    
    def build_deck(self, csv_content: str, format_type: str, colors: List[str],
                   commander: Optional[str] = None, additional_notes: str = "",
                   progress_callback=None) -> str:
        """Main method to build a deck"""
        
        # Load collection
        if progress_callback:
            progress_callback("ðŸ“š Loading collection...")
        cards = self.load_collection_from_string(csv_content)
        
        if progress_callback:
            progress_callback(f"âœ… Loaded {len(cards)} cards from collection")
        
        # Filter by colors
        if progress_callback:
            progress_callback("ðŸŽ¨ Filtering cards by color preference...")
        filtered_cards = self.filter_by_colors(cards, colors)
        
        if not filtered_cards:
            return "âŒ Error: No cards found matching the color preference!"
        
        if progress_callback:
            progress_callback(f"âœ… Filtered to {len(filtered_cards)} cards")
        
        # Load knowledge base
        if progress_callback:
            progress_callback(f"ðŸ“– Loading knowledge base for {format_type}...")
        knowledge, files_loaded = self.load_knowledge_base(format_type)
        
        if progress_callback:
            progress_callback(f"âœ… Loaded {files_loaded} knowledge base file(s)")
        
        # Format collection for prompt
        if progress_callback:
            progress_callback("ðŸ“ Formatting collection for AI...")
        collection_text = self.format_collection_for_prompt(filtered_cards)
        
        # Build system prompt
        if progress_callback:
            progress_callback("ðŸ”§ Building prompt...")
        system_prompt = self.build_system_prompt(
            format_type, colors, commander, additional_notes, knowledge
        )
        
        # Combine everything
        full_prompt = f"{system_prompt}\n\n{collection_text}"
        
        # Call Gemini
        if progress_callback:
            progress_callback("ðŸ¤– Generating deck with Gemini AI... (this may take a moment)")
        
        try:
            response = self.model.generate_content(full_prompt)
            result = response.text
            
            if progress_callback:
                progress_callback("âœ… Deck generation complete!")
            
            return result
            
        except Exception as e:
            error_msg = f"âŒ Error generating deck: {e}"
            if progress_callback:
                progress_callback(error_msg)
            return error_msg


# Main UI
st.header("1ï¸âƒ£ Select Card Collection")

# Create tabs for different input methods
tab1, tab2 = st.tabs(["ðŸ“‹ Use Cleaned Data", "ðŸ“¤ Upload New CSV"])

csv_content = None
csv_source = None

with tab1:
    if 'cleaned_csv' in st.session_state and st.session_state.cleaned_csv:
        st.success(f"âœ… Cleaned data available: {st.session_state.cleaned_csv_name}")
        
        # Preview
        cleaned_df = pd.read_csv(StringIO(st.session_state.cleaned_csv))
        st.info(f"ðŸ“Š {len(cleaned_df)} cards in collection")
        
        with st.expander("ðŸ‘ï¸ Preview Collection"):
            st.dataframe(cleaned_df.head(10), use_container_width=True)
        
        if st.button("âœ… Use This Collection", type="primary", use_container_width=True):
            csv_content = st.session_state.cleaned_csv
            csv_source = "cleaned"
            st.success("Collection selected!")
    else:
        st.info("No cleaned data available. Please visit the **Card Collection Manager** page first, or upload a CSV in the next tab.")

with tab2:
    uploaded_file = st.file_uploader(
        "Upload a CSV file",
        type=['csv'],
        help="Upload your MTG card collection CSV"
    )
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success(f"âœ… Loaded {len(df)} cards from {uploaded_file.name}")
        
        with st.expander("ðŸ‘ï¸ Preview Collection"):
            st.dataframe(df.head(10), use_container_width=True)
        
        if st.button("âœ… Use This Collection", type="primary", use_container_width=True):
            uploaded_file.seek(0)
            csv_content = uploaded_file.read().decode('utf-8')
            csv_source = "uploaded"
            st.success("Collection selected!")

# Deck Building Configuration
if csv_content:
    st.markdown("---")
    st.header("2ï¸âƒ£ Configure Your Deck")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Format selection
        format_type = st.selectbox(
            "ðŸŽ´ Deck Format",
            options=["Commander", "Standard"],
            help="Select the format for your deck"
        )
        
        # Commander selection (if Commander format)
        commander = None
        if format_type == "Commander":
            use_commander = st.checkbox("Select a specific commander", value=False)
            if use_commander:
                commander = st.text_input(
                    "Commander Name",
                    placeholder="e.g., Aang, Avatar",
                    help="Enter the exact name of your commander"
                )
    
    with col2:
        # Color selection
        st.write("ðŸŽ¨ **Color Identity**")
        color_options = {
            "White": st.checkbox("White (W)", key="white"),
            "Blue": st.checkbox("Blue (U)", key="blue"),
            "Black": st.checkbox("Black (B)", key="black"),
            "Red": st.checkbox("Red (R)", key="red"),
            "Green": st.checkbox("Green (G)", key="green")
        }
        
        selected_colors = [color for color, selected in color_options.items() if selected]
        
        if not selected_colors:
            st.info("ðŸ’¡ No colors selected = All colors available")
    
    # Additional notes
    additional_notes = st.text_area(
        "ðŸ“ Additional Notes or Preferences",
        placeholder="e.g., Focus on tribal synergies, competitive meta, budget-friendly, etc.",
        help="Provide any additional guidance for deck building"
    )
    
    # Build deck button
    st.markdown("---")
    st.header("3ï¸âƒ£ Generate Deck")
    
    if st.button("ðŸš€ Build Deck", type="primary", use_container_width=True):
        # Validate API key
        api_key = get_api_key()
        if not api_key:
            st.error("âŒ GEMINI_API_KEY not found! Please add it to Streamlit secrets or .env file!")
            st.stop()
        
        # Create deck builder
        builder = MagicDeckBuilder(api_key)
        
        # Progress tracking
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.expander("ðŸ“ Build Log", expanded=True)
            log_text = log_container.empty()
            logs = []
            
            def log_callback(message):
                logs.append(message)
                log_text.text('\n'.join(logs))
                # Update progress bar based on keywords
                if "Loading collection" in message:
                    progress_bar.progress(10)
                elif "Filtered" in message:
                    progress_bar.progress(20)
                elif "Loading knowledge" in message:
                    progress_bar.progress(30)
                elif "Formatting collection" in message:
                    progress_bar.progress(40)
                elif "Building prompt" in message:
                    progress_bar.progress(50)
                elif "Generating deck" in message:
                    progress_bar.progress(60)
                elif "complete" in message.lower():
                    progress_bar.progress(100)
        
        # Build deck
        with st.spinner("Building your deck..."):
            try:
                result = builder.build_deck(
                    csv_content,
                    format_type,
                    selected_colors if selected_colors else [],
                    commander if format_type == "Commander" else None,
                    additional_notes,
                    log_callback
                )
                
                # Store in session state
                st.session_state.generated_deck = result
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                color_str = "_".join(selected_colors) if selected_colors else "any"
                st.session_state.deck_filename = f"deck_{format_type}_{color_str}_{timestamp}.md"
                
                progress_bar.progress(100)
                status_text.success("âœ… Deck building complete!")
                
            except Exception as e:
                st.error(f"âŒ Error building deck: {e}")
                st.stop()

# Display results
if st.session_state.generated_deck:
    st.markdown("---")
    st.header("ðŸŽ‰ Your Generated Deck")
    
    # Download button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="ðŸ’¾ Download Deck as Markdown",
            data=st.session_state.generated_deck,
            file_name=st.session_state.deck_filename,
            mime="text/markdown",
            use_container_width=True,
            type="primary"
        )
    
    # Display deck
    st.markdown(st.session_state.generated_deck)

# Help section
st.markdown("---")
with st.expander("â„¹ï¸ Help & Tips"):
    st.markdown("""
    ### How to build a deck:
    1. **Select Collection**: Choose to use cleaned data from Card Collection Manager or upload a new CSV
    2. **Configure Deck**: 
       - Choose format (Commander or Standard)
       - Select color identity
       - Optionally specify a commander (Commander format only)
       - Add any additional preferences
    3. **Generate**: Click "Build Deck" and wait for the AI to create your optimized deck
    4. **Download**: Save your deck as a Markdown file
    
    ### Tips for best results:
    - Use cleaned data from the Card Collection Manager for optimal accuracy
    - Be specific in your additional notes (e.g., "aggressive strategy" vs "control")
    - For Commander, let the AI choose the commander if you're unsure
    - The AI will only use cards from your collection and suggest upgrades separately
    
    ### Deck Format Requirements:
    - **Commander**: 100 cards including commander, singleton format
    - **Standard**: 60+ cards minimum, up to 4 copies per card
    """)


