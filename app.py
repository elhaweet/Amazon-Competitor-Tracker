from flask import Flask, jsonify, request
import os
import requests
from dotenv import load_dotenv
import json
import time

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

@app.route('/')
def home():
    return jsonify({
        "status": "Competitor Tracker API is running",
        "endpoints": {
            "/status": "Get the status and latest results of the scraper",
            "/run": "Trigger a scrape on the main server"
        }
    })

@app.route('/status')
def status():
    return jsonify(latest_results)

@app.route('/run', methods=['GET'])
def run_scraper():
    try:
        # In this lightweight version, we would typically call an external API
        # that hosts the full scraper functionality
        
        # For demonstration, we'll just update the status
        latest_results["status"] = "Running on external server"
        latest_results["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return jsonify({
            "status": "success",
            "message": "Scraper job triggered on external server"
        })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

# Vercel serverless function handler
def handler(request, context):
    return app(request, context)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)