import os
from typing import Optional
from core.config import Settings
try:
    from services.vector_db import get_vector_db
    vector_db = get_vector_db()
except (ImportError, Exception):
    # Fallback if vector_db is not available
    vector_db = None

# Prefer OpenAI if key is present; gracefully fallback to Gemini if configured
try:
    import openai  # type: ignore
except Exception:
    openai = None

try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None

class ChatService:
    def __init__(self):
        self.settings = Settings()
        self.use_openai = bool(self.settings.openai_api_key and openai)
        self.use_gemini = bool(self.settings.gemini_api_key and genai)
        self.gemini_model = None  # Initialize to None
        
        if self.use_openai:
            try:
                openai.api_key = self.settings.openai_api_key
            except Exception:
                self.use_openai = False
        
        if self.use_gemini:
            try:
                genai.configure(api_key=self.settings.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
            except Exception:
                self.use_gemini = False
                self.gemini_model = None

    def _build_context(self, prompt: str) -> str:
        try:
            if vector_db:
                context_results = vector_db.search(prompt, k=3)
                if context_results:
                    lines = ["Based on agricultural knowledge:"]
                    for i, result in enumerate(context_results, 1):
                        lines.append(f"{i}. {result}")
                    return "\n".join(lines) + "\n\n"
        except Exception:
            pass
        return ""

    def generate_response(self, prompt: str) -> str:
        try:
            context = self._build_context(prompt)
            
            # Enhanced system prompt with specific focus on Mysuru region
            system_prompt = (
                "You are AgroBot, a specialized AI agriculture assistant for farmers in Mysuru, Karnataka, India. "
                "Your expertise is LIMITED to:\n"
                "- Crop cultivation (ragi, maize, sugarcane, paddy)\n"
                "- Soil management and NPK fertilizers\n"
                "- Irrigation methods (drip, sprinkler, flood, rainfed)\n"
                "- Weather patterns in Mysuru region\n"
                "- Pest and disease management\n"
                "- Crop yield optimization\n"
                "- Agricultural best practices for Karnataka\n\n"
                "IMPORTANT RULES:\n"
                "1. If asked about non-agricultural topics, respond: 'I specialize only in farming and agriculture. "
                "Please ask me about crops, soil, weather, irrigation, or pest management.'\n"
                "2. Always provide practical, actionable advice specific to Mysuru region.\n"
                "3. Keep answers concise (2-3 sentences maximum).\n"
                "4. Use simple language that farmers can understand.\n"
                "5. Reference specific crops grown in Mysuru when relevant (ragi, maize, sugarcane, paddy)."
            )

            if self.use_openai:
                # Use OpenAI ChatCompletion API (gpt-3.5-turbo by default)
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt if not context else f"{context}User question: {prompt}"},
                        ],
                        max_tokens=180,
                        temperature=0.4,
                    )
                    return response.choices[0].message["content"].strip()
                except Exception as e:
                    # Fall through to Gemini if configured
                    pass

            if self.use_gemini and self.gemini_model:
                try:
                    enhanced_prompt = (
                        f"{system_prompt}\n\n{context}User question: {prompt}\n\n"
                        "Provide a clear, helpful response based on the context above and your agricultural expertise."
                    )
                    result = self.gemini_model.generate_content(enhanced_prompt)
                    return result.text
                except Exception as e:
                    print(f"Gemini API error: {e}, falling back to rule-based responses")
                    # Fall through to rule-based responses

            # Enhanced fallback: rule-based responses with Mysuru-specific knowledge
            lower = prompt.lower()
            
            # Check if question is off-topic
            off_topic_keywords = ["movie", "sports", "politics", "technology", "coding", "programming", 
                                 "music", "game", "entertainment", "news", "stock", "crypto", "bitcoin"]
            if any(keyword in lower for keyword in off_topic_keywords):
                return "I specialize only in farming and agriculture for Mysuru region. Please ask me about crops, soil, weather, irrigation, or pest management."
            
            # Farming-related responses
            if "soil" in lower or "fertility" in lower or "npk" in lower:
                return "For Mysuru soils, test pH regularly (ideal: 6.0-7.5). Red sandy loam is common. Apply NPK based on crop needs: Ragi (N:100, P:50, K:70), Maize (N:120, P:60, K:80), Paddy (N:140, P:70, K:90)."
            
            elif "weather" in lower or "rain" in lower or "temperature" in lower:
                return "Mysuru has moderate climate (22-32°C). Annual rainfall ~800mm. Plan irrigation during dry spells. Monsoon season (June-September) is crucial for rainfed crops."
            
            elif "pest" in lower or "disease" in lower or "insect" in lower:
                return "Use integrated pest management: monitor regularly, use resistant crop varieties, apply organic pesticides first. For Mysuru, common pests include stem borers (ragi/maize) and leaf folders (paddy)."
            
            elif "crop" in lower or "yield" in lower or "harvest" in lower:
                return "Popular Mysuru crops: Ragi (2-3 tons/ha), Maize (4-6 tons/ha), Sugarcane (70-90 tons/ha), Paddy (3-5 tons/ha). Yield depends on NPK levels, irrigation, and weather. Use our prediction tool for accurate estimates."
            
            elif "irrigation" in lower or "water" in lower:
                return "Mysuru farmers use: Drip (best for water efficiency), Sprinkler (good coverage), Flood (traditional for paddy), Rainfed (common for ragi). Drip irrigation can save 30-50% water."
            
            elif "fertilizer" in lower or "nutrient" in lower:
                return "NPK fertilizers: Nitrogen (N) for growth, Phosphorus (P) for roots, Potassium (K) for disease resistance. Apply based on soil test. For Mysuru: balanced NPK ratios work best."
            
            elif "ragi" in lower or "finger millet" in lower:
                return "Ragi (finger millet) is drought-resistant, ideal for Mysuru. Requires 500-900mm rainfall, N:100, P:50, K:70 kg/ha. Grows well in red sandy loam. Yield: 2-3 tons/ha."
            
            elif "maize" in lower or "corn" in lower:
                return "Maize needs 700-1100mm rainfall, N:120, P:60, K:80 kg/ha. Best in black cotton or red sandy loam. Requires good drainage. Yield: 4-6 tons/ha in Mysuru."
            
            elif "sugarcane" in lower:
                return "Sugarcane is high-value crop for Mysuru. Needs 1000-1500mm rainfall, N:150, P:60, K:100 kg/ha. Prefers black cotton soil. Requires consistent irrigation. Yield: 70-90 tons/ha."
            
            elif "paddy" in lower or "rice" in lower:
                return "Paddy needs 1000-1600mm rainfall, N:140, P:70, K:90 kg/ha. Requires standing water during growth. Best in clay or black cotton soil. Yield: 3-5 tons/ha in Mysuru."
            
            elif "when" in lower and ("plant" in lower or "sow" in lower):
                return "Mysuru planting seasons: Kharif (June-July with monsoon), Rabi (October-November). Ragi and maize: Kharif. Paddy: Kharif. Sugarcane: year-round with irrigation."
            
            elif "how" in lower and ("grow" in lower or "cultivate" in lower):
                return "For crop cultivation in Mysuru: 1) Test soil NPK and pH, 2) Choose suitable crop for your soil type, 3) Apply recommended fertilizers, 4) Ensure proper irrigation, 5) Monitor for pests. Use our prediction tool for personalized advice."
            
            # Default response for farming-related but unclear questions
            return "I can help with farming topics for Mysuru region. Ask me about: specific crops (ragi, maize, sugarcane, paddy), soil management, NPK fertilizers, irrigation methods, weather patterns, or pest control. Be specific for better answers!"
        except Exception as e:
            return f"An error occurred: {str(e)}"

chat_service = ChatService()