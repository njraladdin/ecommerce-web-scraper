from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import platform
import os
from dotenv import load_dotenv


from utils.logger import logger

# Load environment variables from .env file
load_dotenv()

class SelectorMixin:
    """Mixin class for handling selectors in a consistent way across scrapers."""
    
    def _transform_price(self, value: str) -> str:
        """Clean and transform price string."""
        if not value:
            return None
        # Remove currency symbols and any whitespace
        return value.replace('$', '').replace('USD', '').strip()
    
    def _extract_price_range(self, value: str) -> tuple:
        """Extract min and max prices from a price range string."""
        try:
            if not value:
                return None, None
            
            # Clean the string and split by range indicator
            clean_value = value.replace('$', '').replace('USD', '').strip()
            
            # Remove discount information in parentheses if present
            if '(' in clean_value:
                clean_value = clean_value.split('(')[0].strip()
            
            if '-' in clean_value:
                parts = clean_value.split('-')
                min_price = parts[0].strip()
                max_price = parts[1].strip()
                return min_price, max_price
            
            return clean_value, clean_value
            
        except Exception as e:
            logger.error(f"Error extracting price range from '{value}': {str(e)}")
            return None, None
    
    def extract_with_selector(self, soup_item: BeautifulSoup, selector: Dict[str, Any] | str) -> Any:
        """
        Extract data from BeautifulSoup object using a selector configuration.
        Args:
            soup_item: BeautifulSoup object to extract from
            selector: Selector configuration dictionary with method, pattern, and optional attribute/text flags,
                     or a string representing the CSS selector pattern directly
        Returns:
            Extracted value or None if not found
        """
        if selector is None:
            logger.debug("Selector is None, skipping")
            return None
            
        try:
            # Handle string selector (direct CSS pattern)
            if isinstance(selector, str):
                elements = soup_item.select(selector)
                return elements
            
            # Handle dictionary selector configuration
            method = selector.get('method', 'select_one')
            pattern = selector.get('pattern')
            attribute = selector.get('attribute')
            text_only = selector.get('text', False)
            transform = selector.get('transform')
            
            logger.debug(f"Extracting with selector - Method: {method}, Pattern: {pattern}, "
                        f"Attribute: {attribute}, Text Only: {text_only}, Transform: {transform}")
            
            if method == 'select_one':
                element = soup_item.select_one(pattern)
                if element:
                    if attribute:
                        value = element.get(attribute)
                    else:
                        value = element.text.strip() if text_only else str(element)
                else:
                    value = None
                    
            elif method == 'select':
                elements = soup_item.select(pattern)
                if elements:
                    if attribute:
                        value = [el.get(attribute) for el in elements]
                    else:
                        value = [el.text.strip() if text_only else str(el) for el in elements]
                else:
                    value = None
            else:
                logger.warning(f"Unsupported selector method: {method}")
                return None

            # Apply transformations if specified
            if transform and value:
                logger.debug(f"Applying transform '{transform}' to value: {value}")
                if transform == 'first_url':
                    # Extract first URL from a srcset attribute
                    value = value.split(',')[0].split(' ')[0] if isinstance(value, str) else value
                elif transform == 'clean_price':
                    value = self._transform_price(value)
                elif transform == 'first_price':
                    min_price, _ = self._extract_price_range(value)
                    logger.debug(f"first_price transform result: {min_price}")
                    value = min_price
                elif transform == 'last_price':
                    _, max_price = self._extract_price_range(value)
                    logger.debug(f"last_price transform result: {max_price}")
                    value = max_price
                # Add more transformations as needed
                
            logger.debug(f"Final extracted value: {value}")
            return value
            
        except Exception as e:
            logger.error(f"Error extracting with selector: {e}")
            return None

    def get_config_value(self, field: str, config: Dict[str, Any]) -> Any:
        """
        Get a value directly from config for fields that don't need selectors.
        Args:
            field: The field name to look for in config
            config: The configuration dictionary
        Returns:
            The config value if found, None otherwise
        """
        # First check if it's a direct config value
        if field in config:
            return config[field]
        return None

    def extract_metadata(self, soup_item: BeautifulSoup, selector_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata fields using nested selectors configuration.
        
        Args:
            soup_item: BeautifulSoup object to extract from
            selector_config: Dictionary containing metadata selectors configuration
            
        Returns:
            Dictionary of extracted metadata where each key is the metadata field
            and value is the extracted data
        """
        metadata = {}
        
        # Get the nested selectors for metadata fields
        selectors = selector_config.get('selectors', {})
        
        # Extract each configured metadata field
        for field, field_selector in selectors.items():
            try:
                value = self.extract_with_selector(soup_item, field_selector)
                if value is not None:
                    metadata[field] = value
            except Exception as e:
                logger.debug(f"Failed to extract metadata field '{field}': {str(e)}")
                continue
            
        return metadata

    def extract_product_info(self, soup_item: BeautifulSoup, selectors: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract all product information using configured selectors and config values.
        Args:
            soup_item: BeautifulSoup object of the product item
            selectors: Dictionary of selector configurations
            config: Full configuration dictionary for non-selector values
        Returns:
            Dictionary of extracted product information
        """
        product_info = {}
        config = config or {}
        
        for field, selector in selectors.items():
            try:
                # First try to get value from config if it's a direct config field
                config_value = self.get_config_value(field, config)
                if config_value is not None:
                    product_info[field] = config_value
                    logger.debug(f"Using config value for {field}: {config_value}")
                    continue
                
                # Special handling for metadata field
                if field == 'product_metadata' and isinstance(selector, dict) and selector.get('method') == 'extract_metadata':
                    metadata = self.extract_metadata(soup_item, selector)
                    if metadata:
                        product_info[field] = metadata
                    continue
                    
                # If no config value, try to extract using selector
                value = self.extract_with_selector(soup_item, selector)
                if value is not None:
                    product_info[field] = value
                
            except Exception as e:
                logger.error(f"Error extracting field '{field}': {str(e)}")
                continue
            
        return product_info

class BaseScraper(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.driver = None

    def handle_popups(self, wait_time: int = 5) -> None:
        """Handle any popups that might appear."""
        popup_handlers = self.config.get("popup_handlers", [])
        logger.info(f"Found {len(popup_handlers)} popup handlers")
        logger.info(f"Popup handlers: {popup_handlers}")
        
        for handler in popup_handlers:
            try:
                handler_type = handler.get("type")
                selector = handler.get("selector")
                # Use handler's wait_time if available, otherwise use param
                handler_wait_time = handler.get("wait_time", wait_time)
                
                if handler_type == "close_button":
                    logger.info(f"Looking for popup close button: {selector}")
                    
                    # Wait for elements to appear
                    try:
                        wait = WebDriverWait(self.driver, handler_wait_time)
                        wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    except TimeoutException:
                        logger.info(f"No popup appeared within {handler_wait_time} seconds")
                        continue
                    
                    # Find and try to click elements
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Found {len(elements)} popup close buttons")
                        for elem in elements:
                            try:
                                button_id = elem.get_attribute('id')
                                logger.info(f"Trying to click button ID: {button_id}")
                                if elem.is_displayed():  # Just check if it's visible
                                    elem.click()
                                    logger.info(f"Successfully clicked popup button: {button_id}")
                                    time.sleep(0.5)
                            except Exception as e:
                                logger.debug(f"Could not click button {button_id}: {e}")
                                continue
                    else:
                        logger.info("No popup buttons found")
                    
            except Exception as e:
                logger.warning(f"Error handling popup: {str(e)}")

    @abstractmethod
    def open_page(self, url: str) -> None:
        """Open the URL using either normal or scraping browser."""
        pass

    @abstractmethod
    def scroll_page(self) -> None:
        """Perform any scroll logic or pagination required."""
        pass

    @abstractmethod
    def extract_items(self) -> List[Dict[str, Any]]:
        """Extract the clothing items from the currently loaded page."""
        pass

    @abstractmethod
    def has_next_page(self) -> bool:
        """Determine if there is another page to load."""
        pass

    @abstractmethod
    def go_to_next_page(self) -> None:
        """Go to the next page (click the next button, if applicable)."""
        pass

    def setup_driver(self) -> webdriver.Remote:
        """Setup and return a configured webdriver based on config."""
        chrome_options = Options()
        
        # Get browser config
        browser_config = self.config.get("browser_config", {})
        headless = browser_config.get("headless", True)
        window_size = browser_config.get("window_size", [1920, 1080])
        
        # Enable incognito mode
        chrome_options.add_argument('--incognito')
        
        # Anti-detection arguments
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Add random user agent with more modern versions

        
        # Additional anti-detection and privacy arguments
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-save-password-bubble')
        chrome_options.add_argument('--disable-translate')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-service-autorun')
        chrome_options.add_argument('--password-store=basic')
        chrome_options.add_argument('--use-mock-keychain')
        
        # New anti-detection arguments
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-client-side-phishing-detection')
        chrome_options.add_argument('--disable-site-isolation-trials')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--disable-blink-features')
        chrome_options.add_argument('--disable-plugins-discovery')
        chrome_options.add_argument('--disable-javascript-harmony-shipping')
        
        # Add random plugins count to make fingerprinting harder
        chrome_options.add_argument(f'--plugins-metadata-allowed-for-urls={"," * random.randint(1, 5)}')
        
        # Randomize accepted languages
        languages = ['en-US,en;q=0.9', 'en-GB,en;q=0.9', 'en-CA,en;q=0.9', 'en;q=0.9']
        chrome_options.add_argument(f'--lang={random.choice(languages)}')
        
        # Add random screen specs
        resolutions = ['1920,1080', '2560,1440', '1366,768', '1440,900', '1536,864']
        chrome_options.add_argument(f'--window-size={random.choice(resolutions)}')
        
        if headless:
            chrome_options.add_argument("--headless=new")  # Using newer headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--start-maximized")
        
        if self.config.get("use_scraping_browser"):
            # Setup the remote scraping browser
            remote_url = os.getenv("SCRAPING_BROWSER_URL")
            driver = webdriver.Remote(
                command_executor=remote_url,
                options=chrome_options
            )
        else:
            # Use local ChromeDriver with automatic installation
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Only try chromium on Linux
            if platform.system() == "Linux":
                try:
                    chrome_options.binary_location = "/usr/bin/chromium"
                    service = ChromeService(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    return driver
                except Exception as e:
                    logger.warning(f"Failed to use chromium, falling back to regular chrome: {e}")
            
            # Use regular Chrome for macOS or if Chromium failed on Linux
            chrome_options.binary_location = ""  # Reset binary location
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

        # Set window size
        driver.set_window_size(window_size[0], window_size[1])

        # # Execute CDP commands to prevent detection
        # driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        #     "userAgent": random.choice(user_agents)
        # })
        
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.driver:
            self.driver.quit()


class HumanScrollingMixin:
    def human_like_scroll(self, driver):
        """Scroll down the page in a human-like manner."""
        total_height = driver.execute_script("return document.body.scrollHeight")
        viewport_height = driver.execute_script("return window.innerHeight")
        current_position = driver.execute_script("return window.pageYOffset")
        scroll_steps = random.randint(5, 8)
        
        for step in range(scroll_steps):
            scroll_distance = random.randint(300, 2000)
            current_position += scroll_distance
            if current_position > total_height - viewport_height:
                current_position = total_height - viewport_height
            
            driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}})")
            time.sleep(random.uniform(0.5, 2.0))
            
            # Occasionally pause longer (10% chance)
            if random.random() < 0.1:
                time.sleep(random.uniform(1.5, 3.0))
            
            if current_position >= total_height - viewport_height:
                break