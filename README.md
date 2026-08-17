# 🕷️ The Polite Scraper - Books to Scrape

A polite web scraper that extracts book data from **Books to Scrape** - a practice sandbox for learning web scraping.

## 🎯 Target Classification

- **Site:** [Books to Scrape](http://books.toscrape.com)
- **Type:** Practice sandbox for scraping (explicitly allowed for learning)
- **Scope:** First 3 catalogue pages (60 books total)
- **Data collected:** Title, price, availability, rating, description, source URL, fetch time
- **robots.txt:** Checked - the site allows educational scraping
- **Permission:** Site explicitly states it exists for people to practice scraping

## 📚 What It Scrapes

| Field | Description | Example |
|-------|-------------|---------|
| `title` | Book title | "A Light in the Attic" |
| `product_url` | Full book URL | http://books.toscrape.com/... |
| `price_text` | Raw price text | "£51.77" |
| `price_gbp` | Price as number | 51.77 |
| `availability_text` | Stock status | "In stock (22 available)" |
| `rating_text` | Star rating | "Three" |
| `description` | Book description | "...a collection of poems..." |
| `source_page` | Where it was found | http://books.toscrape.com/... |
| `fetched_at` | Timestamp of fetch | 2026-08-17T10:00:00Z |

## 🛠️ Technologies

| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Programming language |
| **Requests** | HTTP requests with timeout & user-agent |
| **BeautifulSoup4** | HTML parsing and extraction |
| **Pydantic** | Data validation and schema enforcement |
| **lxml** | Fast HTML parser |

## 📂 Project Structure
polite-scraper/
├── scraper.py # Main scraping script
├── requirements.txt # Python dependencies
├── README.md # Documentation
├── .gitignore # Git ignore rules
├── cache/ # Cached HTML files (not in repo)
└── output/
├── books.json # 60 validated book records
├── run-report.json # Run statistics
└── errors.json # Invalid records (if any)

text

## 🔧 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/muzzammilahmed18/polite-scraper.git
cd polite-scraper
Step 2: Create Virtual Environment
Windows:

bash
python -m venv venv
venv\Scripts\activate
Mac/Linux:

bash
python3 -m venv venv
source venv/bin/activate
Step 3: Install Dependencies
bash
pip install -r requirements.txt
Step 4: Run the Scraper
bash
python scraper.py
📊 Sample Output
text
🕷️  BOOKS TO SCRAPE - POLITE SCRAPER
==================================================
📚 Target: Books to Scrape
📄 Pages: 3
⏳ Delay: 0.5s
🕐 Timeout: 10s
==================================================

📚 DISCOVERING CATALOGUE PAGES
==================================================

📄 Page 1: http://books.toscrape.com/catalogue/page-1.html
🌐 FETCH: http://books.toscrape.com/catalogue/page-1.html
   Found 20 books on this page

📄 Page 2: http://books.toscrape.com/catalogue/page-2.html
🌐 FETCH: http://books.toscrape.com/catalogue/page-2.html
   Found 20 books on this page

📄 Page 3: http://books.toscrape.com/catalogue/page-3.html
🌐 FETCH: http://books.toscrape.com/catalogue/page-3.html
   Found 20 books on this page

✅ Total unique books found: 60

📖 SCRAPING BOOK DETAILS
==================================================
[1/60] http://books.toscrape.com/catalogue/...
   ✅ Valid: A Light in the Attic (£51.77)
...
💾 Saved 60 valid records to: output/books.json

📊 RUN REPORT
==================================================
Duration: 35.62s
Books processed: 60
✅ Valid records: 60
❌ Invalid records: 0
💀 Failed pages: 1
📊 Sample Run Report
json
{
  "start_time": "2026-08-17T16:30:00.123456",
  "end_time": "2026-08-17T16:30:35.789012",
  "duration_seconds": 35.62,
  "pages_processed": 60,
  "cache_hits": 0,
  "fetches": 0,
  "requests_made": 64,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1,
  "failed_urls": [
    "http://books.toscrape.com/catalogue/nonexistent.html"
  ]
}
📁 Output Files
File	Description
output/books.json	60 validated book records
output/run-report.json	Run statistics and performance
output/errors.json	Invalid records (empty if all valid)
🤝 Scraping Ethics & Politeness
This scraper follows best practices:

✅ User-Agent header - Identifies itself with contact info

✅ 0.5 second delay between requests - Doesn't hammer the server

✅ Timeout set to 10 seconds - Never waits forever

✅ Cache system - Saves HTML locally to avoid re-fetching

✅ Error handling - One bad page never crashes the run

✅ Respects robots.txt - Only scrapes allowed paths

✅ Status code check - Only processes 200 OK responses

✅ Idempotent - Running twice produces same 60 records

✅ Assignment Requirements Met
☑ Target: Books to Scrape sandbox
☑ 3 catalogue pages discovered
☑ 60 unique books found
☑ 8 raw fields extracted per book
☑ Price converted to number (price_gbp)
☑ Pydantic schema validation
☑ Cache system implemented
☑ Broken URL handled gracefully
☑ run-report.json generated
☑ errors.json created (empty)
☑ 7+ meaningful commits
☑ README with target classification
⚠️ Important Note
Never use this code on another site without checking its rules, robots.txt, and terms of service first! This scraper is designed specifically for the Books to Scrape practice sandbox.

👨‍💻 Author
Muzzammil Ahmed

📄 License
MIT License - For learning purposes only. Use responsibly.