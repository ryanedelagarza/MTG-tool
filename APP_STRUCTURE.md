# 🏗️ Streamlit App Structure

## File Organization

```
Code/
├── app.py                              # Main landing page
├── .env                                # API key configuration (not in git)
├── requirements.txt                    # Python dependencies
├── run_app.bat                         # Quick start script
├── STREAMLIT_README.md                 # Streamlit app documentation
│
├── .streamlit/
│   └── config.toml                     # Streamlit theme configuration
│
├── pages/
│   ├── 1_📋_Card_Collection_Manager.py # Data cleaning page
│   └── 2_🃏_Deck_Builder.py            # Deck generation page
│
├── knowledge/
│   ├── commander/                      # Commander strategy guides (.md, .txt)
│   └── standard/                       # Standard strategy guides (.md, .txt)
│
├── collection/
│   └── ATLA.csv                        # Your card collection
│
├── deck_builder.py                     # CLI deck builder (original)
└── data_clean/
    ├── main.py                         # CLI data cleaner
    ├── test_run.py                     # Test script
    └── fix_existing_data.py            # Data fix utility
```

## Page Flow

### 🏠 Landing Page (app.py)
```
┌─────────────────────────────────────┐
│  MTG Deck Builder Welcome           │
│  ─────────────────────────────────  │
│  Overview of features               │
│  Navigation instructions            │
│  Getting started guide              │
└─────────────────────────────────────┘
```

### 📋 Page 1: Card Collection Manager
```
┌──────────────────────┬──────────────┐
│  Upload CSV          │  Download    │
│  ─────────────────   │  ──────────  │
│  • File uploader     │  • Status    │
│  • Preview data      │  • Download  │
│  • AI verification   │    button    │
│  • Process button    │  • Preview   │
│                      │    cleaned   │
│  ─────────────────   │              │
│  Processing Log      │              │
│  • Progress bar      │              │
│  • Live updates      │              │
└──────────────────────┴──────────────┘
```

**Features:**
- Upload CSV with card collection
- Fetch missing data from Scryfall API
- Optional AI verification with Gemini
- Real-time progress tracking
- Download cleaned CSV
- Store in session state for Deck Builder

**User Flow:**
1. Upload CSV → 2. Enable AI → 3. Process → 4. Download/Use in Deck Builder

### 🃏 Page 2: Deck Builder
```
┌─────────────────────────────────────┐
│  Select Collection                  │
│  ─────────────────────────────────  │
│  [Use Cleaned Data] [Upload New]    │
│  • Session state   • File upload    │
│  • Preview         • Preview         │
└─────────────────────────────────────┘
         ↓
┌──────────────────┬──────────────────┐
│  Configuration   │  Color Selection │
│  ──────────────  │  ──────────────  │
│  • Format        │  ☐ White         │
│  • Commander     │  ☐ Blue          │
│    (optional)    │  ☐ Black         │
│                  │  ☐ Red           │
│  • Notes         │  ☐ Green         │
└──────────────────┴──────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Generate Deck                      │
│  ─────────────────────────────────  │
│  • Progress tracking                │
│  • Build log                        │
│  • Status updates                   │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Results                            │
│  ─────────────────────────────────  │
│  • Deck preview (Markdown)          │
│  • Download button                  │
│  • Card type summary                │
│  • Suggested upgrades               │
└─────────────────────────────────────┘
```

**Features:**
- Flexible input (cleaned data or upload)
- Format selection (Commander/Standard)
- Color identity selection (checkboxes)
- Optional commander specification
- Additional preferences (text area)
- AI-powered deck generation
- Real-time progress tracking
- Markdown preview
- One-click download

**User Flow:**
1. Select Collection → 2. Configure Deck → 3. Generate → 4. Download

## Data Flow

### Session State Variables
```python
st.session_state = {
    'cleaned_csv': str,           # CSV content from Card Manager
    'cleaned_csv_name': str,      # Filename of cleaned CSV
    'generated_deck': str,        # Generated deck (Markdown)
    'deck_filename': str          # Filename for download
}
```

### Inter-Page Communication
```
Card Collection Manager
    ↓ (stores in session_state.cleaned_csv)
Deck Builder
    → Reads session_state.cleaned_csv
    → Uses data for deck building
    → No need to re-upload or re-clean
```

## UI/UX Considerations

### 🎨 Design Principles

1. **Progressive Disclosure**
   - Show only relevant options based on selections
   - Expandable sections for advanced features
   - Help sections collapsed by default

2. **Clear Visual Hierarchy**
   - Numbered steps (1️⃣, 2️⃣, 3️⃣)
   - Consistent headers and sections
   - Color-coded status messages (✅, ❌, ⚠️)

3. **Responsive Feedback**
   - Progress bars for long operations
   - Real-time logs during processing
   - Status messages for user actions
   - Success confirmations

4. **Error Prevention**
   - Validation before processing
   - Clear instructions and examples
   - Help sections on each page
   - Tooltips on complex options

5. **Efficiency**
   - Session state for data persistence
   - No unnecessary re-processing
   - One-click operations where possible
   - Batch operations

### 📱 Layout Patterns

**Two-Column Layout** (Card Collection Manager)
- Left: Input and processing
- Right: Output and download
- Separation of concerns

**Single-Column with Tabs** (Deck Builder - Input)
- Tab 1: Use existing data
- Tab 2: Upload new data
- Clear choice without clutter

**Progressive Disclosure** (Both Pages)
- Expandable previews
- Collapsible help sections
- Show details only when relevant

## Technical Features

### Session State Management
- Data persists across pages
- No database required
- Cleaned data reusable
- Generated decks stored

### Progress Tracking
- Real-time updates
- Progress bars
- Log messages
- Status indicators

### File Handling
- In-memory processing (StringIO)
- No temporary files
- Direct upload/download
- CSV validation

### Error Handling
- API key validation
- File format checks
- Graceful error messages
- Fallback options

### Performance
- Minimal API calls
- Efficient data processing
- Cached operations
- Rate limit compliance

## Color Scheme

**Theme Colors:**
- Primary: `#FF6B35` (Orange-Red) - CTAs, emphasis
- Background: `#0E1117` (Dark Blue-Grey) - Main background
- Secondary BG: `#262730` (Medium Grey) - Cards, containers
- Text: `#FAFAFA` (Off-White) - Primary text

**Status Colors:**
- Success: Green (✅)
- Error: Red (❌)
- Warning: Yellow (⚠️)
- Info: Blue (💡, 📊)

## Navigation

**Sidebar:**
- Always visible
- Page navigation
- API configuration info
- Contextual help

**Page Tabs:**
- Within pages for related content
- Clear visual separation
- No nested navigation

## Accessibility

- Clear labels on all inputs
- Help text and tooltips
- Status messages for screen readers
- Keyboard navigation support
- High contrast theme
- Large click targets

## Future Enhancements

Potential improvements:
- [ ] Save multiple deck versions
- [ ] Compare decks side-by-side
- [ ] Export to various formats (TXT, JSON)
- [ ] Deck statistics and analysis
- [ ] Collection statistics dashboard
- [ ] Card search and filtering
- [ ] Deck sharing via URL
- [ ] User accounts and deck history

