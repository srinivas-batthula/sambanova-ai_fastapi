from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import re


# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

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
async def fetch(q: str = 'false', request: ChatRequest):
    try:
        client = get_openai_client()

        response = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": (q=='false') ? "You are an AI assistant for a blogging site ~Verseify developed by Srinivas. Now give the response in a normal format { not give title or hashtags or content, etc}." : "You are an AI-powered blog assistant for the platform ~Verseify (developed by Srinivas Batthula). Given a topic, generate an **SEO-friendly 5-word title**, **4 trending and keyword-rich hashtags**, and a **10-word engaging blog content snippet**  in separate blocks **(strictly, provide the response only in this specified format only, but AtLast, Ask a question to engage the user)**,,,    with real-world and current updates on the topic given by the user. Ensure content is relevant, fresh, and attention-grabbing."},
                {"role": "user", "content": request.userInput}
            ],
            temperature=0.1,
            top_p=0.1
        )
        
                                                # Do these Conversions at the Frontend-Side....
        # Extract title
        title_match = re.search(r'\*\*SEO-friendly 5-word title:\*\* "(.*?)"', response.choices[0].message.content)
        title = title_match.group(1) if title_match else None

        # Extract hashtags
        hashtags_list = re.findall(r'#\w+', response.choices[0].message.content)
        hashtags = " ".join(hashtags_list)

        # Extract content snippet
        content_match = re.search(r'\*\*10-word engaging blog content snippet:\*\* "(.*?)"', response.choices[0].message.content)
        content = content_match.group(1) if content_match else None


        return {"response": response.choices[0].message.content, "hashtags": hashtags, "content": content, 'title': title}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

