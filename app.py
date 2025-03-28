import asyncio
import threading
import time
from flask import Flask, jsonify
from dotenv import load_dotenv

# Import your existing functionality
from competitor_tracker import track_price
from src.mongodb_handler import mongodb_handler

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Global variable to store the latest scraping results
latest_results = {
    "last_run": None,
    "product_name": None,
    "price": None,
    "discount": None,
    "rating": None,
    "status": "Not started"
}

def background_scraper():
    """
    Background thread function that runs the scraper every 10 seconds
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    while True:
        try:
            latest_results["status"] = "Running"
            # Run the track_price function
            result = loop.run_until_complete(track_price(single_run=True))
            
            if result:
                latest_results["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
                latest_results["product_name"] = result.get("product_name")
                latest_results["price"] = result.get("price")
                latest_results["discount"] = result.get("discount")
                latest_results["rating"] = result.get("rating")
                latest_results["status"] = "Success"
            else:
                latest_results["status"] = "No data returned"
                
        except Exception as e:
            latest_results["status"] = f"Error: {str(e)}"
            
        # Wait for 10 seconds before the next run
        time.sleep(10)

@app.route('/')
def home():
    return jsonify({
        "status": "Competitor Tracker API is running",
        "endpoints": {
            "/status": "Get the status and latest results of the scraper",
            "/run": "Trigger a scrape immediately"
        }
    })

@app.route('/status')
def status():
    return jsonify(latest_results)

@app.route('/run', methods=['GET'])
def run_scraper():
    try:
        # Connect to MongoDB if not already connected
        if not mongodb_handler.is_connected:
            mongodb_handler.connect()
            
        # Create a new event loop for this request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the track_price function once
        result = loop.run_until_complete(track_price(single_run=True))
        
        if result:
            return jsonify({
                "status": "success",
                "data": result
            })
        else:
            return jsonify({
                "status": "error",
                "message": "No data returned from scraper"
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    # Start the background scraper thread
    scraper_thread = threading.Thread(target=background_scraper, daemon=True)
    scraper_thread.start()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=8000)