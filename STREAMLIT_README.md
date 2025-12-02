# 🃏 MTG Deck Builder - Streamlit Application

A modern web application for managing your Magic: The Gathering card collection and building optimized decks using AI.

## 🚀 Quick Start

### Run the Application

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 📋 Features

### 1. Card Collection Manager
- **Upload CSV**: Import your MTG card collection
- **Auto-Enhancement**: Fetch missing card data from Scryfall API
- **AI Verification**: Use Gemini AI to verify card data accuracy
- **Download**: Save your cleaned collection
- **Session Storage**: Use cleaned data directly in Deck Builder

### 2. Deck Builder
- **Flexible Input**: Use cleaned data or upload new CSV
- **Format Support**: Commander and Standard formats
- **Color Selection**: Choose specific color identities
- **Commander Selection**: Pick specific commanders or let AI choose
- **AI-Powered**: Gemini 2.5 Pro generates optimized decks
- **Knowledge-Based**: Uses strategy guides for better deck building
- **Upgrade Suggestions**: Get recommendations for cards to add to your collection

## 🎯 User Flow

### Recommended Workflow:
1. **Start at Card Collection Manager**
   - Upload your CSV file
   - Enable AI verification for best results
   - Process your collection
   - Download cleaned data (optional)

2. **Navigate to Deck Builder**
   - Select "Use Cleaned Data" tab
   - Choose deck format and colors
   - Add any specific preferences
   - Generate your deck
   - Download as Markdown

### Alternative Workflow:
- Skip directly to Deck Builder
- Upload CSV directly
- Build deck immediately

## 📊 CSV Format Requirements

### Required Columns:
- `Name` or `Card Name`: The card name

### Optional Columns (auto-populated if missing):
- `Card color(s)` or `Card Color(s)`: Card colors
- `Card Text`: Oracle text
- `Mana Cost`: Mana cost in MTG format
- `Power/Toughness`: For creatures
- `Is Fancy`: Mark special versions

### Example CSV:
```csv
Name,Card color(s),Mana Cost,Card Text,Power/Toughness,Is Fancy
Sol Ring,Colorless,{1},"{T}: Add {C}{C}.",,Yes
Lightning Bolt,Red,{R},"Lightning Bolt deals 3 damage to any target.",,No
```

## 🎨 UI/UX Highlights

### Card Collection Manager:
- **Two-Column Layout**: Upload/process on left, download/preview on right
- **Live Progress**: Real-time processing logs and progress bar
- **Data Preview**: See your data before and after processing
- **Session Persistence**: Cleaned data saved for use in Deck Builder

### Deck Builder:
- **Tabbed Input**: Clean separation between using cleaned data vs. uploading new
- **Visual Configuration**: Checkboxes for colors, clear format selection
- **Progress Tracking**: Real-time build log and progress indicators
- **Markdown Preview**: See your deck directly in the app
- **Easy Download**: One-click Markdown export

## ⚙️ Configuration

### Environment Variables:
Ensure your `.env` file contains:
```
GEMINI_API_KEY=your_api_key_here
```

### Knowledge Base:
Place strategy documents in:
- `knowledge/commander/` - Commander-specific guides
- `knowledge/standard/` - Standard-specific guides
- `knowledge/general/` - General deck building principles

Supported formats: `.txt`, `.md`

## 🛠️ Technical Details

### Technology Stack:
- **Framework**: Streamlit
- **AI Model**: Google Gemini 2.5 Pro (Deck Building), Gemini 2.5 Flash (Verification)
- **Data Source**: Scryfall API
- **Data Processing**: Pandas, CSV

### Session State Management:
- Cleaned CSV data persists across pages
- Generated decks stored for download
- No data lost when switching between pages

### Performance:
- **Data Cleaning**: ~0.1s per card + API rate limits
- **Deck Generation**: 30-60 seconds depending on collection size
- **Progress Tracking**: Real-time updates throughout

## 📱 Page Navigation

The app uses Streamlit's multi-page architecture:
- `app.py` - Landing page with instructions
- `pages/1_📋_Card_Collection_Manager.py` - Data cleaning
- `pages/2_🃏_Deck_Builder.py` - Deck generation

## 🎯 Best Practices

### For Best Results:
1. Clean your data first in Card Collection Manager
2. Enable AI verification for accuracy
3. Be specific in deck preferences
4. Review "Suggested Upgrades" to improve your collection

### Performance Tips:
- Larger collections take longer to process
- Use cleaned data in Deck Builder to avoid reprocessing
- Commander decks take longer to generate (100 cards vs 60)

## 🐛 Troubleshooting

### "GEMINI_API_KEY not found"
- Ensure `.env` file exists in the root directory
- Check that the key is correctly formatted
- Restart the Streamlit app after creating/modifying `.env`

### "No cards found matching color preference"
- Check your color selection
- Verify your CSV has proper color data
- Try using "Any" colors to see all cards

### Slow Performance
- Scryfall API has rate limits (100ms delay between requests)
- Large collections take time to process
- Deck generation with Gemini can take 30-60 seconds

## 📄 License

This application uses:
- Scryfall API (free tier)
- Google Gemini API (requires API key)
- Streamlit (open source)

## 🤝 Support

For issues or questions:
1. Check the "Help" sections in each page
2. Review this README
3. Check your `.env` configuration
4. Verify CSV format matches requirements

