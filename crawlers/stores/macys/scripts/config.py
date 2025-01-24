SCRAPER_CONFIG = {
    "store": "macys",
    "brand": "macys",
    "use_scraping_browser": False,
    "browser_config": {
        "headless": False,
        "window_size": [1920, 1080]
    },
    "popup_handlers": [
        {
            "type": "close_button",
            "selector": "[id^='bx-close-inside-']",
            "wait_time": 5
        }
    ],
    "lazy_loading_type": "pagination",
    "scroll_behavior": {
        "human_like": True,
        "replace_data_on_scroll": False,
    },
    "pagination": {
        "type": "next_button",
        "selectors": {
            "next_button": {
                "pattern": "#canvas > div.pagination.pagination-wrapper > nav > ul.pagination > li:nth-child(3)"
            }
        }
    },
    "selectors": {
        "product_item": ".product-thumbnail-container",
        "store": None,  # Set in code
        "store_product_id": {
            "method": "select_one",
            "pattern": ".product-description a",
            "attribute": "href"
        },
        "brand": {
            "method": "select_one",
            "pattern": ".product-brand.medium",
            "text": True
        },
        "name": {
            "method": "select_one",
            "pattern": ".product-name.medium",
            "text": True
        },
        "product_url": {
            "method": "select_one",
            "pattern": ".product-description a",
            "attribute": "href"
        },
        "image_url": {
            "method": "select_one",
            "pattern": "picture source[type='image/webp']",
            "attribute": "srcset"
        },
        "price_current": {
            "method": "select_one",
            "pattern": "div.pricing.price-simplification > div:nth-child(1) > span",
            "text": True,
            "transform": "clean_price"
        },
        "price_min": {
            "method": "select_one",
            "pattern": "div.pricing.price-simplification > div:nth-child(1) > span",
            "text": True,
            "transform": "first_price"
        },
        "price_max": {
            "method": "select_one",
            "pattern": "div.pricing.price-simplification > div:nth-child(1) > span",
            "text": True,
            "transform": "last_price"
        },
        "price_original": {
            "method": "select_one",
            "pattern": ".price-strike-sm",
            "text": True,
            "transform": "clean_price"
        },
        "product_metadata": {
            "method": "extract_metadata",
            "selectors": {
                "rating": {
                    "method": "select_one",
                    "pattern": "fieldset[aria-label^='Rated']",
                    "attribute": "aria-label"
                },
                "review_count": {
                    "method": "select_one",
                    "pattern": ".rating-description span.small",
                    "text": True
                },
                "colors": {
                    "method": "select",
                    "pattern": ".colors-container label",
                    "attribute": "title"
                }
            }
        }
    }
}
