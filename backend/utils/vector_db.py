import chromadb

client = chromadb.Client()
collection = client.get_or_create_collection("cropwise_memory")

def store_in_vector_db(text, embedding):
    collection.add(documents=[text], embeddings=[embedding])