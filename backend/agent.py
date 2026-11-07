import os
import json
import chromadb
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from chromadb.utils import embedding_functions

load_dotenv()

class SchemeAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash", 
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1 
        )
        
        # --- DYNAMIC DATABASE PATH FIX ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, "..", "chroma_db")
        
        self.client = chromadb.PersistentClient(path=db_path)
        # ---------------------------------

        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_collection(
            name="india_schemes", 
            embedding_function=self.embedding_func
        )

    def find_matches(self, user_profile: str):
        # 1. Search the database for the top 5 most relevant schemes
        results = self.collection.query(
            query_texts=[user_profile],
            n_results=5
        )
        
        context = "\n\n".join(results['documents'][0])

        # 2. Instruct Gemini to act as a strict evaluator
        prompt = PromptTemplate.from_template(
            """
            You are an expert civic-tech AI data evaluator. 
            Compare the USER PROFILE against the SCHEME CONTEXT. 
            Only return schemes where the user explicitly qualifies based on the rules.

            USER PROFILE: {profile}

            SCHEME CONTEXT: {context}

            Respond ONLY with a valid JSON object matching this exact structure:
            {{
                "matches": [
                    {{
                        "name": "Official Scheme Name",
                        "status": "Eligible / Conditionally Eligible",
                        "reasoning": "Clear point-by-point eligibility matching details",
                        "benefits": "What financial or material aid do they get exactly?",
                        "documents": "Comma-separated list of required paperwork",
                        "how_to_apply": "Step-by-step application pipeline guidance",
                        "url": "Official portal URL link string"
                    }}
                ]
            }}
            """
        )
        
        response = self.llm.invoke(prompt.format(profile=user_profile, context=context))
        
        # Clean the JSON output
        clean_text = response.content.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean_text)
        except:
            return {"matches": []}

agent = SchemeAgent()