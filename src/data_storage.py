import os
import csv
import datetime
from config import BASE_URL
from src.mongodb_handler import mongodb_handler

# Constants
# Define the CSV filename
CSV_FILENAME = "competitor_history.csv"

def save_price_to_csv(price_value, price_string, product_name, discount, rating, num_ratings, timestamp):
    """
    Save the price data to a CSV file.
    
    Args:
        price_value (float): Numeric price value for calculations
        price_string (str): Original price string with currency
        product_name (str): Name of the product
        discount (str): Discount percentage if available
        rating (str): Product rating
        num_ratings (str): Number of ratings
        timestamp (datetime): When the price was checked
    """
    file_exists = os.path.isfile(CSV_FILENAME)
    
    with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = ['timestamp', 'product_name', 'price', 'price_numeric', 'discount', 'rating', 'num_ratings']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'product_name': product_name,
            'price': price_string,
            'price_numeric': price_value,
            'discount': discount,
            'rating': rating,
            'num_ratings': num_ratings
        })

def save_price_to_mongodb(price_value, price_string, product_name, discount, rating, num_ratings, timestamp):
    """
    Save the price data to MongoDB and CSV.
    
    Args:
        price_value (float): Numeric price value for calculations
        price_string (str): Original price string with currency
        product_name (str): Name of the product
        discount (str): Discount percentage if available
        rating (str): Product rating
        num_ratings (str): Number of ratings
        timestamp (datetime): When the price was checked
    """
    from src.mongodb_handler import mongodb_handler
    
    # Save to CSV first
    save_price_to_csv(price_value, price_string, product_name, discount, rating, num_ratings, timestamp)
    
    # Then save to MongoDB
    price_data = {
        'timestamp': timestamp,
        'product_name': product_name,
        'price': price_string,
        'price_numeric': price_value,
        'discount': discount,
        'rating': rating,
        'num_ratings': num_ratings
    }
    
    mongodb_handler.insert_price_data(price_data)  # Changed from insert_price to insert_price_data

def save_price_to_csv(price_value, price_string, product_name, discount, bought_30_days=None, rating=None, num_ratings=None, timestamp=None):
    """
    Save the price data to a CSV file.
    
    Args:
        price_value (float): Numeric price value for calculations
        price_string (str): Original price string with currency
        product_name (str): Name of the product
        discount (str): Discount percentage if available
        bought_30_days (str, optional): Number of items bought in last 30 days
        rating (float, optional): Product rating
        num_ratings (int, optional): Number of ratings
        timestamp (datetime, optional): When the price was checked
    """
    file_exists = os.path.isfile(CSV_FILENAME)
    
    with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = [
            'timestamp', 'product_name', 'price', 'price_numeric', 
            'discount', 'bought_30_days', 'rating', 'num_ratings'
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'product_name': product_name,
            'price': price_string,
            'price_numeric': price_value,
            'discount': discount,
            'bought_30_days': bought_30_days or 'N/A',
            'rating': rating or 'N/A',
            'num_ratings': num_ratings or 'N/A'
        })