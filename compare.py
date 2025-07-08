# compare.py

from pymongo import MongoClient
from config import CONFIG

client = MongoClient(CONFIG["MONGO_URI"])
db = client[CONFIG["DB_NAME"]]
collection = db[CONFIG["COLLECTION_NAME"]]

def get_new_jobs(scraped_jobs):
    new_jobs = []

    for job in scraped_jobs:
        if not collection.find_one(job):  # check if already exists
            new_jobs.append(job)
            collection.insert_one(job)     # add to DB if new

    return new_jobs
