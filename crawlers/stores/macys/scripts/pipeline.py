from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

from utils.logger import logger
from crawlers.base import BaseScraper, HumanScrollingMixin, SelectorMixin
from .config import SCRAPER_CONFIG

class MacysScraper(BaseScraper, HumanScrollingMixin, SelectorMixin):
    def __init__(self, config: dict):
        super().__init__(config)
        logger.info("Initializing MacysScraper")
        logger.debug(f"Scraper configuration: {config}")

    def open_page(self, url: str) -> None:
        """Open the URL using configured browser."""
        logger.info(f"Opening page: {url}")
        self.driver = self.setup_driver()
        self.driver.get(url)
        time.sleep(random.uniform(2.0, 4.0))
        logger.debug("Page loaded successfully")
        
        # Handle any popups
        self.handle_popups()
        logger.debug("Popup handling completed")

    def scroll_page(self) -> None:
        """Scroll the page using human-like behavior."""
        logger.debug("Starting page scroll")
        if self.config["scroll_behavior"]["human_like"]:
            self.human_like_scroll(self.driver)
        time.sleep(random.uniform(1.5, 3.0))
        logger.debug("Page scroll completed")

    def click_next_page(self) -> bool:
        """Click the next page button."""
        try:
            next_button_selector = self.config["pagination"]["selectors"]["next_button"]["pattern"]
            wait = WebDriverWait(self.driver, 5)
            next_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_selector))
            )
            
            # Scroll button into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)

            time.sleep(random.uniform(3.0, 5.0))
            logger.info("Checking for popups before clicking")
            # Quick check for popups before clicking
            self.handle_popups(wait_time=3)
            logger.info("Popup check completed")
            # Wait before clicking
            next_button.click()
            # Wait after clicking
            time.sleep(random.uniform(4.0, 6.0))
            return True
        except Exception as e:
            logger.error(f"Error clicking next page button: {e}")
            return False

    def extract_items(self, items_limit: int = None) -> List[Dict[str, Any]]:
        """
        Extract product information from the current page.
        
        Args:
            items_limit: Maximum number of items to extract (optional)
        """
        logger.info("Starting item extraction")
        all_items_data = []
        seen_product_ids = set()
        
        while True:
            # First scroll to the next button to ensure all content loads
            try:
                next_button_selector = self.config["pagination"]["selectors"]["next_button"]["pattern"]
                next_button = self.driver.find_element(By.CSS_SELECTOR, next_button_selector)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                    next_button
                )
                # Wait for dynamic content to load
                time.sleep(random.uniform(2.0, 3.0))
            except Exception as e:
                logger.debug(f"Could not scroll to next button: {e}")
                # Continue anyway as we might be on the last page

            # Get current page source and parse
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find all product items
            items = soup.select(self.config["selectors"]["product_item"])
            logger.debug(f"Found {len(items)} items in current view")
            
            # Extract items
            new_items = 0
            for idx, item in enumerate(items, 1):
                try:
                    product_info = self.extract_product_info(
                        item, 
                        self.config["selectors"],
                        self.config
                    )
                    
                    if product_info:
                        # Simply exclude the product_item from the data
                        if 'product_item' in product_info:
                            del product_info['product_item']
                        
                        # # Debug print
                        # print("\n--- Product Info ---")
                        # for key, value in product_info.items():
                        #     print(f"{key}: {value}")
                        # print("------------------\n")
                        
                        product_id = product_info.get('store_product_id')
                        if product_id and product_id not in seen_product_ids:
                            all_items_data.append(product_info)
                            seen_product_ids.add(product_id)
                            new_items += 1
                            
                except Exception as e:
                    logger.error(f"Error extracting item {idx}: {e}")
                    continue
            
            logger.info(f"Extracted {new_items} new items")
            
            # Try to go to next page
            if self.has_next_page():
                logger.info("Going to next page...")
                self.go_to_next_page()
                time.sleep(random.uniform(2.0, 4.0))
            else:
                logger.info("No more pages available")
                break
            
            # Safety check
            if items_limit and len(all_items_data) >= items_limit:
                logger.info(f"Reached specified items limit of {items_limit}")
                break
        
        logger.info(f"Completed extraction. Total unique items: {len(all_items_data)}")
        return all_items_data

    def has_next_page(self) -> bool:
        """Check if there is a next page button."""
        try:
            next_button_selector = self.config["pagination"]["selectors"]["next_button"]["pattern"]
            next_button = self.driver.find_element(By.CSS_SELECTOR, next_button_selector)
            return next_button.is_displayed()
        except Exception:
            logger.error("Next page button not found")
            return False

    def go_to_next_page(self) -> None:
        """Navigate to the next page."""
        if self.has_next_page():
            self.click_next_page()

def get_scraper(config=None):
    """Factory function to create a MacysScraper instance."""
    logger.info("Creating new MacysScraper instance")
    if config is None:
        config = SCRAPER_CONFIG
        logger.debug("Using default scraper configuration")
    return MacysScraper(config)
