SCRAPER_CONFIG = {
    "store": "nordstrom",
    "brand": None,  # Since Nordstrom sells multiple brands
    "use_scraping_browser": False,
    "browser_config": {
        "headless": False,
        "window_size": [1920, 1080]
    },
    "popup_handlers": [
        {
            "type": "close_button",
            "selector": "#dialog-description > a",
            "wait_time": 5
        }
    ],
    "lazy_loading_type": "scroll",
    "scroll_behavior": {
        "human_like": True,
        "replace_data_on_scroll": False,
    },
    "pagination": {
        "type": "next_button",
        "selectors": {
            "next_button": {
                "pattern": "#product-results-view > div > div.EyLzO > div > section > footer > ul > li.v_hDo.rCIzA"
            }
        }
    },
    "selectors": {
        "product_item": "article.zzWfq",
        "store_product_id": {
            "method": "select_one",
            "pattern": "a.dls-ogz194",
            "attribute": "href"
        },
        "brand": {
            "method": "select_one",
            "pattern": "div.KtWqU.jgLpg.Y9bA4.Io521",
            "text": True
        },
        "name": {
            "method": "select_one",
            "pattern": "a.dls-ogz194",
            "text": True
        },
        "product_url": {
            "method": "select_one",
            "pattern": "a.dls-ogz194",
            "attribute": "href"
        },
        "image_url": {
            "method": "select_one",
            "pattern": "img.P9JC8",
            "attribute": "src"
        },
        "price_current": {
            "method": "select_one",
            "pattern": "span.qHz0a.BkySr.EhCiu.dls-ihm460, span.qHz0a.EhCiu.dls-ihm460",
            "text": True,
            "transform": "clean_price"
        },
        "price_min": {
            "method": "select_one",
            "pattern": "span.qHz0a.BkySr.EhCiu.dls-ihm460, span.qHz0a.EhCiu.dls-ihm460",
            "text": True,
            "transform": "first_price"
        },
        "price_max": {
            "method": "select_one",
            "pattern": "span.qHz0a.BkySr.EhCiu.dls-ihm460, span.qHz0a.EhCiu.dls-ihm460",
            "text": True,
            "transform": "last_price"
        },
        "price_original": {
            "method": "select_one",
            "pattern": "span.fj69a.EhCiu.dls-ihm460",
            "text": True,
            "transform": "clean_price"
        },
        "product_metadata": {
            "method": "extract_metadata",
            "selectors": {
                "rating": {
                    "method": "select_one",
                    "pattern": "span.T2Mzf",
                    "attribute": "aria-label"
                },
                "review_count": {
                    "method": "select_one",
                    "pattern": "span.HZv8u",
                    "text": True
                },
                "discount": {
                    "method": "select_one",
                    "pattern": "span.BkySr.EhCiu.dls-ihm460",
                    "text": True
                },
                "colors": {
                    "method": "select",
                    "pattern": "button.xvHAz",
                    "attribute": "aria-label"
                },
                "badges": {
                    "method": "select_one",
                    "pattern": "div.KxWmZ.UDYjU.UKMdh",
                    "text": True
                }
            }
        }
    }
} 