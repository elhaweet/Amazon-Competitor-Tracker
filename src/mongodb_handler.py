from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = "price_tracker_db"
COLLECTION_NAME = "price_history"

class MongoDBHandler:
    """Handler for MongoDB operations"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.is_connected = False
        
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]
            
            # Test connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
            self.is_connected = True
            return True
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            self.is_connected = False
            return False
    
    def insert_price_data(self, price_document):
        """Insert price data into MongoDB collection"""
        if not self.is_connected:
            if not self.connect():
                return None
        
        try:
            result = self.collection.insert_one(price_document)
            print(f"Price data saved to MongoDB with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            print(f"Error inserting data into MongoDB: {e}")
            return None
    
    def get_previous_prices(self, limit=2):
        """Get the most recent price entries"""
        if not self.is_connected:
            if not self.connect():
                return []
        
        try:
            return list(self.collection.find(
                {"price_numeric": {"$ne": None}},
                sort=[("timestamp", -1)],
                limit=limit
            ))
        except Exception as e:
            print(f"Error retrieving data from MongoDB: {e}")
            return []

# Create a singleton instance
mongodb_handler = MongoDBHandler()


def save_price_to_mongodb(price_value, price_string, product_name, discount, bought_30_days, rating, num_ratings, timestamp):
    """
    Save the price data to MongoDB.
    """
    price_data = {
        'timestamp': timestamp,
        'product_name': product_name,
        'price': price_string,
        'price_numeric': price_value,
        'discount': discount,
        'bought_30_days': bought_30_days,
        'rating': rating,
        'num_ratings': num_ratings
    }
    
    try:
        mongodb_handler.db.prices.insert_one(price_data)
        print(f"Successfully saved price data to MongoDB")
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")