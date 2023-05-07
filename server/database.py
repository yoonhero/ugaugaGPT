from pymongo import MongoClient

import os
from dotenv import load_dotenv

load_dotenv(".env")

MONGODB_URL = os.getenv("MONGODB_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

client = MongoClient(MONGODB_URL)
db = client.ugauga