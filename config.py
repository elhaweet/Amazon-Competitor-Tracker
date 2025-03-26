import os

LLM_MODEL = "gemini/gemini-2.0-flash"

API_TOKEN = os.getenv("GEMINI_API_KEY")

# Base URL of the website to scrape.
# This URL is for Lenovo laptops on Amazon Egypt.
# You can modify the URL to change the product category or search query.
# The {page_number} placeholder will be replaced with the actual page number during crawling.
BASE_URL = "https://www.amazon.com/Lenovo-V15-Business-Display-Numeric/dp/B0D3JLHQ8K/ref=sr_1_4?crid=PJSLU1RHELZZ&dib=eyJ2IjoiMSJ9.g6y9YwJTWMx-PRpmNCGgzF3Gbh8-aRtwpdYAE2WNc6hrS_jiyxBOASsRgOriQJPcWaUaXJquWauP8eY2lZJRAQtjT_ItsjnDJxFpUi2R4WKnvvkvcP-0-i9cGkqcJSo_e3X3FpZgBt9uZ1oQk-9xcSsDHGcT67uIt919pw1zf9RaRrsf6ea5oYPyHety8smZY8FVDy_RupckPWiHEnLI1dtGfGJBhLwv8RcacRPE8gs.0Bh0BThrqKSWnHEaOHqGceDUGDQoGzLvugQrt0-vwRs&dib_tag=se&keywords=laptop%2Blenovo&qid=1742796037&sprefix=%2Caps%2C186&sr=8-4&th=1"

# CSS selector to target the main HTML element containing the product information.

# CSS selector specifically for the price element on Amazon product pages

## Very Specific CSS Selector for the price element on Amazon product pages
# PRICE_SELECTOR = "#corePriceDisplay_desktop_feature_div > div.a-section.a-spacing-none.aok-align-center.aok-relative > span.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay > span:nth-child(2) > span.a-price-whole"


## Less Specific CSS Selector for the price element on Amazon product pages
PRICE_SELECTOR = "span.a-price-whole"

# CSS selector for the product name on Amazon product pages
PRODUCT_NAME_SELECTOR = "span.a-size-large.product-title-word-break"

# CSS selector for the discount element on Amazon product pages
DISCOUNT_SELECTOR = "span.a-size-large.a-color-price.savingPriceOverride.aok-align-center.reinventPriceSavingsPercentageMargin.savingsPercentage"

NUM_OF_BOUGHT_IN_30_DAYS_SELECTOR = "span.a-text-bold"

RATING_SELECTOR = "#acrPopover > span.a-declarative > a > span"

NUM_OF_RATINGS ="#acrCustomerReviewText"


# Maximum number of pages to crawl. Adjust this value based on how much data you want to scrape.
MAX_PAGES = 3  # Example: Set to 5 to scrape 5 pages.

# Instructions for the LLM on what information to extract from the scraped content.
# The LLM will extract the following details for each product:
# - Name
# - Price
# - Rating
# - Reviews count
# - Availability
# - Description
# - URL
SCRAPER_INSTRUCTIONS = (
    "Extract the following information for each Amazon product in the search results: "
    "'name' (product title), 'price' (current price with currency), 'rating' (star rating), "
    "'reviews_count' (number of reviews), 'availability' (in stock or not), "
    "'description' (brief summary of key features), and 'url' (product page link). "
    "If any information is not available, indicate with 'Not available'."
)