import sys
sys.path.append('C:\\Users\\sande\\OneDrive\\Desktop\\cropwise\\backend\\.venv\\Lib\\site-packages')

from utils.mongo_config import get_db
import datetime

def seed_farmers():
    db = get_db()
    farmers_collection = db["farmers"]

    # Clear existing data
    farmers_collection.delete_many({})

    # Sample farmer data
    farmers = [
        {
            "name": "John Doe",
            "location": {
                "type": "Point",
                "coordinates": [ -74.0060, 40.7128 ]
            },
            "crops": ["wheat", "corn"],
            "soil_type": "loam",
            "created_at": datetime.datetime.utcnow()
        },
        {
            "name": "Jane Smith",
            "location": {
                "type": "Point",
                "coordinates": [ -122.4194, 37.7749 ]
            },
            "crops": ["rice", "sugarcane"],
            "soil_type": "clay",
            "created_at": datetime.datetime.utcnow()
        }
    ]

    # Insert data
    farmers_collection.insert_many(farmers)
    print("Seeded 'farmers' collection with 2 documents.")

if __name__ == "__main__":
    seed_farmers()