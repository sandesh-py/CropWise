import sys
sys.path.append('C:\\Users\\sande\\OneDrive\\Desktop\\cropwise\\backend\\.venv\\Lib\\site-packages')

from services.vector_db import get_vector_db

def seed_vector_database():
    """Seed the vector database with agricultural knowledge"""
    
    # Get the vector database instance
    vector_db = get_vector_db()
    
    # Add some additional agricultural knowledge
    additional_docs = [
        {
            "text": "Tomatoes require warm temperatures (20-28°C) and well-drained soil. They need consistent watering but avoid overhead watering to prevent diseases.",
            "metadata": {"topic": "crop_cultivation", "crop": "tomato"}
        },
        {
            "text": "Potatoes grow best in cool climates (15-20°C) with loose, well-drained soil. They require hilling to prevent greening of tubers.",
            "metadata": {"topic": "crop_cultivation", "crop": "potato"}
        },
        {
            "text": "Cotton requires long growing seasons with temperatures above 21°C. It needs well-drained soil and is sensitive to frost.",
            "metadata": {"topic": "crop_cultivation", "crop": "cotton"}
        },
        {
            "text": "Green manure crops like legumes and grasses improve soil fertility when plowed under. They add organic matter and fix nitrogen.",
            "metadata": {"topic": "farming_methods", "method": "green_manure"}
        },
        {
            "text": "Mulching helps retain soil moisture, suppress weeds, and regulate soil temperature. Organic mulches also improve soil structure.",
            "metadata": {"topic": "farming_methods", "method": "mulching"}
        }
    ]
    
    # Add documents to the vector database
    for doc in additional_docs:
        vector_db.add_document(doc["text"], doc["metadata"])
    
    print(f"Successfully seeded vector database with {len(additional_docs)} additional documents.")
    
    # Verify by searching
    results = vector_db.search("tomato cultivation", top_k=2)
    print(f"\nVerification search for 'tomato cultivation':")
    for i, result in enumerate(results):
        print(f"{i+1}. {result['text'][:100]}... (similarity: {result['similarity']:.2f})")

if __name__ == "__main__":
    seed_vector_database()