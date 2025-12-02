import csv
import requests
import time
from typing import Dict, Optional

class CSVDataFixer:
    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        self.scryfall_api = "https://api.scryfall.com/cards/named"
    
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
    
    def fix_power_toughness(self, value: str) -> str:
        """Fix power/toughness that was formatted as date or convert slash to decimal"""
        if not value or value.strip() == '':
            return ''
        
        # If it looks like a date (e.g., "2-Jan"), we need to re-fetch from Scryfall
        # For now, return empty and let the main script refetch
        if '-' in value and any(month in value for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
            return ''  # Mark for re-fetch
        
        # If it's a number like "45659" (Excel date serial), mark for re-fetch
        if value.replace('.', '').isdigit() and len(value) > 3:
            return ''  # Mark for re-fetch
        
        # If it already has a slash, convert to decimal
        if '/' in value:
            parts = value.split('/')
            if len(parts) == 2:
                return f"{parts[0].strip()}.{parts[1].strip()}"
        
        return value
    
    def fix_card_text(self, card_name: str, current_text: str) -> str:
        """Re-fetch card text if it seems incomplete"""
        if not current_text or current_text.strip() == '':
            return ''  # Empty, will be re-fetched
        
        # If text seems very short (likely truncated), re-fetch
        if len(current_text) < 20 and not any(keyword in current_text.lower() for keyword in ['flying', 'haste', 'vigilance', 'reach', 'trample']):
            return ''  # Might be incomplete
        
        # Otherwise, fix newlines to use pipe separator
        if '\n' in current_text:
            return current_text.replace('\n', ' | ')
        
        return current_text
    
    def fix_csv(self):
        """Fix existing data in the CSV"""
        # Read the CSV
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        print(f"\n🔧 Fixing Existing Data in CSV")
        print(f"📄 File: {self.csv_file}")
        print(f"📊 Total cards: {len(rows)}\n")
        
        fixed_count = 0
        needs_refetch = []
        
        for idx, row in enumerate(rows, 1):
            card_name = row.get('Name', '').strip()
            if not card_name:
                continue
            
            fixed_something = False
            
            # Fix Power/Toughness
            pt_value = row.get('Power/Toughness', '')
            if pt_value:
                fixed_pt = self.fix_power_toughness(pt_value)
                if fixed_pt == '':
                    needs_refetch.append((idx, card_name, 'power/toughness'))
                    row['Power/Toughness'] = ''
                    fixed_something = True
                elif fixed_pt != pt_value:
                    row['Power/Toughness'] = fixed_pt
                    fixed_something = True
                    print(f"Row {idx}: Fixed P/T '{pt_value}' → '{fixed_pt}' for '{card_name}'")
            
            # Fix Card Text newlines
            card_text = row.get('Card Text', '')
            if card_text and '\n' in card_text:
                fixed_text = card_text.replace('\n', ' | ')
                row['Card Text'] = fixed_text
                fixed_something = True
                print(f"Row {idx}: Fixed card text formatting for '{card_name}'")
            
            if fixed_something:
                fixed_count += 1
        
        # Write fixed data back
        with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"\n{'='*50}")
        print(f"✅ Fix complete!")
        print(f"🔧 Fixed {fixed_count} cards")
        print(f"💾 Saved to {self.csv_file}")
        
        if needs_refetch:
            print(f"\n⚠️  {len(needs_refetch)} cards need data re-fetched:")
            print("   Run main.py again to fetch missing data")
        
        print(f"{'='*50}\n")


def main():
    CSV_FILE = "../collection/ATLA.csv"  # CSV is in collection directory
    
    fixer = CSVDataFixer(CSV_FILE)
    fixer.fix_csv()


if __name__ == "__main__":
    main()

