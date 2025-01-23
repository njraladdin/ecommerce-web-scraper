import json
import argparse
import importlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from utils.logger import logger

def run_scraper(urls: List[str], store_name: str, items_limit: int = None) -> List[Dict[str, Any]]:
    """
    Run a store's scraper on URLs and return the results.
    Args:
        urls: List of URLs to scrape
        store_name: Name of the store (e.g., lululemon)
        items_limit: Maximum number of items to scrape (optional)
    Returns:
        List of extracted product information
    """
    logger.info(f"Starting scraper for store '{store_name}' with {len(urls)} URLs")
    
    store_scraper = None
    all_items = []
    
    try:
        # Dynamically import store-specific scraper and config
        logger.debug(f"Attempting to import modules for store: {store_name}")
        module = importlib.import_module(f"crawlers.stores.{store_name}.scripts.pipeline")
        logger.debug("Pipeline module imported successfully")
        
        # Initialize scraper
        logger.debug("Initializing store scraper...")
        store_scraper = module.get_scraper()
        logger.info(f"Successfully initialized scraper for store: {store_name}")
        
        # Process each URL
        for url in urls:
            try:
                logger.info(f"Processing URL: {url}")
                # Open the page
                store_scraper.open_page(url)
                #add debug for items_limit if there is one 
                logger.debug(f"Items limit set to: {items_limit}")

                # Extract items (pagination is handled within extract_items)
                items = store_scraper.extract_items(items_limit=items_limit)
                logger.info(f"Extracted {len(items)} items from URL: {url}")
                all_items.extend(items)
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {str(e)}", exc_info=True)
                continue
                
            finally:
                if store_scraper:
                    store_scraper.cleanup()
        
        return all_items
        
    except Exception as e:
        logger.error(f"Fatal error running scraper: {str(e)}", exc_info=True)
        return []

def save_results(items: List[Dict[str, Any]], store_name: str, output_dir: str = "crawler_output") -> str:
    """
    Save scraping results to a JSON file.
    Args:
        items: List of extracted items
        store_name: Name of the store
        output_dir: Directory to save results in
    Returns:
        Path to the saved file
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_path / f"{store_name}_{timestamp}.json"
    
    # Save results
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "store": store_name,
                "timestamp": timestamp,
                "total_items": len(items)
            },
            "items": items
        }, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Results saved to {filename}")
    return str(filename)

def main():
    """Run a store's scraper locally and save results to JSON."""
    parser = argparse.ArgumentParser(description='Run a store scraper locally')
    parser.add_argument('--store', type=str, required=True, help='Store name (e.g., lululemon)')
    parser.add_argument('--urls', type=str, required=True, help='URLs to scrape (comma-separated)')
    parser.add_argument('--output', type=str, default='crawler_output', help='Output directory for results')
    parser.add_argument('--items-limit', type=int, help='Maximum number of items to scrape')
    
    args = parser.parse_args()
    
    # Split URLs
    urls = [url.strip() for url in args.urls.split(',')]
    logger.info(f"Starting scraper with store: {args.store}, URLs: {urls}")
    
    # Run scraper
    items = run_scraper(urls, args.store, args.items_limit)
    
    # Save results
    if items:
        output_file = save_results(items, args.store, args.output)
        print(f"\nScraping completed successfully!")
        print(f"Total items extracted: {len(items)}")
        print(f"Results saved to: {output_file}")
    else:
        print("\nNo items were extracted or an error occurred.")

if __name__ == "__main__":
    main() 