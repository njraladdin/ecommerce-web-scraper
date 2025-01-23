# Scraper Configuration Reference

The `SCRAPER_CONFIG` object defines how a store's product listings should be scraped. Below is a complete reference with all possible options and their explanations:

```javascript
{
    // Required: Unique identifier for the store being scraped
    "store": "store_name",

    // Optional: Default brand name for the store's products
    // Set to null for multi-brand stores like Nordstrom
    "brand": "brand_name" | null,

    // Required: Whether to use specialized scraping browser features
    "use_scraping_browser": false,

    // Required: Browser configuration settings
    "browser_config": {
        // Whether to run browser in headless mode
        "headless": false,
        // Browser window dimensions [width, height]
        "window_size": [1920, 1080]
    },

    // Optional: Handlers for dealing with popups
    "popup_handlers": [
        {
            // Type of popup handler (currently only "close_button" supported)
            "type": "close_button",
            // CSS selector for the close button
            "selector": "button.close",
            // Maximum seconds to wait for popup to appear
            "wait_time": 5
        }
    ],

    // Required: How additional products are loaded
    // Possible values: "scroll" | "pagination" | "button"
    "lazy_loading_type": "scroll",

    // Required: Controls scrolling behavior
    "scroll_behavior": {
        // Whether to simulate human-like scrolling patterns
        "human_like": true,
        // Whether to replace existing data when scrolling
        "replace_data_on_scroll": false
    },

    // Required for "pagination" or "button" lazy_loading_type
    "pagination": {
        // Type of pagination: "next_button" | "load_more_button"
        "type": "next_button",
        
        "selectors": {
            // For type="next_button": Selector for next page button
            "next_button": {
                "pattern": "button.next"
            },
            
            // For type="load_more_button": Selector for load more button
            "load_more_button": {
                "pattern": "button.load-more",
                // Optional: Text that should be contained in button
                "text_contains": "View More"
            },
            
            // Optional: Selector to extract total items count
            "total_items_indicator": {
                "pattern": "p.count",
                // Regex pattern with two capture groups: current and total
                "text_pattern": "Viewing (\\d+) of (\\d+)"
            }
        }
    },

    // Required: Selectors for extracting product data
    "selectors": {
        // CSS selector for individual product containers
        "product_item": "div.product",

        // How to extract store's unique product ID
        "store_product_id": {
            "method": "select_one",  // "select_one" or "select"
            "pattern": "a.product-link", // CSS selector
            "attribute": "href"  // Attribute to extract
        },

        // How to extract product brand (null if using default brand)
        "brand": {
            "method": "select_one",
            "pattern": "div.brand",
            "text": true  // Extract text content instead of attribute
        },

        // How to extract product name
        "name": {
            "method": "select_one",
            "pattern": "h2.name",
            "text": true
        },

        // How to extract product URL
        "product_url": {
            "method": "select_one",
            "pattern": "a.product-link",
            "attribute": "href"
        },

        // How to extract product image URL
        "image_url": {
            "method": "select_one",
            "pattern": "img.product-image",
            "attribute": "src",
            // Optional: Transform the extracted value
            // Possible values: "first_url", "clean_price", etc.
            "transform": "first_url"
        },

        // How to extract current price
        "price_current": {
            "method": "select_one",
            "pattern": "span.price",
            "text": true,
            "transform": "clean_price"
        },

        // How to extract original price (if on sale)
        "price_original": {
            "method": "select_one",
            "pattern": "span.original-price",
            "text": true
        },

        // Optional: Additional metadata to extract
        "product_metadata": {
            "method": "extract_metadata",
            "selectors": {
                // Example metadata fields
                "rating": {
                    "method": "select_one",
                    "pattern": "span.rating",
                    "attribute": "aria-label"
                },
                "review_count": {
                    "method": "select_one",
                    "pattern": "span.reviews",
                    "text": true
                },
                "colors": {
                    "method": "select",  // "select" gets all matches
                    "pattern": "button.color",
                    "attribute": "title"
                },
                "badges": {
                    "method": "select_one",
                    "pattern": "div.badge",
                    "text": true
                }
            }
        }
    }
}
```

Each selector configuration can have these properties:
- `method`: Either "select_one" (single element) or "select" (multiple elements)
- `pattern`: CSS selector pattern
- `attribute`: Name of attribute to extract (optional)
- `text`: Whether to extract text content instead of attribute (optional)
- `transform`: Name of transformation to apply to extracted value (optional)
- `text_contains`: For buttons, text that should be contained (optional)
- `text_pattern`: Regex pattern for extracting structured text (optional)
