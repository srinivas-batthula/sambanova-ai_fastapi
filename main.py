from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.extension import Limiter
from fastapi.requests import Request
from fastapi.responses import JSONResponse



# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )


# Enable CORS (Allow all origins, for testing purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Model for request validation
class ChatRequest(BaseModel):
    userInput: str

# Function to initialize OpenAI client
def get_openai_client():
    apiKey = os.getenv("AI_API_KEY")
    baseUrl = os.getenv("AI_BASE_URL")

    if not apiKey or not baseUrl:
        raise HTTPException(status_code=500, detail="OpenAI API key or Base URL not set")

    return openai.OpenAI(api_key=apiKey, base_url=baseUrl)


# Root Route
@app.get("/")
def root():
    return {"message": "API is live."}

# Test Route (Alias for Root)
@app.get("/test")
def test():
    return root()


# Verseify-Chatbot Route
@app.post("/verseify_ai")
@limiter.limit("5/minute")  # 5 requests per minute per IP
async def fetch(request: Request, data: ChatRequest, q: str = 'false'):
    try:
        client = get_openai_client()
        
        system_message = ""
        if(q=='false'):
            system_message = "You are an AI assistant for a blogging site ~Verseify developed by Srinivas Batthula. Now give the response in a normal format as like how chatgpt, gemini, etc gives... {/Note: Do not give it in format of title or hashtags or content, etc/}, AtLast, Ask a question to engage the user."
        else:
            system_message = "You are an AI-powered blog assistant for the platform ~Verseify (developed by Srinivas Batthula). Given a topic, generate an **SEO-friendly 5-word title**, **4 trending and keyword-rich hashtags**, and a **10-word engaging blog content snippet** in separate blocks **(strictly, provide the response only in this specified format only, but AtLast, Ask a question to engage the user)**,,,    with real-world and current updates on the topic given by the user. Ensure content is relevant, fresh, and attention-grabbing."

        response = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": data.userInput}
            ],
            temperature=0.1,
            top_p=0.1
        )

        return {"response": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

