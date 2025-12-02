import csv
import os
from typing import List, Dict, Optional
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

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
    
    def load_collection(self, csv_file: str) -> List[Dict]:
        """Load the user's card collection from CSV"""
        print(f"📚 Loading collection from {csv_file}...")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cards = list(reader)
        
        print(f"✅ Loaded {len(cards)} cards from collection\n")
        return cards
    
    def load_knowledge_base(self, format_type: str) -> str:
        """Load relevant knowledge base documents from directories"""
        print(f"📖 Loading knowledge base for {format_type}...")
        
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
            print("⚠️  No knowledge base files found. Creating basic guidelines...")
            knowledge_content = self.create_default_knowledge(format_type)
        else:
            print(f"✅ Loaded {files_loaded} knowledge base file(s)\n")
        
        return knowledge_content
    
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
        else:  # Standard
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
            card_colors = card.get('Card Color(s)', '').upper()
            
            # Check if card is colorless or matches color preferences
            if 'COLORLESS' in card_colors or not card_colors:
                filtered.append(card)
            else:
                # Check if all card colors are in user's preferences
                card_color_list = [c.strip() for c in card_colors.split(',')]
                color_map = {
                    'GREEN': 'G', 'RED': 'R', 'BLACK': 'B', 
                    'WHITE': 'W', 'BLUE': 'U'
                }
                
                card_color_codes = [color_map.get(c, c) for c in card_color_list]
                user_color_codes = [c[0].upper() for c in colors]
                
                if all(cc in user_color_codes for cc in card_color_codes):
                    filtered.append(card)
        
        print(f"🎨 Filtered to {len(filtered)} cards matching color preference\n")
        return filtered
    
    def format_collection_for_prompt(self, cards: List[Dict]) -> str:
        """Format card collection for the AI prompt"""
        collection_text = "# USER'S CARD COLLECTION\n\n"
        
        for card in cards:
            card_name = card.get('Card Name', 'Unknown')
            colors = card.get('Card Color(s)', 'Unknown')
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
- **Grouping**: Group cards by type—Lands, Creatures, Instants, Sorceries, Artifacts, Enchantments, Planeswalkers, Others—and sort alphabetically within each group
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
    
    def build_deck(self, csv_file: str, format_type: str, colors: List[str],
                   commander: Optional[str] = None, additional_notes: str = "") -> str:
        """Main method to build a deck"""
        
        print("=" * 60)
        print("🃏 MAGIC DECK BUILDER")
        print("=" * 60)
        print(f"Format: {format_type}")
        print(f"Colors: {', '.join(colors) if colors else 'Any'}")
        if commander:
            print(f"Commander: {commander}")
        print("=" * 60)
        print()
        
        # Load collection
        cards = self.load_collection(csv_file)
        
        # Filter by colors
        filtered_cards = self.filter_by_colors(cards, colors)
        
        if not filtered_cards:
            return "❌ Error: No cards found matching the color preference!"
        
        # Load knowledge base
        knowledge = self.load_knowledge_base(format_type)
        
        # Format collection for prompt
        print("📝 Formatting collection for AI...")
        collection_text = self.format_collection_for_prompt(filtered_cards)
        
        # Build system prompt
        print("🔧 Building prompt...")
        system_prompt = self.build_system_prompt(
            format_type, colors, commander, additional_notes, knowledge
        )
        
        # Combine everything
        full_prompt = f"{system_prompt}\n\n{collection_text}"
        
        # Call Gemini
        print("🤖 Generating deck with Gemini AI...\n")
        print("⏳ This may take a moment...\n")
        
        try:
            response = self.model.generate_content(full_prompt)
            result = response.text
            
            # Save the deck
            output_file = self.save_deck(result, format_type, colors)
            
            print("\n" + "=" * 60)
            print(f"✅ DECK BUILDING COMPLETE!")
            print(f"💾 Saved to: {output_file}")
            print("=" * 60)
            
            return result
            
        except Exception as e:
            error_msg = f"❌ Error generating deck: {e}"
            print(error_msg)
            return error_msg
    
    def save_deck(self, deck_content: str, format_type: str, colors: List[str]) -> str:
        """Save the generated deck to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        color_str = "_".join(colors) if colors else "any"
        filename = f"deck_{format_type}_{color_str}_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(deck_content)
        
        return filename


def main():
    """Main interactive function"""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set!")
        print("Please set it with: export GEMINI_API_KEY='your-key-here'")
        return
    
    # Initialize builder
    builder = MagicDeckBuilder(api_key)
    
    # Get user inputs
    print("\n" + "=" * 60)
    print("🎴 MAGIC: THE GATHERING DECK BUILDER")
    print("=" * 60 + "\n")
    
    # CSV file - automatically use collection/ATLA.csv
    csv_file = "collection/ATLA.csv"
    if not os.path.exists(csv_file):
        print(f"❌ Error: File '{csv_file}' not found!")
        return
    print(f"📁 Using card collection: {csv_file}")
    
    # Format type
    print("\n📋 Select deck format:")
    print("1. Commander")
    print("2. Standard")
    format_choice = input("Enter choice (1 or 2): ").strip()
    format_type = "Commander" if format_choice == "1" else "Standard"
    
    # Commander selection (if applicable)
    commander = None
    if format_type == "Commander":
        has_commander = input("\n👑 Do you have a commander in mind? (y/n): ").strip().lower()
        if has_commander == 'y':
            commander = input("Enter commander name: ").strip()
    
    # Color selection
    print("\n🎨 Select colors (enter numbers or names separated by spaces, or press Enter for all):")
    print("1. White")
    print("2. Blue")
    print("3. Black")
    print("4. Red")
    print("5. Green")
    color_input = input("Enter choices: ").strip()
    
    color_map = {'1': 'White', '2': 'Blue', '3': 'Black', '4': 'Red', '5': 'Green'}
    color_name_map = {'white': 'White', 'blue': 'Blue', 'black': 'Black', 'red': 'Red', 'green': 'Green',
                      'w': 'White', 'u': 'Blue', 'b': 'Black', 'r': 'Red', 'g': 'Green'}
    
    colors = []
    if color_input:
        for c in color_input.split():
            c_lower = c.lower()
            if c in color_map:  # Number input
                if color_map[c] not in colors:
                    colors.append(color_map[c])
            elif c_lower in color_name_map:  # Color name or abbreviation
                if color_name_map[c_lower] not in colors:
                    colors.append(color_name_map[c_lower])
    
    # Additional notes
    print("\n📝 Any additional notes or preferences?")
    additional_notes = input("(Press Enter to skip): ").strip()
    
    # Build the deck
    print("\n")
    deck = builder.build_deck(csv_file, format_type, colors, commander, additional_notes)
    
    # Display result
    print("\n" + "=" * 60)
    print("GENERATED DECK")
    print("=" * 60)
    print(deck)


if __name__ == "__main__":
    main()