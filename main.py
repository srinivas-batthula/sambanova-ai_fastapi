# Backend Code {main.py}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv() 



class ChatRequest(BaseModel):
    userInput: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def start():
    try:
        return {"Success":"API is live."}
    except Exception as e:
        return {"Failed":str(e)}


# Src code
@app.post("/chatbot")
async def fetch(request: ChatRequest):
    userInput = request.userInput
    
    apiKey = os.getenv('AI_API_KEY')
    baseUrl = os.getenv('AI_BASE_URL')
    
    try:
        client = openai.OpenAI(
            api_key=apiKey,
            base_url=baseUrl
        )
        
        response = client.chat.completions.create(
            model='Meta-Llama-3.1-8B-Instruct',
            messages=[{"role":"system","content":"You are a helpful Health Assistant assistant"},{"role":"user","content":userInput}],
            temperature =  0.1,
            top_p = 0.1
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(e)
        return {"error: ":e}


# Test/Ping to up the API access...
@app.get("/test")
def hello():
    try:
        return {"Success":"API is live."}
    except Exception as e:
        return {"Failed:   -":str(e)}