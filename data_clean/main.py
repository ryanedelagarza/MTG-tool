import csv
import requests
import time
import os
from typing import Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv

class MagicCardUpdater:
    def __init__(self, csv_file: str, gemini_api_key: Optional[str] = None):
        self.csv_file = csv_file
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
                print(f"  ⚠️  Scryfall API error for '{card_name}': {response.status_code}")
                return None
        except Exception as e:
            print(f"  ❌ Error fetching from Scryfall: {e}")
            return None
    
    def extract_card_data(self, card_data: Dict) -> Dict:
        """Extract relevant information from Scryfall response"""
        # Get card text and preserve formatting, replace newlines with space + newline for CSV compatibility
        card_text = card_data.get('oracle_text', '')
        # Preserve line breaks but ensure they work in CSV
        card_text = card_text.replace('\n', ' | ')
        
        extracted = {
            'colors': ', '.join(card_data.get('colors', [])) or 'Colorless',
            'mana_cost': card_data.get('mana_cost', ''),
            'card_text': card_text,
            'power_toughness': ''
        }
        
        # Handle power/toughness for creatures - use decimal format to avoid Excel date conversion
        if 'power' in card_data and 'toughness' in card_data:
            power = card_data['power']
            toughness = card_data['toughness']
            # Convert to decimal format: 2/1 -> 2.1
            extracted['power_toughness'] = f"{power}.{toughness}"
        
        return extracted
    
    def verify_with_gemini(self, card_name: str, card_data: Dict, scryfall_url: str = "") -> bool:
        """Use Gemini to verify the card information accuracy"""
        if not self.gemini_model:
            return True  # Skip verification if no Gemini API key
        
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
Scryfall Link: {scryfall_url}

VERIFICATION CHECKLIST:
1. Does the mana cost format look valid? (e.g., {{1}}{{W}}, {{2}}{{U}}{{U}})
2. Do the colors match what's in the mana cost?
3. If there's a Power/Toughness, does it make sense? (Note: format is decimal like "3.3" or "2.1" representing power.toughness)
4. Does the card text contain valid MTG mechanics and formatting?
5. Is there any obvious data corruption or formatting errors?

Respond with 'VERIFIED' if the data looks consistent and properly formatted, or 'CONCERN: [specific issue]' only if there's a clear data quality problem."""

            response = self.gemini_model.generate_content(prompt)
            result = response.text.strip()
            
            if 'VERIFIED' in result:
                print(f"  ✓ Gemini verification passed")
                return True
            else:
                print(f"  ⚠️  Gemini flagged issue: {result}")
                return False
        except Exception as e:
            print(f"  ⚠️  Gemini verification failed: {e}")
            return True  # Continue even if verification fails
    
    def update_csv(self):
        """Main loop to update the CSV file"""
        # Read the CSV
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        # Ensure required columns exist
        required_cols = ['Card color(s)', 'Card Text', 'Mana Cost', 'Power/Toughness']
        for col in required_cols:
            if col not in fieldnames:
                fieldnames.append(col)
        
        print(f"\n🃏 Starting Magic Card List Update")
        print(f"📄 File: {self.csv_file}")
        print(f"📊 Total cards: {len(rows)}\n")
        
        updated_count = 0
        
        # Process each row
        for idx, row in enumerate(rows, 1):
            card_name = row.get('Name', '').strip()
            
            if not card_name:
                print(f"Row {idx}: ⚠️  Empty card name, skipping...")
                continue
            
            # Check if row needs updating
            needs_update = any(not row.get(col, '').strip() for col in required_cols)
            
            if not needs_update:
                print(f"Row {idx}: '{card_name}' - Already complete ✓")
                continue
            
            print(f"\nRow {idx}: Processing '{card_name}'...")
            
            # Search Scryfall
            card_data = self.search_scryfall(card_name)
            
            if not card_data:
                print(f"  ❌ Could not find card data")
                continue
            
            # Extract information
            extracted = self.extract_card_data(card_data)
            scryfall_url = card_data.get('scryfall_uri', '')
            
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
            verified = self.verify_with_gemini(card_name, extracted, scryfall_url)
            
            if verified:
                print(f"  ✅ Updated successfully")
                updated_count += 1
            else:
                print(f"  ⚠️  Updated but verification had concerns")
                updated_count += 1
            
            # Rate limiting (be nice to APIs)
            time.sleep(0.1)
        
        # Write updated data back to CSV
        with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"\n{'='*50}")
        print(f"✅ Update complete!")
        print(f"📊 Updated {updated_count} cards")
        print(f"💾 Saved to {self.csv_file}")
        print(f"{'='*50}\n")


def main():
    # Load environment variables from .env file in parent directory
    load_dotenv(dotenv_path="../.env")
    
    # Configuration
    CSV_FILE = "../collection/ATLA.csv"  # CSV is in collection directory
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    if not GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY environment variable not set!")
        print("Please create a .env file with: GEMINI_API_KEY=your-key-here")
        return
    
    # Check if CSV exists
    if not os.path.exists(CSV_FILE):
        print(f"❌ Error: File '{CSV_FILE}' not found!")
        print("Please update the CSV_FILE variable with your file path.")
        return
    
    # Initialize updater
    updater = MagicCardUpdater(CSV_FILE, GEMINI_API_KEY)
    
    # Run the update
    updater.update_csv()


if __name__ == "__main__":
    main()