# E-commerce Web Scraper

A Python-based web scraper for e-commerce sites using Selenium and BeautifulSoup4.

## Task

We need to implement scrapers for several e-commerce stores following the same pattern as the Lululemon implementation. The goal is to scrape all clothing items from the provided URLs, handling pagination, lazy loading, and scrolling as needed.

### Requirements

1. Use the Lululemon scraper (`crawlers/stores/lululemon/`) as a working example
2. Each scraper should:
   - Extract all products from the provided URL
   - Handle pagination/infinite scroll/lazy loading
   - Follow the same schema for data extraction
   - Use normal Selenium by default, only use scraping browser if needed (when bot protection blocks normal Selenium)
   - Handle any popups or overlays that might appear
   - Implement proper error handling and logging

### Stores to Implement

1. **Nordstrom** (Fix/Complete existing implementation)
   - URL: `https://www.nordstrom.com/browse/men/all?breadcrumb=Home%2FMen%2FAll%20Men`
   - Currently uses scraping browser but might work with normal Selenium
   - Needs proper scroll handling and product extraction

2. **Macys** (New Implementation)
   - URL: `https://www.macys.com/shop/mens-clothing/all-mens-clothing?id=197651`
   - Test with normal Selenium first
   - Implement pagination/scroll handling

3. **Quince** (New Implementation)
   - URL: `https://www.quince.com/men?qpid=_elmtbo79k`
   - Test with normal Selenium first
   - Implement lazy loading/scroll handling

### Data Schema

Each product should include (where available):
```python
{
    "store": str,              # Store name (e.g., "lululemon")
    "store_product_id": str,   # Unique product ID from the store
    "brand": str,              # Brand name
    "name": str,               # Product name
    "product_url": str,        # Full URL to product page
    "image_url": str,          # Main product image URL
    "price_current": str,      # Current price (without currency symbol)
    "price_original": str,     # Original price if on sale (without currency symbol)
    "product_metadata": dict   # Any additional product data (colors, ratings, etc.)
}
```

### Implementation Steps

1. Create store directory under `crawlers/stores/` if it doesn't exist
2. Create `config.py` with selectors and configuration:
   ```python
   SCRAPER_CONFIG = {
       "store": "store_name",
       "use_scraping_browser": False,  # Only set True if normal Selenium doesn't work
       "lazy_loading_type": "scroll",  # or "button" or "pagination"
       "scroll_behavior": {
           "human_like": True
       },
       "selectors": {
           # Add CSS selectors for all required fields
       }
   }
   ```
3. Create `pipeline.py` implementing the scraper class:
   - Inherit from `BaseScraper`
   - Implement all required methods
   - Use the Lululemon implementation as a reference

### Testing

Test your implementation with:
```bash
python -m crawlers.run_scraper --store <store_name> --urls "<url>"
```

The scraper should:
- Successfully extract all products
- Handle errors gracefully
- Save results to JSON with proper metadata
- Log progress and any issues

## Requirements

- Python 3.12+
- Chrome/Chromium browser
- uv (Python package manager)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd crawler-project
```

2. Create and activate a virtual environment:
```bash
uv sync
source .venv/bin/activate  # On Unix/macOS
# OR
.venv\Scripts\activate  # On Windows
```

3. Create a `.env` file in the root directory:
```bash
SCRAPING_BROWSER_URL="your-browser-url-here"  # Only needed if use_scraping_browser is True
```

## Usage

The scraper can be run in two modes:

### Local Mode (Without Remote Browser)

```bash
python -m crawlers.run_scraper --store lululemon --urls "https://shop.lululemon.com/c/shoes/_/N-1z0xcmkZ8tj"
```

### Remote Browser Mode

```bash
python -m crawlers.run_scraper --store nordstrom --urls "https://www.nordstrom.com/browse/women/clothing"
```

### Command Line Arguments

- `--store`: Store name (e.g., 'lululemon', 'nordstrom')
- `--urls`: URLs to scrape (comma-separated for multiple URLs)
- `--output`: Output directory for scraped data (default: 'crawler_output')
- `--items-limit`: Maximum number of items to scrape (optional)

### Example Usage

Basic usage for each store:

**Lululemon:**
```bash
python -m crawlers.run_scraper --store lululemon --urls "https://shop.lululemon.com/c/shoes/_/N-1z0xcmkZ8tj" --items-limit 50
```

**Nordstrom:**
```bash
python -m crawlers.run_scraper --store nordstrom --urls "https://www.nordstrom.com/browse/men/all?breadcrumb=Home%2FMen%2FAll%20Men" --items-limit 50
```

**Macys:**
```bash
python -m crawlers.run_scraper --store macys --urls "https://www.macys.com/shop/mens-clothing/all-mens-clothing?id=197651" --items-limit 50
```

**Quince:**
```bash
python -m crawlers.run_scraper --store quince --urls "https://www.quince.com/men?qpid=_elmtbo79k" --items-limit 50
```

If no `--items-limit` is specified, the scraper will collect all available items from the URL.

## Project Structure

```
crawler-project/
├── crawlers/
│   ├── base.py              # Base scraper classes and mixins
│   ├── run_scraper.py       # Main entry point
│   └── stores/             # Store-specific implementations
│       ├── lululemon/
│       └── nordstrom/
├── utils/
│   └── logger.py           # Logging configuration
├── .env                    # Environment variables
├── .gitignore
├── README.md
└── pyproject.toml         # Project dependencies and config
```

## Adding New Stores

1. Create a new directory under `crawlers/stores/`
2. Implement the store configuration in `config.py`
3. Create a scraper class in `pipeline.py` that inherits from `BaseScraper`
4. Implement the required abstract methods

## Logging

Logs are stored in `logs/crawler.log` with rotation enabled (500MB max size, 10 days retention).

## Stores of interest:
Nordstrom:
https://www.nordstrom.com/browse/men/all?breadcrumb=Home%2FMen%2FAll%20Men

Macys:
https://www.macys.com/shop/mens-clothing/all-mens-clothing?id=197651

Quince:
https://www.quince.com/men?qpid=_elmtbo79k

