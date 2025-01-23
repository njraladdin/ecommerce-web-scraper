from typing import List, Dict, Any
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
import random

from utils.logger import logger
from crawlers.base import BaseScraper, HumanScrollingMixin, SelectorMixin
from .config import SCRAPER_CONFIG

class NordstromScraper(BaseScraper, HumanScrollingMixin, SelectorMixin):
    def __init__(self, config: dict):
        super().__init__(config)
        logger.info("Initializing NordstromScraper")
        logger.debug(f"Scraper configuration: {config}")

    def open_page(self, url: str) -> None:
        """Open the URL using configured browser."""
        logger.info(f"Opening page: {url}")
        self.driver = self.setup_driver()
        
        # Try up to 5 times to successfully visit nordstrom.com
        tries = 0
        success = False
        
        while tries < 5 and not success:
            tries += 1
            logger.debug(f"Attempt {tries} to visit nordstrom.com")
            
            try:
                # Visit nordstrom.com
                self.driver.get("https://www.nordstrom.com")
                time.sleep(2)
                
                # Check for header element
                header_elements = self.driver.find_elements(By.CSS_SELECTOR, "#global-header-desktop > div > a > figure")
                if header_elements:
                    success = True
                    logger.info("Successfully loaded nordstrom.com with header element present")
                    break
                else:
                    logger.warning(f"Header element not found on attempt {tries}")
                    # Open new tab for next attempt
                    self.driver.execute_script("window.open('');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    
            except Exception as e:
                logger.error(f"Error during attempt {tries}: {str(e)}")
                # Open new tab for next attempt
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                continue
        
        if not success:
            raise Exception("Failed to load nordstrom.com after 5 attempts - website may be blocking access")
            
        # Navigate to target URL in current tab
        logger.debug(f"Loading target URL: {url}")
        self.driver.get(url)
        time.sleep(random.uniform(2.0, 4.0))
        logger.debug("Target page loaded successfully")
    def scroll_page(self) -> None:
        """Scroll the page using human-like behavior."""
        logger.debug("Starting page scroll")
        if self.config["scroll_behavior"]["human_like"]:
            self.human_like_scroll(self.driver)
        time.sleep(random.uniform(1.5, 3.0))
        logger.debug("Page scroll completed")

    def extract_items(self, items_limit: int = None) -> List[Dict[str, Any]]:
        """
        Extract product information from the current page.
        
        Args:
            items_limit: Maximum number of items to extract (optional)
        """
        logger.info("Starting item extraction")
        all_items_data = []
        
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
            
            # Save page source for debugging
            page_source = self.driver.page_source
            
            # Parse the entire page
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
                        if 'product_item' in product_info:
                            del product_info['product_item']
                        all_items_data.append(product_info)
                        new_items += 1
                        
                except Exception as e:
                    logger.error(f"Error extracting item {idx}: {e}")
                    continue
            
            logger.info(f"Extracted {new_items} new items from current page")
            
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
        
        logger.info(f"Completed extraction. Total items: {len(all_items_data)}")
        return all_items_data

    def has_next_page(self) -> bool:
        """Check if there is a next page button."""
        try:
            next_button_selector = self.config["pagination"]["selectors"]["next_button"]["pattern"]
            next_buttons = self.driver.find_elements(By.CSS_SELECTOR, next_button_selector)
            result = len(next_buttons) > 0
            if not result:
                logger.info("No next page button found on the page")
            return result
        except Exception as e:
            logger.info(f"Error checking for next page button: {e}")
            return False

    def go_to_next_page(self) -> None:
        """Click the next page button if it exists."""
        logger.info("Attempting to navigate to next page")
        #time.sleep(10000000)
        try:
            if self.has_next_page():
                next_button_selector = self.config["pagination"]["selectors"]["next_button"]["pattern"]
                next_button = self.driver.find_element(By.CSS_SELECTOR, next_button_selector)
                
                # Scroll button into view
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                    next_button
                )
                time.sleep(random.uniform(1.0, 2.0))
                
                # Wait before clicking
                time.sleep(random.uniform(2.0, 4.0))
                next_button.click()
                logger.info("Successfully clicked next page button")
                time.sleep(random.uniform(3.0, 5.0))
            else:
                logger.info("No next page button found - we may be on the last page")
        except Exception as e:
            logger.info(f"Error while clicking next page button: {e}")

def get_scraper(config=None):
    """Factory function to create a NordstromScraper instance."""
    logger.info("Creating new NordstromScraper instance")
    if config is None:
        config = SCRAPER_CONFIG
        logger.debug("Using default scraper configuration")
    return NordstromScraper(config) 