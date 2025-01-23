from typing import List, Dict, Any
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

from utils.logger import logger
from crawlers.base import BaseScraper, HumanScrollingMixin, SelectorMixin
from .config import SCRAPER_CONFIG

class QuinceScraper(BaseScraper, HumanScrollingMixin, SelectorMixin):
    def __init__(self, config: dict):
        super().__init__(config)
        logger.info("Initializing QuinceScraper")
        logger.debug(f"Scraper configuration: {config}")

    def open_page(self, url: str) -> None:
        """Open the URL using configured browser."""
        logger.info(f"Opening page: {url}")
        self.driver = self.setup_driver()
        self.driver.get(url)
        time.sleep(random.uniform(2.0, 4.0))
        logger.debug("Page loaded successfully")

    def scroll_page(self) -> None:
        """Scroll down the page using human-like behavior."""
        logger.debug("Starting page scroll")
        self.human_like_scroll(self.driver)
        logger.debug("Page scroll completed")

    def extract_items(self, items_limit: int = None) -> List[Dict[str, Any]]:
        """
        Extract product information from the current page.
        
        Args:
            items_limit: Maximum number of items to extract (optional)
        """
        logger.info("Starting item extraction")
        all_items_data = []
        seen_product_ids = set()
        no_change_count = 0
        max_no_change = 3
        
        while True:
            # Check limit before scrolling
            logger.debug(f"Checking limit - Current items: {len(all_items_data)}, Limit: {items_limit}")
            if items_limit and len(all_items_data) >= items_limit:
                logger.info(f"Reached items limit of {items_limit}")
                return all_items_data

            # Get initial item count
            items_before = len(self.driver.find_elements(By.CSS_SELECTOR, self.config["selectors"]["product_item"]))
            
            # Scroll to load more content
            self.scroll_page()
            time.sleep(random.uniform(2.0, 3.0))
            
            # Check if new items were loaded
            items_after = len(self.driver.find_elements(By.CSS_SELECTOR, self.config["selectors"]["product_item"]))
            if items_after == items_before:
                no_change_count += 1
                logger.info(f"No new items loaded after scroll {no_change_count}/{max_no_change}")
                if no_change_count >= max_no_change:
                    logger.info("No more items to load")
                    break
            else:
                no_change_count = 0
                logger.debug(f"Found {items_after - items_before} newly loaded items")
            
            # Extract items from current page
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find all product items
            items = soup.select(self.config["selectors"]["product_item"])
            logger.debug(f"Found {len(items)} items in current view")
            
            for item in items:
                if items_limit and len(all_items_data) >= items_limit:
                    logger.info(f"Reached items limit of {items_limit}")
                    return all_items_data
                    
                try:
                    product_info = self.extract_product_info(
                        item, 
                        self.config["selectors"],
                        self.config
                    )
                    
                    if product_info:
                        if 'product_item' in product_info:
                            del product_info['product_item']
                        product_id = product_info.get('store_product_id')
                        if product_id and product_id not in seen_product_ids:
                            seen_product_ids.add(product_id)
                            all_items_data.append(product_info)
                            logger.debug(f"Current items count: {len(all_items_data)}")
                            
                except Exception as e:
                    logger.error(f"Error extracting item: {e}")
                    continue
            
            logger.info(f"Total items extracted: {len(all_items_data)}")
        
        return all_items_data

    def clean_price(self, price: str) -> str:
        """Clean price string to remove currency symbol and whitespace."""
        if price:
            return price.replace('$', '').strip()
        return ''

    def has_next_page(self) -> bool:
        """
        Check if there is a next page.
        For Quince, we don't need this since it uses infinite scroll.
        """
        return False  # Always return False since we handle everything through scrolling

    def go_to_next_page(self) -> None:
        """
        Go to next page.
        For Quince, we don't need this since it uses infinite scroll.
        """
        pass  # No-op since we handle everything through scrolling

def get_scraper(config=None):
    """Factory function to create a QuinceScraper instance."""
    logger.info("Creating new QuinceScraper instance")
    if config is None:
        config = SCRAPER_CONFIG
        logger.debug("Using default scraper configuration")
    return QuinceScraper(config)
