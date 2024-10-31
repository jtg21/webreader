import re
import os
import json
import asyncio
import logging

from urllib.parse import urljoin, urlparse
from typing import Dict, Set, Optional
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    os.system('playwright install')
    os.system('playwright install-deps')

class WebsiteReader:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited_urls: Set[str] = set()
        self.content_data: Dict[str, Dict] = {}
        
    async def extract_text_content(self, page: Page, url: str) -> Dict:
        """Extract meaningful text content from the page."""
        # Wait for the content to load
        await page.wait_for_load_state('domcontentloaded')
        
        # Get text content from important elements
        content = {
            'title': await page.title(),
            'headings': list(set(await page.eval_on_selector_all('h1, h2, h3', """
                elements => elements.map(e => e.textContent.trim()).filter(text => text.length > 0)
            """))),
            'paragraphs': list(set(await page.eval_on_selector_all('p', """
                elements => elements.map(e => e.textContent.trim()).filter(text => text.length > 0)
            """))),
            'lists': list(set(await page.eval_on_selector_all('ul, ol', """
                elements => elements.map(e => e.textContent.trim()).filter(text => text.length > 0)
            """)))
        }
        
        return content

    async def get_valid_links(self, page: Page) -> Set[str]:
        """Get all valid internal links from the current page."""
        links = await page.eval_on_selector_all('a[href]', 'elements => elements.map(e => e.href)')
        valid_links = set()
        
        for link in links:
            # Ensure link is from the same domain
            if self.domain in link and '#' not in link:
                # Remove query parameters and fragments
                clean_link = re.sub(r'\?.*$', '', link)
                if clean_link not in self.visited_urls:
                    valid_links.add(clean_link)
        
        return valid_links

    async def crawl_page(self, page: Page, url: str, max_depth: int = 2, current_depth: int = 0):
        """Crawl a single page and its links up to max_depth."""
        if current_depth >= max_depth or url in self.visited_urls:
            return

        start_time = datetime.now()
        logging.info(f"Starting crawl of {url} at depth {current_depth}")

        try:
            # Add timeout and catch navigation errors
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            self.visited_urls.add(url)
            
            try:
                # Extract content with timeout and error handling
                content = await asyncio.wait_for(
                    self.extract_text_content(page, url),
                    timeout=30.0
                )
                self.content_data[url] = content
                logging.info(f"Successfully extracted content from {url} ({len(content.get('paragraphs', []))} paragraphs)")
                
                # Get valid links with timeout and error handling
                valid_links = await asyncio.wait_for(
                    self.get_valid_links(page),
                    timeout=30.0
                )
                logging.info(f"Found {len(valid_links)} valid links on {url}")
                
                for link in valid_links:
                    await self.crawl_page(page, link, max_depth, current_depth + 1)
                    
            except asyncio.TimeoutError:
                logging.error(f"Timeout while processing content for {url} after {(datetime.now() - start_time).total_seconds():.1f}s")
            except Exception as e:
                logging.error(f"Error extracting content from {url}: {str(e)}", exc_info=True)
                
        except Exception as e:
            logging.error(f"Error navigating to {url}: {str(e)}", exc_info=True)
            # Add the URL to visited to prevent retries
            self.visited_urls.add(url)
        finally:
            duration = (datetime.now() - start_time).total_seconds()
            logging.info(f"Finished processing {url} in {duration:.1f}s")

    async def read_website(self, max_depth: int = 3, output_file: str = 'website_content.json'):
        """Main method to read website content."""
        # Add logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        logging.info(f"Starting website crawl of {self.base_url} with max_depth={max_depth}")
        start_time = datetime.now()
        
        async with async_playwright() as playwright:
            browser: Browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await self.crawl_page(page, self.base_url, max_depth)
                
                # Save the collected data to a JSON file
                # with open(output_file, 'w', encoding='utf-8') as f:
                #     json.dump(self.content_data, f, indent=2, ensure_ascii=False)
                
                duration = (datetime.now() - start_time).total_seconds()
                logging.info(f"Crawl completed in {duration:.1f}s. Processed {len(self.visited_urls)} pages.")
                logging.info(f"Results saved to {output_file}")
                
            finally:
                await browser.close()

def read_website(url: str, max_depth: int = 3, output_file: Optional[str] = None):
    """Convenience function to run the website reader."""
    if output_file is None:
        output_file = f"data/{url.replace('https://', '').replace('/', '_')}_content.json"
    
    reader = WebsiteReader(url)
    asyncio.run(reader.read_website(max_depth, output_file))
    return reader.content_data

if __name__ == "__main__":
    # Example usage
    website_url = "https://humansignal.com/"
    content_data = read_website(website_url, max_depth=3)

