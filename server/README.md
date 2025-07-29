# Crossword Server & Web Scraping Setup

## Database Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Migrate CSV Data to database (one-time)
```bash
python3 migrate_csv.py
```
This will transfer the existing `xword_modern_data.csv` (containing 500 most popular answers and their clues) to the SQLite database.

### 3. Start the server
```bash
python3 main.py
```
Then visit `http://localhost:8080/api/words/ERA` to test the API.

## XWord Info Scraper
The scraper is configured to scrape from [XWord Info](https://www.xwordinfo.com/), which provides high-quality NYT crossword data.

**Features:**
- Scrapes from URL pattern: `https://www.xwordinfo.com/Crossword?date=7/22/2025`
- Extracts answers of the day and writes to db all past clues for those answers
- Handles duplicate detection automatically

### To run scraper on today's date:
```bash
python3 scraper.py
```