import asyncio
from dotenv import load_dotenv

from config import (
    BASE_URL, PRICE_SELECTOR, PRODUCT_NAME_SELECTOR, DISCOUNT_SELECTOR,
    NUM_OF_BOUGHT_IN_30_DAYS_SELECTOR, RATING_SELECTOR, NUM_OF_RATINGS
)
from src.price_extractor import extract_product_price
from src.data_storage import save_price_to_mongodb, CSV_FILENAME
from src.price_analyzer import check_price_change
from src.mongodb_handler import mongodb_handler

# Load environment variables
load_dotenv()

# Configuration for price tracking
TRACKING_INTERVAL = 10  # seconds

# Initialize MongoDB connection
mongodb_handler.connect()

async def track_price(single_run=False):
    """
    Main function to track the price of a product over time.
    
    Args:
        single_run (bool): If True, run once and return the result instead of looping
        
    Returns:
        dict: The extracted data if single_run is True, otherwise None
    """
    print(f"Starting price tracker for: {BASE_URL}")
    if not single_run:
        print(f"Checking price every {TRACKING_INTERVAL} seconds")
        print(f"Price history will be saved to MongoDB and {CSV_FILENAME}")
    
    while True:
        try:
            # Extract current price and additional data
            price_value, price_string, product_name, discount, rating, num_ratings, timestamp = await extract_product_price(BASE_URL)
            
            result = None
            if price_string != "Not available":
                print(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {product_name}")
                print(f"Price: {price_string} (Discount: {discount})")
                print(f"Rating: {rating} ({num_ratings} ratings)")
                
                # Save to MongoDB and CSV
                save_price_to_mongodb(
                    price_value, price_string, product_name, discount,
                    rating, num_ratings, timestamp
                )
                
                # Check for significant price change
                if price_value is not None:
                    has_changed, percent_change = check_price_change(price_value)
                    if has_changed:
                        print(f"🔔 PRICE CHANGE ALERT: {percent_change:.2%} change detected!")
                
                # Prepare result for API if in single_run mode
                if single_run:
                    result = {
                        "product_name": product_name,
                        "price": price_string,
                        "price_numeric": price_value,
                        "discount": discount,
                        "rating": rating,
                        "num_ratings": num_ratings,
                        "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    }
            else:
                print(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] Failed to extract price")
                if single_run:
                    result = {
                        "error": "Failed to extract price",
                        "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    }
        
        except Exception as e:
            print(f"Error in price tracking: {e}")
            if single_run:
                result = {
                    "error": str(e),
                    "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S') if 'timestamp' in locals() else None
                }
        
        # If single_run mode, return the result and exit
        if single_run:
            return result
            
        # Wait for the next check
        await asyncio.sleep(TRACKING_INTERVAL)


async def main():
    """
    Entry point of the script.
    """
    await track_price()


if __name__ == "__main__":
    asyncio.run(main())