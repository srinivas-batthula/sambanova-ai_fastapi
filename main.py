from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import io

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
        return {"Success": "API is live."}
    except Exception as e:
        return {"Failed": str(e)}

# Function to process image and extract text
def extract_text_from_image(image: UploadFile) -> str:
    try:
        image_data = Image.open(io.BytesIO(image.file.read()))
        extracted_text = pytesseract.image_to_string(image_data)
        return extracted_text.strip()
    except Exception as e:
        return f"Error processing image: {str(e)}"

# Chatbot with text input
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
            messages=[
                {"role": "system", "content": "You are a helpful Health Assistant assistant"},
                {"role": "user", "content": userInput}
            ],
            temperature=0.1,
            top_p=0.1
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(e)
        return {"error": str(e)}

# Endpoint for image upload
@app.post("/upload-image")
async def upload_image(image: UploadFile = File(...)):
    extracted_text = extract_text_from_image(image)
    
    if not extracted_text:
        return {"error": "No text extracted from image."}
    
    apiKey = os.getenv('AI_API_KEY')
    baseUrl = os.getenv('AI_BASE_URL')
    
    try:
        client = openai.OpenAI(
            api_key=apiKey,
            base_url=baseUrl
        )
        
        response = client.chat.completions.create(
            model='Meta-Llama-3.1-8B-Instruct',
            messages=[
                {"role": "system", "content": "You are a helpful Health Assistant assistant."},
                {"role": "user", "content": extracted_text}
            ],
            temperature=0.1,
            top_p=0.1
        )
        
        return {"summary": response.choices[0].message.content}
    
    except Exception as e:
        print(e)
        return {"error": str(e)}

@app.get("/test")
def hello():
    try:
        return {"Success": "API is live."}
    except Exception as e:
        return {"Failed": str(e)}
