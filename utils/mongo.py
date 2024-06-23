from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
def insert(result, file_id):
    uri = os.getenv("MONGO_URL")
    client = MongoClient(uri)
    
    # specify db and collection
    db = client.whisper
    collection = db.whisper
    
    # append file_id to the result dictionary
    result['file_id'] = file_id
    
    # insert 
    collection.insert_one(result)
    client.close()
    
def retrieve(file_id):
    uri = os.getenv("MONGO_URL")
    client = MongoClient(uri)
    
    # specify db and collection
    db = client.whisper
    collection = db.whisper
    
    result = collection.find_one({'file_id': file_id})
    
    client.close()
    
    return result