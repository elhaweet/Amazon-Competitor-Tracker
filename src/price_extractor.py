import re
import json
import datetime
from crawl4ai import AsyncWebCrawler, LLMExtractionStrategy, LLMConfig, CrawlerRunConfig, CacheMode

from config import BASE_URL, API_TOKEN, LLM_MODEL, PRICE_SELECTOR, PRODUCT_NAME_SELECTOR, DISCOUNT_SELECTOR, RATING_SELECTOR, NUM_OF_RATINGS
from src.scraper import get_browser_config


async def extract_product_price(url):
    """
    Extract the current price of a product from its URL.
    
    Args:
        url (str): The product URL to scrape
        
    Returns:
        tuple: (price_value, price_string, product_name, discount, rating, num_ratings, timestamp)
    """
    browser_config = get_browser_config()
    
    # Create a session ID with timestamp to avoid caching
    session_id = f"price_tracker_{datetime.datetime.now().timestamp()}"
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # First, extract the price directly using the CSS selector
        price_result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,  # Always get fresh data
                css_selector=PRICE_SELECTOR,  # Use the price selector from config
                session_id=session_id,
            ),
        )
        
        # Extract price from the selector result
        price_string = "Not available"
        price_value = None
        
        if price_result.success and price_result.cleaned_html:
            # Extract just the text content by removing all HTML tags
            price_text = re.sub(r'<[^>]+>', '', price_result.cleaned_html).strip()
            
            # Fix for repeated prices - extract only the first price pattern
            price_match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)', price_text)
            if price_match:
                price_text = price_match.group(1)
                # For Amazon Egypt, we need to add the currency
                price_string = f"$ {price_text}"
                # Extract numeric value
                try:
                    price_value = float(re.sub(r'[^\d.]', '', price_text))
                except ValueError:
                    print(f"Could not convert price '{price_text}' to numeric value")
        
        # Extract discount information using the provided CSS selector
        discount_result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                css_selector=DISCOUNT_SELECTOR,
                session_id=f"{session_id}_discount",
            ),
        )
        
        discount = "No discount"
        if discount_result.success and discount_result.cleaned_html:
            # Clean up the discount text by removing HTML tags
            discount_text = re.sub(r'<[^>]+>', '', discount_result.cleaned_html).strip()
            # Extract just the percentage value if it exists
            discount_match = re.search(r'(-?\d+(?:\.\d+)?)%', discount_text)
            if discount_match:
                discount = f"{discount_match.group(0)}"
            else:
                discount = discount_text
        
        # Extract product name using CSS selector instead of LLM
        name_result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                css_selector=PRODUCT_NAME_SELECTOR,  # Use the product name selector from config
                session_id=f"{session_id}_name",
            ),
        )
        
        product_name = "Unknown Product"
        if name_result.success and name_result.cleaned_html:
            # Clean up the product name by removing HTML tags
            product_name = re.sub(r'<[^>]+>', '', name_result.cleaned_html).strip()
        
        # Extract rating using CSS selector
        rating_result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                css_selector=RATING_SELECTOR,
                session_id=f"{session_id}_rating",
            ),
        )
        
        rating = "Not available"
        if rating_result.success and rating_result.cleaned_html:
            # Clean up the rating text by removing HTML tags
            rating_text = re.sub(r'<[^>]+>', '', rating_result.cleaned_html).strip()
            # Extract just the rating value if it exists
            rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
            if rating_match:
                rating = f"{rating_match.group(1)} out of 5"
            else:
                rating = rating_text
        
        # Extract number of ratings using CSS selector
        num_ratings_result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                css_selector=NUM_OF_RATINGS,
                session_id=f"{session_id}_num_ratings",
            ),
        )
        
        num_ratings = "Not available"
        if num_ratings_result.success and num_ratings_result.cleaned_html:
            # Clean up the number of ratings text by removing HTML tags
            num_ratings_text = re.sub(r'<[^>]+>', '', num_ratings_result.cleaned_html).strip()
            # Extract just the number if it exists
            num_ratings_match = re.search(r'(\d{1,3}(?:,\d{3})*)', num_ratings_text)
            if num_ratings_match:
                num_ratings = num_ratings_match.group(1)
            else:
                num_ratings = num_ratings_text
        
        # If CSS selector fails, fall back to LLM extraction
        if product_name == "Unknown Product":
            instruction = (
                "Extract only the exact product name from this Amazon product page. "
                "Return the data in JSON format with key 'name'."
            )
            
            llm_strategy = LLMExtractionStrategy(
                llm_config=LLMConfig(provider=LLM_MODEL, api_token=API_TOKEN),
                instruction=instruction,
                extraction_type="json",
                input_format="markdown",
                verbose=True,
            )
            
            # Run the crawler for product name with LLM
            name_result = await crawler.arun(
                url=url,
                config=CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    extraction_strategy=llm_strategy,
                    session_id=f"{session_id}_name_llm",
                ),
            )
            
            if name_result.success and name_result.extracted_content:
                try:
                    data = json.loads(name_result.extracted_content)
                    if isinstance(data, list) and data:
                        data = data[0] if isinstance(data[0], dict) else {"name": "Unknown Product"}
                    elif not isinstance(data, dict):
                        data = {"name": "Unknown Product"}
                    
                    product_name = data.get("name", "Unknown Product")
                except json.JSONDecodeError:
                    print("Error parsing product name JSON")
        
        timestamp = datetime.datetime.now()
        return price_value, price_string, product_name, discount, rating, num_ratings, timestamp