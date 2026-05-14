from typing import List, Dict, Any, Optional
import numpy as np
import json
import os
from pathlib import Path

class VectorDatabase:
    """A simple vector database implementation for storing and retrieving agricultural knowledge"""
    
    def __init__(self, data_dir: str = "data/vector_db"):
        self.data_dir = data_dir
        self.vectors_file = os.path.join(data_dir, "vectors.json")
        self.documents_file = os.path.join(data_dir, "documents.json")
        self.vectors = []
        self.documents = []
        self.initialize()
    
    def initialize(self):
        """Initialize the vector database"""
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing data if available
        if os.path.exists(self.vectors_file) and os.path.exists(self.documents_file):
            try:
                with open(self.vectors_file, 'r') as f:
                    self.vectors = json.load(f)
                with open(self.documents_file, 'r') as f:
                    self.documents = json.load(f)
            except Exception as e:
                print(f"Error loading vector database: {e}")
                # Initialize with default agricultural knowledge if loading fails
                self._initialize_default_data()
        else:
            # Initialize with default agricultural knowledge
            self._initialize_default_data()
    
    def _initialize_default_data(self):
        """Initialize with default agricultural knowledge"""
        # Default agricultural knowledge
        default_documents = [
            {
                "id": 1,
                "text": "Rice cultivation requires warm temperatures between 20-35°C and abundant water. It's commonly grown in flooded fields called paddies.",
                "metadata": {"topic": "crop_cultivation", "crop": "rice"}
            },
            {
                "id": 2,
                "text": "Wheat grows best in well-drained soil with moderate rainfall. It requires temperatures between 15-24°C during the growing season.",
                "metadata": {"topic": "crop_cultivation", "crop": "wheat"}
            },
            {
                "id": 3,
                "text": "Maize (corn) needs full sun exposure and grows optimally in temperatures between 18-32°C. It requires consistent moisture throughout the growing season.",
                "metadata": {"topic": "crop_cultivation", "crop": "maize"}
            },
            {
                "id": 4,
                "text": "Organic farming relies on natural inputs and ecological processes rather than synthetic fertilizers and pesticides. It promotes biodiversity and soil health.",
                "metadata": {"topic": "farming_methods", "method": "organic"}
            },
            {
                "id": 5,
                "text": "Drip irrigation delivers water directly to plant roots, minimizing evaporation and runoff. It's highly efficient, saving up to 60% water compared to conventional methods.",
                "metadata": {"topic": "irrigation", "method": "drip"}
            },
            {
                "id": 6,
                "text": "Crop rotation involves growing different types of crops in the same area across seasons. It helps prevent soil depletion and breaks pest cycles.",
                "metadata": {"topic": "farming_methods", "method": "crop_rotation"}
            },
            {
                "id": 7,
                "text": "Nitrogen is essential for leaf growth and protein production in plants. Deficiency symptoms include yellowing of older leaves.",
                "metadata": {"topic": "nutrients", "nutrient": "nitrogen"}
            },
            {
                "id": 8,
                "text": "Phosphorus promotes root development and flowering. It's crucial for energy transfer in plants. Deficiency causes stunted growth and purplish leaves.",
                "metadata": {"topic": "nutrients", "nutrient": "phosphorus"}
            },
            {
                "id": 9,
                "text": "Potassium regulates water uptake and disease resistance in plants. Deficiency appears as scorching along leaf edges.",
                "metadata": {"topic": "nutrients", "nutrient": "potassium"}
            },
            {
                "id": 10,
                "text": "Integrated Pest Management (IPM) combines biological, cultural, physical, and chemical methods to minimize pest damage with the least harm to people and environment.",
                "metadata": {"topic": "pest_management", "method": "ipm"}
            },
            {
                "id": 11,
                "text": "Red sandy loam soil is well-draining and suitable for crops like groundnuts, millets, and vegetables. It benefits from organic matter addition.",
                "metadata": {"topic": "soil_types", "soil": "red_sandy_loam"}
            },
            {
                "id": 12,
                "text": "Black cotton soil (Regur) has high clay content and water retention. It's excellent for cotton, sugarcane, and cereals but requires careful water management.",
                "metadata": {"topic": "soil_types", "soil": "black_cotton"}
            },
            {
                "id": 13,
                "text": "Laterite soil is rich in iron and aluminum but poor in nutrients. It benefits from liming and organic matter addition. Suitable for tree crops and some cereals.",
                "metadata": {"topic": "soil_types", "soil": "laterite"}
            },
            {
                "id": 14,
                "text": "Clay soil has high nutrient content but poor drainage. It works well for rice and certain vegetables when properly managed.",
                "metadata": {"topic": "soil_types", "soil": "clay"}
            },
            {
                "id": 15,
                "text": "FSSAI (Food Safety and Standards Authority of India) sets standards for organic food production, including restrictions on chemical inputs and GMOs.",
                "metadata": {"topic": "regulations", "organization": "fssai"}
            }
        ]
        
        # Create simple vector embeddings (in a real system, use a proper embedding model)
        default_vectors = []
        for doc in default_documents:
            # Create a simple embedding based on word frequencies
            # This is a placeholder - in a real system, use a proper embedding model
            words = doc["text"].lower().split()
            # Simple frequency-based vector (just for demonstration)
            vector = [len(words)]
            default_vectors.append(vector)
        
        self.documents = default_documents
        self.vectors = default_vectors
        
        # Save to files
        self._save_data()
    
    def _save_data(self):
        """Save vector database to disk"""
        with open(self.vectors_file, 'w') as f:
            json.dump(self.vectors, f)
        with open(self.documents_file, 'w') as f:
            json.dump(self.documents, f)
    
    def add_document(self, text: str, metadata: Dict[str, Any] = None) -> int:
        """Add a document to the vector database"""
        doc_id = len(self.documents) + 1
        document = {
            "id": doc_id,
            "text": text,
            "metadata": metadata or {}
        }
        
        # Create a simple embedding (in a real system, use a proper embedding model)
        words = text.lower().split()
        vector = [len(words)]  # Simple placeholder vector
        
        self.documents.append(document)
        self.vectors.append(vector)
        
        # Save updated data
        self._save_data()
        
        return doc_id
        
    def _text_to_vector(self, text: str) -> List[float]:
        """Convert text to vector embedding"""
        # Simple placeholder implementation
        # In a real system, use a proper embedding model
        words = text.lower().split()
        return [len(words)]
        
    def store_farmer_data(self, farmer_data: Dict[str, Any]) -> bool:
        """
        Store farmer-specific data in the vector database for personalized recommendations
        
        Args:
            farmer_data: Dictionary containing farmer data (crops, soil, location, etc.)
            
        Returns:
            bool: Success status
        """
        try:
            # Create a document from farmer data
            document = {
                "id": len(self.documents) + 1,
                "text": f"Farmer data: Growing {farmer_data.get('crop', 'unknown crop')} in {farmer_data.get('soil_type', 'unknown soil')} soil. " +
                       f"NPK values: N={farmer_data.get('nitrogen', 0)}, P={farmer_data.get('phosphorus', 0)}, K={farmer_data.get('potassium', 0)}. " +
                       f"Location: lat={farmer_data.get('latitude', 0)}, lon={farmer_data.get('longitude', 0)}.",
                "metadata": {
                    "type": "farmer_data",
                    "timestamp": farmer_data.get("timestamp", ""),
                    "user_id": farmer_data.get("user_id", "anonymous"),
                    "crop": farmer_data.get("crop", ""),
                    "soil_type": farmer_data.get("soil_type", ""),
                    "location": {
                        "latitude": farmer_data.get("latitude", 0),
                        "longitude": farmer_data.get("longitude", 0)
                    }
                }
            }
            
            # Generate vector embedding for the document
            vector = self._text_to_vector(document["text"])
            
            # Add to database
            self.documents.append(document)
            self.vectors.append(vector)
            
            # Save to disk
            self._save_data()
            
            return True
        except Exception as e:
            print(f"Error storing farmer data: {e}")
            return False
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search the vector database for documents similar to the query
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of matching documents with similarity scores
        """
        if not self.vectors or not self.documents:
            return []
            
        # Convert query to vector
        query_vector = self._text_to_vector(query)
        
        # Calculate similarity scores
        scores = []
        for i, vector in enumerate(self.vectors):
            # Simple cosine similarity approximation
            similarity = self._calculate_similarity(query_vector, vector)
            scores.append((i, similarity))
        
        # Sort by similarity score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results
        results = []
        for i, score in scores[:top_k]:
            document = self.documents[i].copy()
            document["similarity"] = float(score)
            results.append(document)
            
        return results
        
    def _calculate_similarity(self, vec1, vec2):
        """Calculate similarity between two vectors"""
        # Simple placeholder implementation
        # In a real system, use proper vector similarity calculation
        return 0.5 + (abs(vec1[0] - vec2[0]) / 100)  # Normalized similarity score
        
    def _save_data(self):
        """Save vector database to disk"""
        try:
            with open(self.vectors_file, 'w') as f:
                json.dump(self.vectors, f)
            with open(self.documents_file, 'w') as f:
                json.dump(self.documents, f)
        except Exception as e:
            print(f"Error saving vector database: {e}")
            
    def get_recommendations_for_user(self, user_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get personalized recommendations based on user's previous data"""
        user_data = [doc for doc in self.documents if doc["metadata"].get("user_id") == user_id 
                    and doc["metadata"].get("type") == "farmer_data"]
        
        if not user_data:
            return []
            
        # Get the most recent data
        user_data.sort(key=lambda x: x["metadata"].get("timestamp", ""), reverse=True)
        recent_data = user_data[0]
        
        # Find similar crops based on soil type and NPK values
        recommendations = []
        for doc in self.documents:
            if doc["metadata"].get("type") == "crop_recommendation":
                if doc["metadata"].get("soil_type") == recent_data["metadata"].get("soil_type"):
                    recommendations.append({
                        "crop": doc["metadata"].get("crop", ""),
                        "confidence": 0.85,
                        "reason": "Based on your soil type"
                    })
        
        return recommendations[:limit]
        
        # Special handling for organic farming queries
        if "organic" in query_lower or "organic farming" in query_lower:
            # Find documents specifically about organic farming
            organic_results = []
            for i, doc in enumerate(self.documents):
                if doc["metadata"].get("method") == "organic":
                    organic_results.append({
                        "document": doc,
                        "score": 0.95  # High confidence for exact match
                    })
            
            # If we found specific organic farming documents, return them
            if organic_results:
                return organic_results
        
        # Create a simple query vector (in a real system, use the same embedding model)
        words = query_lower.split()
        query_vector = [len(words)]  # Simple placeholder vector
        
        # Calculate similarity scores (in a real system, use cosine similarity)
        scores = []
        for vector in self.vectors:
            # Simple similarity metric (just for demonstration)
            # In a real system, use cosine similarity between proper embeddings
            similarity = 1.0 / (1.0 + abs(vector[0] - query_vector[0]))
            scores.append(similarity)
        
        # Get top-k results
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        results = []
        
        for idx in top_indices:
            results.append({
                "document": self.documents[idx],
                "score": scores[idx]
            })
        
        return results
    
    def get_document_by_id(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """Get a document by its ID"""
        for doc in self.documents:
            if doc["id"] == doc_id:
                return doc
        return None
    
    def filter_by_metadata(self, metadata_filter: Dict[str, Any], top_k: int = None) -> List[Dict[str, Any]]:
        """Filter documents by metadata"""
        results = []
        
        for doc in self.documents:
            match = True
            for key, value in metadata_filter.items():
                if key not in doc["metadata"] or doc["metadata"][key] != value:
                    match = False
                    break
            
            if match:
                results.append(doc)
        
        if top_k is not None:
            results = results[:top_k]
        
        return results

# Singleton instance
_vector_db_instance = None

def get_vector_db() -> VectorDatabase:
    """Get the vector database singleton instance"""
    global _vector_db_instance
    if _vector_db_instance is None:
        data_dir = os.path.join(Path(__file__).parent.parent.parent, "data", "vector_db")
        _vector_db_instance = VectorDatabase(data_dir=data_dir)
    return _vector_db_instance