import os

from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Read MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Create MongoDB client
client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)

# Select database
database = client[DATABASE_NAME]


# Check database connection
def check_database_connection():
    try:
        client.admin.command("ping")
        print("MongoDB connected successfully!")
    except Exception as error:
        print("MongoDB connection failed:", error)
        raise
