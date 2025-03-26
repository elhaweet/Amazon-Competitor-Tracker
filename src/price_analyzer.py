import os
import csv
from src.mongodb_handler import mongodb_handler
from src.data_storage import CSV_FILENAME

# Constants
PRICE_CHANGE_THRESHOLD = 0.01  # 1% threshold for price change notifications

def check_price_change(current_price):
    """
    Check if there's a significant price change compared to the last recorded price.
    
    Args:
        current_price (float): The current price value
        
    Returns:
        tuple: (bool, float) - Whether there's a significant change and the percentage change
    """
    if current_price is None:
        return False, 0
    
    try:
        # First try to get the previous price from MongoDB
        previous_entries = mongodb_handler.get_previous_prices(limit=2)
        
        if len(previous_entries) > 1:
            # Get the second-to-last entry (previous price)
            previous_price = previous_entries[1].get('price_numeric')
            if previous_price is not None:
                # Calculate percentage change
                if previous_price > 0:
                    percent_change = abs(current_price - previous_price) / previous_price
                    return percent_change >= PRICE_CHANGE_THRESHOLD, percent_change
        
        # Fallback to CSV if MongoDB doesn't have enough data
        if not os.path.isfile(CSV_FILENAME):
            return False, 0
        
        with open(CSV_FILENAME, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            
            if len(rows) <= 1:  # Not enough data for comparison
                return False, 0
            
            # Get the previous price (second to last entry)
            previous_price = rows[-2].get('price_numeric')
            if previous_price and previous_price != '':
                previous_price = float(previous_price)
                
                # Calculate percentage change
                if previous_price > 0:
                    percent_change = abs(current_price - previous_price) / previous_price
                    return percent_change >= PRICE_CHANGE_THRESHOLD, percent_change
    
    except Exception as e:
        print(f"Error checking price change: {e}")
    
    return False, 0