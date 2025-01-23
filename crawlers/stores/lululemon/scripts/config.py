SCRAPER_CONFIG = {
    "store": "lululemon",
    "brand": "lululemon",
    "use_scraping_browser": False,
    "browser_config": {
        "headless": False,
        "window_size": [1920, 1080]
    },
    "popup_handlers": [
        {
            "type": "close_button",
            "selector": "button.closeButton-1vSmX",
            "wait_time": 5  # Maximum seconds to wait for popup
        }
    ],
    "lazy_loading_type": "button",
    "scroll_behavior": {
        "human_like": True,
        "replace_data_on_scroll": False,
    },
    "pagination": {
        "type": "load_more_button",
        "selectors": {
            "load_more_button": {
                "pattern": "button.pagination_button__V8a85",
                "text_contains": "View More Products"
            },
            "total_items_indicator": {
                "pattern": "p.pagination_indicator__OIBX5",
                "text_pattern": r"Viewing (\d+) of (\d+)"
            }
        }
    },
    "selectors": {
        "product_item": "div.product-list_productListItem__uA9Id",
        "store": None,
        "store_product_id": {
            "method": "select_one",
            "pattern": "a.link.product-tile__image-link",
            "attribute": "data-productid"
        },
        "brand": None,
        "name": {
            "method": "select_one",
            "pattern": "a.link.lll-font-weight-medium",
            "text": True
        },
        "product_url": {
            "method": "select_one",
            "pattern": "a.link.product-tile__image-link",
            "attribute": "href"
        },
        "image_url": {
            "method": "select_one",
            "pattern": "source[type='image/webp']",
            "attribute": "srcset",
            "transform": "first_url"
        },
        "price_current": {
            "method": "select_one",
            "pattern": "span.price__UKrxpE span:not(.lll-hidden-visually):not(.price__spacer):not(.priceInactiveListPrice__x8WoFg)",
            "text": True,
            "transform": "first_price"
        },
        "price_min": {
            "method": "select_one",
            "pattern": "span.price__UKrxpE span:not(.lll-hidden-visually):not(.price__spacer):not(.priceInactiveListPrice__x8WoFg)",
            "text": True,
            "transform": "first_price"
        },
        "price_max": {
            "method": "select_one",
            "pattern": "span.price__UKrxpE span:not(.lll-hidden-visually):not(.price__spacer):not(.priceInactiveListPrice__x8WoFg)",
            "text": True,
            "transform": "last_price"
        },
        "price_original": {
            "method": "select_one",
            "pattern": "span.priceInactiveListPrice__x8WoFg span:not(.lll-hidden-visually)",
            "text": True,
            "transform": "clean_price"
        },
        "product_metadata": {
            "method": "select_one",
            "pattern": "a.link.product-tile__image-link",
            "attribute": "data-lulu-attributes"
        },
    }
}