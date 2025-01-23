from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import re

from utils.logger import logger
from crawlers.base import BaseScraper, HumanScrollingMixin, SelectorMixin
from .config import SCRAPER_CONFIG

class LululemonScraper(BaseScraper, HumanScrollingMixin, SelectorMixin):
    def __init__(self, config: dict):
        super().__init__(config)
        logger.info("Initializing LululemonScraper")
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

    def check_load_more_button(self) -> bool:
        """Check if the load more button is present and visible."""
        try:
            button_selector = self.config["pagination"]["selectors"]["load_more_button"]["pattern"]
            button_text = self.config["pagination"]["selectors"]["load_more_button"]["text_contains"]
            
            # Wait briefly for button to be present
            wait = WebDriverWait(self.driver, 3)
            buttons = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, button_selector))
            )
            
            for button in buttons:
                if button_text.lower() in button.text.lower():
                    # Scroll button into view
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                    time.sleep(random.uniform(1.0, 2.0))
                    return True
            return False
        except Exception as e:
            logger.debug(f"Load more button not found: {e}")
            return False

    def click_load_more(self) -> bool:
        """Click the load more button if it exists."""
        try:
            button_selector = self.config["pagination"]["selectors"]["load_more_button"]["pattern"]
            button_text = self.config["pagination"]["selectors"]["load_more_button"]["text_contains"]
            
            # Wait for button to be clickable
            wait = WebDriverWait(self.driver, 5)
            buttons = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, button_selector))
            )
            
            for button in buttons:
                if button_text.lower() in button.text.lower():
                    # Wait specifically for this button to be clickable
                    clickable_button = wait.until(
                        EC.element_to_be_clickable(button)
                    )
                    time.sleep(random.uniform(0.5, 1.0))
                    clickable_button.click()
                    time.sleep(random.uniform(2.0, 4.0))
                    return True
            return False
        except Exception as e:
            logger.error(f"Error clicking load more button: {e}")
            return False

    def get_total_items_info(self) -> Tuple[int, int]:
        """Get current and total items count from the indicator."""
        try:
            indicator_selector = self.config["pagination"]["selectors"]["total_items_indicator"]["pattern"]
            text_pattern = self.config["pagination"]["selectors"]["total_items_indicator"]["text_pattern"]
            
            indicator = self.driver.find_element(By.CSS_SELECTOR, indicator_selector)
            if indicator:
                match = re.search(text_pattern, indicator.text)
                if match:
                    current = int(match.group(1))
                    total = int(match.group(2))
                    return current, total
            return 0, 0
        except Exception as e:
            logger.error(f"Error getting total items info: {e}")
            return 0, 0

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
                        product_id = product_info.get('store_product_id')
                        if product_id and product_id not in seen_product_ids:
                            all_items_data.append(product_info)
                            seen_product_ids.add(product_id)
                            new_items += 1
                            
                except Exception as e:
                    logger.error(f"Error extracting item {idx}: {e}")
                    continue
            
            logger.info(f"Extracted {new_items} new items")
            
            # # Check if we've reached the end
            # current, total = self.get_total_items_info()
            # if current > 0 and total > 0:
            #     logger.info(f"Progress: {current}/{total} items")
            #     if current >= total:
            #         logger.info("Reached total items count")
            #         break
            
            try:
                # Try to load more items
                if self.check_load_more_button():
                    logger.info("Found load more button, clicking...")
                if not self.click_load_more():
                    logger.warning("Failed to click load more button")
                    # break
                time.sleep(random.uniform(2.0, 4.0))
            except Exception as e:
                logger.warning(f"Error checking or clicking load more button: {e}")


            logger.info("Scrolling...")
            self.scroll_page()
            # else:
            #     # If no load more button and we're not at total, try scrolling
            #     if new_items == 0:
            #         logger.info("No new items found and no load more button, stopping")
            #         break
                    
            #     logger.info("No load more button found, scrolling...")
            #     self.scroll_page()
            if new_items == 0:
                logger.info("No new items found and no load more button, stopping")
                break
            
            # Safety check
            if items_limit and len(all_items_data) >= items_limit:
                logger.info(f"Reached specified items limit of {items_limit}")
                break
        
        logger.info(f"Completed extraction. Total unique items: {len(all_items_data)}")
        return all_items_data

    def has_next_page(self) -> bool:
        """Not used in this implementation as we handle pagination in extract_items."""
        return False

    def go_to_next_page(self) -> None:
        """Not used in this implementation as we handle pagination in extract_items."""
        pass

def get_scraper(config=None):
    """Factory function to create a LululemonScraper instance."""
    logger.info("Creating new LululemonScraper instance")
    if config is None:
        config = SCRAPER_CONFIG
        logger.debug("Using default scraper configuration")
    return LululemonScraper(config) 