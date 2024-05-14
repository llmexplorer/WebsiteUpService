from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2 import sql
import requests
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "your_username"
DB_PASSWORD = "postgres"
DB_NAME = "wus"

# Connect to the database
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    conn.autocommit = True
    cursor = conn.cursor()
except psycopg2.Error as e:
    logger.error(f"Error connecting to the database: {e}")
    raise

# Helper function to get all unique URLs from the database
def get_all_sites():
    try:
        cursor.execute("SELECT url FROM sites;")
        return [row[0] for row in cursor.fetchall()]
    except psycopg2.Error as e:
        logger.error(f"Error retrieving URLs from the database: {e}")
        raise

# Dictionary to store URL and status
all_sites = {url: False for url in get_all_sites()}

# Function to check URL status
def check_url(url):
    if url in all_sites:
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.warning(f"Error checking URL {url}: {e}")
            return False
    return False

@app.get("/url_up/{url}")
def url_up(url: str):
    status = all_sites.get(url, False)
    return {"url": url, "status": status}

@app.post("/register_site/{url}")
def register_site(url: str):
    try:
        cursor.execute(
            "INSERT INTO sites (url, creation_date) VALUES (%s, NOW()) ON CONFLICT DO NOTHING;",
            (url,)
        )
        all_sites[url] = check_url(url)  # Initialize and check the URL
        return {"url": url, "registered": True}
    except psycopg2.Error as e:
        logger.error(f"Error registering URL {url}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/uptime/{url}")
def uptime(url: str):
    try:
        cursor.execute(
            "SELECT response_code, creation_time FROM status_check WHERE url = %s;",
            (url,)
        )
        return cursor.fetchall()
    except psycopg2.Error as e:
        logger.error(f"Error retrieving uptime data for URL {url}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/check_all_sites")
def check_all_sites():
    results = []
    for url in list(all_sites.keys()):
        status = check_url(url)
        all_sites[url] = status
        try:
            cursor.execute(
                "INSERT INTO status_check (url, creation_time, response_code) VALUES (%s, NOW(), %s);",
                (url, 200 if status else 500)
            )
            results.append({"url": url, "status": status})
        except psycopg2.Error as e:
            logger.error(f"Error inserting status check for URL {url}: {e}")
    return results