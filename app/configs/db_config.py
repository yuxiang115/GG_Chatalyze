from pymongo import MongoClient
import os
import mysql.connector
from dotenv import load_dotenv
load_dotenv()



# Database connection configuration
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "mysql"),
    "user": os.getenv("MYSQL_USER", "gg_chatalyze"),
    "password": os.getenv("MYSQL_PASSWORD", "gg_chatalyze"),
    "database": os.getenv("MYSQL_DATABASE", "gg_chatalyze"),
}


def get_mysql_connection():
    """Get a connection from the pool."""
    connection = mysql.connector.connect(host = DB_CONFIG["host"], user = DB_CONFIG["user"], password = DB_CONFIG["password"], database = DB_CONFIG["database"])
    return connection

mongodb_client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongodb:27017"))
