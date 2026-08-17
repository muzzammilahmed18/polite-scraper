import os
import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
from urllib.parse import urljoin
from pydantic import BaseModel, ValidationError, HttpUrl
from typing import Optional, List
import re

# ========== CONFIGURATION ==========
BASE_URL = "http://books.toscrape.com"
CATALOGUE_URL = f"{BASE_URL}/catalogue/"
PAGES_TO_SCRAPE = 3
DELAY = 0.5  # seconds between requests
TIMEOUT = 10  # seconds
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/muzzammilahmed18/polite-scraper)"

# ========== CACHE SETUP ==========
CACHE_DIR = "cache"
OUTPUT_DIR = "output"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========== PYDANTIC SCHEMA ==========
class BookRecord(BaseModel):
    """Schema for validated book records"""
    title: str
    product_url: str  # Changed from HttpUrl to str for serialization
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: Optional[str] = None
    source_page: str  # Changed from HttpUrl to str
    fetched_at: str

# ========== HELPER FUNCTIONS ==========

def fetch_page(url, use_cache=True):
    """
    Fetch a page with polite caching
    Returns: HTML content or None
    """
    # Create cache filename from URL
    cache_filename = url.replace("http://", "").replace("https://", "").replace("/", "_") + ".html"
    cache_path = os.path.join(CACHE_DIR, cache_filename)
    
    # Check cache first
    if use_cache and os.path.exists(cache_path):
        print(f"📦 CACHE HIT: {url}")
        with open(cache_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Fetch from network
    print(f"🌐 FETCH: {url}")
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        
        # Save to cache
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

def extract_books_from_catalogue(html, page_url):
    """
    Extract book URLs from a catalogue page
    Returns: list of absolute URLs
    """
    soup = BeautifulSoup(html, 'html.parser')
    book_urls = []
    
    # Find all book links on the page
    articles = soup.find_all('article', class_='product_pod')
    for article in articles:
        link = article.find('a')
        if link and link.get('href'):
            relative_url = link.get('href')
            # Convert relative URL to absolute
            absolute_url = urljoin(page_url, relative_url)
            book_urls.append(absolute_url)
    
    return book_urls

def get_next_page_url(html, current_url):
    """
    Find the 'next' page link
    Returns: absolute URL or None
    """
    soup = BeautifulSoup(html, 'html.parser')
    next_link = soup.find('a', string='next')
    if next_link and next_link.get('href'):
        return urljoin(current_url, next_link.get('href'))
    return None

def extract_book_details(html, page_url):
    """
    Extract all required fields from a book page
    Returns: dict with raw data
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Title
    title = soup.find('h1')
    title_text = title.text.strip() if title else "Unknown Title"
    
    # Price
    price = soup.find('p', class_='price_color')
    price_text = price.text.strip() if price else "£0.00"
    # Extract number from price (remove £ and convert to float)
    price_match = re.search(r'[\d.]+', price_text)
    price_gbp = float(price_match.group()) if price_match else 0.0
    
    # Availability
    availability = soup.find('p', class_='instock availability')
    availability_text = availability.text.strip() if availability else "Out of stock"
    
    # Rating
    rating = soup.find('p', class_='star-rating')
    rating_text = rating.get('class')[1] if rating and len(rating.get('class', [])) > 1 else "No rating"
    
    # Description
    description_div = soup.find('div', id='product_description')
    description = None
    if description_div:
        description_p = description_div.find_next('p')
        if description_p:
            description = description_p.text.strip()
    
    return {
        "title": title_text,
        "product_url": page_url,
        "price_text": price_text,
        "price_gbp": price_gbp,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": page_url,
        "fetched_at": datetime.now().isoformat()
    }

def validate_book(book_data):
    """
    Validate a book record against the schema
    Returns: (is_valid, record_or_error)
    """
    try:
        record = BookRecord(**book_data)
        return True, record.model_dump()
    except ValidationError as e:
        return False, str(e)

# ========== MAIN SCRAPER ==========

class PoliteScraper:
    def __init__(self):
        self.start_time = datetime.now()
        self.book_urls = []
        self.valid_records = []
        self.invalid_records = []
        self.failed_pages = []
        self.cache_hits = 0
        self.fetches = 0
        self.requests_made = 0
    
    def discover_catalogue_pages(self):
        """
        Stage 2: Discover all book URLs from first 3 pages
        """
        print("\n📚 DISCOVERING CATALOGUE PAGES")
        print("=" * 50)
        
        current_url = CATALOGUE_URL + "page-1.html"
        pages_collected = 0
        
        while pages_collected < PAGES_TO_SCRAPE:
            print(f"\n📄 Page {pages_collected + 1}: {current_url}")
            
            # Fetch the page
            html = fetch_page(current_url)
            if not html:
                self.failed_pages.append(current_url)
                break
            
            self.requests_made += 1
            
            # Extract book URLs
            book_urls = extract_books_from_catalogue(html, current_url)
            print(f"   Found {len(book_urls)} books on this page")
            self.book_urls.extend(book_urls)
            
            pages_collected += 1
            
            # Get next page URL
            if pages_collected < PAGES_TO_SCRAPE:
                next_url = get_next_page_url(html, current_url)
                if next_url:
                    current_url = next_url
                    time.sleep(DELAY)
                else:
                    break
        
        # Remove duplicates
        unique_urls = list(set(self.book_urls))
        self.book_urls = unique_urls
        print(f"\n✅ Total unique books found: {len(self.book_urls)}")
    
    def scrape_book_details(self):
        """
        Stage 3: Extract details from each book page
        """
        print("\n📖 SCRAPING BOOK DETAILS")
        print("=" * 50)
        
        for i, url in enumerate(self.book_urls, 1):
            print(f"\n[{i}/{len(self.book_urls)}] {url}")
            
            # Fetch the page
            html = fetch_page(url)
            if not html:
                self.failed_pages.append(url)
                continue
            
            self.requests_made += 1
            
            # Extract details
            raw_data = extract_book_details(html, url)
            
            # Validate against schema
            is_valid, result = validate_book(raw_data)
            
            if is_valid:
                self.valid_records.append(result)
                print(f"   ✅ Valid: {raw_data['title']} (£{raw_data['price_gbp']})")
            else:
                self.invalid_records.append({
                    "url": url,
                    "error": result,
                    "raw_data": raw_data
                })
                print(f"   ❌ Invalid: {raw_data['title']} - {result}")
            
            # Polite delay
            if i < len(self.book_urls):
                time.sleep(DELAY)
    
    def test_broken_url(self):
        """
        Stage 5: Test that one bad URL doesn't crash the run
        """
        print("\n🧪 TESTING BROKEN URL HANDLING")
        print("=" * 50)
        
        # Add one fake URL to test failure handling
        fake_url = "http://books.toscrape.com/catalogue/nonexistent.html"
        self.book_urls.append(fake_url)
        print(f"   Added fake URL: {fake_url}")
        print("   This should be logged and skipped...")
        
        # Try to scrape it
        html = fetch_page(fake_url)
        if not html:
            self.failed_pages.append(fake_url)
            print("   ✅ Broken URL handled gracefully")
        
        # Remove fake URL for final count
        self.book_urls.remove(fake_url)
        print("   ✅ Removed fake URL from list")
    
    def generate_run_report(self):
        """
        Stage 5: Generate run report
        """
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report = {
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "pages_processed": len(self.book_urls),
            "cache_hits": self.cache_hits,
            "fetches": self.fetches,
            "requests_made": self.requests_made,
            "valid_records": len(self.valid_records),
            "invalid_records": len(self.invalid_records),
            "failed_pages": len(self.failed_pages),
            "failed_urls": self.failed_pages[:10]
        }
        
        # Save report
        report_path = os.path.join(OUTPUT_DIR, "run-report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print("\n📊 RUN REPORT")
        print("=" * 50)
        print(f"Duration: {duration:.2f}s")
        print(f"Books processed: {len(self.book_urls)}")
        print(f"✅ Valid records: {len(self.valid_records)}")
        print(f"❌ Invalid records: {len(self.invalid_records)}")
        print(f"💀 Failed pages: {len(self.failed_pages)}")
        print(f"📦 Cache hits: {self.cache_hits}")
        print(f"💾 Report saved to: {report_path}")
        
        return report
    
    def save_records(self):
        """
        Save valid records to books.json and invalid records to errors.json
        """
        # Save valid records
        books_path = os.path.join(OUTPUT_DIR, "books.json")
        with open(books_path, 'w', encoding='utf-8') as f:
            json.dump(self.valid_records, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved {len(self.valid_records)} valid records to: {books_path}")
        
        # Save invalid records
        if self.invalid_records:
            errors_path = os.path.join(OUTPUT_DIR, "errors.json")
            with open(errors_path, 'w', encoding='utf-8') as f:
                json.dump(self.invalid_records, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(self.invalid_records)} invalid records to: {errors_path}")
    
    def run(self):
        """
        Main execution
        """
        print("🕷️  BOOKS TO SCRAPE - POLITE SCRAPER")
        print("=" * 50)
        print(f"📚 Target: Books to Scrape")
        print(f"📄 Pages: {PAGES_TO_SCRAPE}")
        print(f"⏳ Delay: {DELAY}s")
        print(f"🕐 Timeout: {TIMEOUT}s")
        print("=" * 50)
        
        # Stage 2: Discover pages
        self.discover_catalogue_pages()
        
        # Test broken URL
        self.test_broken_url()
        
        # Stage 3: Scrape details
        self.scrape_book_details()
        
        # Stage 5: Save records
        self.save_records()
        
        # Stage 5: Generate report
        self.generate_run_report()
        
        print("\n✅ SCRAPING COMPLETE!")

# ========== ENTRY POINT ==========

if __name__ == "__main__":
    scraper = PoliteScraper()
    scraper.run()