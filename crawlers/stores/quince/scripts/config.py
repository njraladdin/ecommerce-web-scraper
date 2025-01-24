SCRAPER_CONFIG = {
    "store": "quince",
    "brand": "Quince",
    "use_scraping_browser": False,
    "browser_config": {
        "headless": False,
        "window_size": [1920, 1080]
    },
    "popup_handlers": [
        {
            "type": "close_button",
            "selector": "#closeIconContainer",
            "wait_time": 5
        }
    ],
    "lazy_loading_type": "scroll",
    "scroll_behavior": {
        "human_like": True,
        "replace_data_on_scroll": False,
    },
    "selectors": {
        "product_item": ".product-card-module--productCard--340e0",
        "store": None,
        "store_product_id": {
            "method": "select_one",
            "pattern": "a.product-card-link-module--productLink--037ff",
            "attribute": "href"
        },
        "brand": None,
        "name": {
            "method": "select_one",
            "pattern": "a.product-card-link-module--productLink--037ff",
            "text": True
        },
        "product_url": {
            "method": "select_one",
            "pattern": "a.product-card-link-module--productLink--037ff",
            "attribute": "href"
        },
        "image_url": {
            "method": "select_one",
            "pattern": "picture source[type='image/webp']",
            "attribute": "srcset"
        },
        "price_current": {
            "method": "select_one",
            "pattern": "div.product-title-section-module--basePrice--9cd19",
            "text": True,
            "transform": "clean_price"
        },
        "price_original": None,
        "product_metadata": {
            "method": "extract_metadata",
            "selectors": {
                "rating": {
                    "method": "select_one",
                    "pattern": "span.product-card-footer-module--rating_text--b4c8a",
                    "text": True
                },
                "colors": {
                    "method": "select",
                    "pattern": "input.option-container-module--input--02174",
                    "attribute": "value"
                },
                "tags": {
                    "method": "select",
                    "pattern": "li.product-tags-module--tag--ccf2a",
                    "text": True
                }
            }
        }
    }
}
