import requests
from bs4 import BeautifulSoup
import time
import csv
import json
from datetime import datetime

class PoliteScraper:
    def __init__(self):
        """Initialize the scraper with polite settings"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.delay = 1  # 1 second delay between requests
        self.data = []
    
    def fetch_page(self, url):
        """
        Fetch a page with proper headers and error handling
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  # Raise exception for bad status codes
            print(f"✅ Successfully fetched: {url}")
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def parse_quotes(self, html):
        """
        Parse quotes from the HTML using BeautifulSoup
        """
        soup = BeautifulSoup(html, 'html.parser')
        quotes = []
        
        # Find all quote blocks on the page
        quote_elements = soup.find_all('div', class_='quote')
        
        for element in quote_elements:
            quote_text = element.find('span', class_='text')
            author = element.find('small', class_='author')
            tags = element.find('div', class_='tags')
            
            if quote_text and author:
                quote = {
                    'text': quote_text.text.strip(),
                    'author': author.text.strip(),
                    'tags': []
                }
                
                # Extract tags if they exist
                if tags:
                    tag_elements = tags.find_all('a', class_='tag')
                    for tag in tag_elements:
                        quote['tags'].append(tag.text.strip())
                
                quotes.append(quote)
        
        return quotes
    
    def scrape_quotes_page(self, url):
        """
        Scrape quotes from a single page
        """
        html = self.fetch_page(url)
        if html:
            quotes = self.parse_quotes(html)
            self.data.extend(quotes)
            print(f"📝 Scraped {len(quotes)} quotes from {url}")
            return len(quotes)
        return 0
    
    def scrape_multiple_pages(self, base_url, num_pages=5):
        """
        Scrape multiple pages with delays
        """
        print(f"🔄 Starting to scrape {num_pages} pages...")
        
        for page_num in range(1, num_pages + 1):
            url = f"{base_url}page/{page_num}/"
            print(f"\n📄 Scraping page {page_num}...")
            
            count = self.scrape_quotes_page(url)
            if count == 0:
                print(f"⚠️ No quotes found on page {page_num}, stopping...")
                break
            
            # Polite delay between requests
            if page_num < num_pages:
                print(f"⏳ Waiting {self.delay} second(s) before next request...")
                time.sleep(self.delay)
        
        print(f"\n✅ Total quotes scraped: {len(self.data)}")
        return self.data
    
    def save_to_csv(self, filename='quotes.csv'):
        """
        Save scraped data to CSV file
        """
        if not self.data:
            print("⚠️ No data to save!")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['quote', 'author', 'tags'])
            
            for item in self.data:
                tags_str = ', '.join(item['tags']) if item['tags'] else ''
                writer.writerow([item['text'], item['author'], tags_str])
        
        print(f"💾 Data saved to {filename}")
    
    def save_to_json(self, filename='quotes.json'):
        """
        Save scraped data to JSON file
        """
        if not self.data:
            print("⚠️ No data to save!")
            return
        
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=2, ensure_ascii=False)
        
        print(f"💾 Data saved to {filename}")
    
    def print_summary(self):
        """
        Print a summary of what was scraped
        """
        if not self.data:
            print("⚠️ No data collected!")
            return
        
        # Get top authors
        authors = {}
        for item in self.data:
            author = item['author']
            authors[author] = authors.get(author, 0) + 1
        
        top_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)[:3]
        
        print("\n" + "="*50)
        print("📊 SCRAPING SUMMARY")
        print("="*50)
        print(f"Total quotes scraped: {len(self.data)}")
        print(f"Number of authors: {len(authors)}")
        print(f"\n🏆 Top 3 Authors:")
        for author, count in top_authors:
            print(f"   {author}: {count} quotes")
        print("="*50)


def main():
    """
    Main function to run the scraper
    """
    print("🕷️ Starting Polite Scraper...")
    print("="*50)
    
    # Create scraper instance
    scraper = PoliteScraper()
    
    # Target website (http://quotes.toscrape.com is a public scraper practice site)
    base_url = "http://quotes.toscrape.com/"
    
    # Scrape 3 pages (be polite!)
    print("🌐 Target: http://quotes.toscrape.com")
    print("📄 Pages to scrape: 3")
    print("⏳ Delay between requests: 1 second")
    print("="*50)
    
    # Start scraping
    scraper.scrape_multiple_pages(base_url, num_pages=3)
    
    # Save results
    if scraper.data:
        scraper.save_to_csv('quotes.csv')
        scraper.save_to_json('quotes.json')
        scraper.print_summary()
    
    print("\n✅ Scraping complete! Check the output files.")


if __name__ == "__main__":
    main()