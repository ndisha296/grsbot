from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Changed to Groq

print("GROQ KEY FOUND:", bool(GROQ_API_KEY))

app = FastAPI(title="GRS Lightweight Chatbot API")

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ REQUEST MODEL ------------------

class ChatRequest(BaseModel):
    message: str
    
    class Config:
        extra = "ignore"

# ------------------ HARD CODED DATA ------------------

qa_data = [
    {
        "keywords": ["grs", "platform", "about", "what is"],
        "answer": "GRS is a sustainability platform that helps users track eco-friendly products and earn eco-points."
    },
    {
        "keywords": ["eco", "points", "earn", "get"],
        "answer": "You earn eco-points by scanning or purchasing eco-friendly products through the GRS app."
    },
    {
        "keywords": ["redeem", "use", "points", "spend"],
        "answer": "Eco-points can be redeemed for discounts or donated to environmental causes."
    },
    {
        "keywords": ["eco", "cred", "wallet", "store"],
        "answer": "Eco-Cred Wallet stores and manages all your earned eco-points."
    }
]

# ------------------ GROQ AI FALLBACK ------------------

def call_ai(user_message: str) -> str:
    if not GROQ_API_KEY:
        return "⚠️ AI API key not configured."

    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""You are GRS Assistant, an eco-sustainability chatbot.
Only answer questions related to GRS features, eco-points, and sustainability.
If the question is unrelated, politely say you can help only with GRS topics.
Answer in simple English, maximum 4 lines."""

    payload = {
        "model": "llama-3.3-70b-versatile",  # Fast and free
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        
        return "⚠️ Could not generate a response. Please try again."
        
    except requests.exceptions.HTTPError as e:
        print(f"Groq HTTP error: {e}")
        print(f"Response: {response.text}")
        return "⚠️ API request failed. Please check your API key."
    except Exception as e:
        print(f"Groq error: {e}")
        return "⚠️ AI service is temporarily unavailable. Please try again later."

# ------------------ CHAT ENDPOINT ------------------

@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message.lower().strip()
    
    # Handle empty messages
    if not user_msg:
        return {"reply": "Please ask me something about GRS and eco-points!"}

    best_score = 0
    best_answer = None

    # 1️⃣ Hardcoded keyword matching
    for item in qa_data:
        score = sum(1 for kw in item["keywords"] if kw in user_msg)

        if score > best_score:
            best_score = score
            best_answer = item["answer"]

    # Use hardcoded answer if score is high enough
    if best_score >= 2:
        return {"reply": best_answer}

    # 2️⃣ AI fallback
    ai_reply = call_ai(req.message)
    return {"reply": ai_reply}

# ------------------ ROOT & FRONTEND ------------------

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the chat frontend"""
    try:
        with open("ui.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body>
                <h1>GRS Chatbot API is running!</h1>
                <p>Frontend not found. Please create index.html in the project folder.</p>
                <p>API endpoint: <a href="/docs">/docs</a></p>
            </body>
        </html>
        """

@app.get("/api")
def api_info():
    return {
        "status": "GRS Chatbot API is running",
        "endpoints": {
            "/": "Chat frontend UI",
            "/chat": "POST - Send a message",
            "/docs": "API documentation"
        }
    }

# ------------------ DEBUG ENDPOINT ------------------

@app.get("/debug")
def debug():
    return {
        "api_key_loaded": bool(GROQ_API_KEY),
        "api_key_length": len(GROQ_API_KEY) if GROQ_API_KEY else 0
    }