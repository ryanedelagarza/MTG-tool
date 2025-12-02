# 🃏 MTG Deck Builder

An AI-powered web application for managing your Magic: The Gathering card collection and building optimized decks.

## ✨ Features

### 📋 Card Collection Manager
- Upload your MTG card collection CSV
- Automatically fetch missing card data from Scryfall API
- AI-powered data verification with Google Gemini
- Auto-add missing columns to your CSV
- Clean and standardize card data

### 🃏 Deck Builder
- Build optimized Commander and Standard format decks
- AI-powered deck generation using Google Gemini 2.5 Pro
- Color identity filtering
- Strategy-based deck building using knowledge base
- Get upgrade suggestions for cards not in your collection
- Export decks as Markdown

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ryanedelagarza/MTG-tool.git
cd MTG-tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```
GEMINI_API_KEY=your_api_key_here
```

4. Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Alternative: Use the batch file (Windows)
```bash
run_app.bat
```

## 📊 CSV Format

Your card collection CSV needs at minimum:
- `Name` or `Card Name` column

All other columns will be automatically added and populated:
- `Card color(s)` - Card colors
- `Card Text` - Oracle text
- `Mana Cost` - Mana cost
- `Power/Toughness` - Creature stats

### Example Minimal CSV
```csv
Name
Sol Ring
Lightning Bolt
Forest
Aang, Avatar
```

## 📁 Project Structure

```
MTG-tool/
├── app.py                              # Main Streamlit app
├── pages/
│   ├── 1_📋_Card_Collection_Manager.py # Data cleaning interface
│   └── 2_🃏_Deck_Builder.py            # Deck building interface
├── knowledge/
│   ├── commander/                      # Commander strategy guides
│   └── standard/                       # Standard strategy guides
├── collection/                         # Your card collection
├── deck_builder.py                     # CLI deck builder
├── data_clean/                         # CLI data cleaning tools
└── requirements.txt                    # Python dependencies
```

## 🎮 How to Use

### Workflow 1: Full Process
1. Navigate to **Card Collection Manager**
2. Upload your CSV file
3. Enable AI verification (optional)
4. Process your collection
5. Navigate to **Deck Builder**
6. Select "Use Cleaned Data"
7. Configure your deck (format, colors, preferences)
8. Generate deck
9. Download as Markdown

### Workflow 2: Quick Build
1. Navigate to **Deck Builder**
2. Upload CSV directly
3. Configure and generate deck

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI Models**: 
  - Google Gemini 2.5 Pro (Deck Building)
  - Google Gemini 2.5 Flash (Data Verification)
- **Data Source**: Scryfall API
- **Data Processing**: Pandas, CSV

## 📖 Documentation

- [Streamlit App Guide](STREAMLIT_README.md) - Detailed app usage
- [Architecture Guide](APP_STRUCTURE.md) - Technical architecture and UI/UX design

## 🔒 Security

- Never commit your `.env` file
- Keep your Gemini API key private
- The `.gitignore` is configured to exclude sensitive files

## 🤝 Contributing

This is a personal project, but feel free to fork and customize for your own use!

## 📝 License

This project uses:
- [Scryfall API](https://scryfall.com/docs/api) (free tier)
- [Google Gemini API](https://ai.google.dev/) (requires API key)
- [Streamlit](https://streamlit.io/) (open source)

## 🎯 Features in Development

- [ ] Deck comparison tools
- [ ] Collection statistics dashboard
- [ ] Multiple deck format export (TXT, JSON)
- [ ] Deck sharing capabilities
- [ ] Advanced filtering and search

## 🐛 Troubleshooting

### "GEMINI_API_KEY not found"
- Ensure `.env` file exists in root directory
- Verify the key is correctly formatted
- Restart the app after creating/modifying `.env`

### Slow Performance
- Scryfall API has rate limits (100ms delay between requests)
- Large collections take time to process
- Deck generation can take 30-60 seconds

## 📧 Contact

For issues or questions, please open an issue on GitHub.

---

Built with ❤️ for MTG players who love data and AI

