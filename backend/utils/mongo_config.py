from pymongo import MongoClient

# In a real implementation, you would use a secure way to store your credentials
MONGO_URI = "mongodb://localhost:27017/"
CLIENT = MongoClient(MONGO_URI)
DB = CLIENT["cropwise"]

def get_db():
    return DB