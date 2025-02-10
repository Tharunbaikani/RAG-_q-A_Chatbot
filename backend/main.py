

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import chromadb
import openai
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Get API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is missing. Set it in the .env file.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is running!"}


client = OpenAI(api_key=OPENAI_API_KEY)
chroma_client = chromadb.PersistentClient(path="db")
collection = chroma_client.get_or_create_collection(name="documents")

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    text = extract_text_from_pdf(file_path)
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    
    for i, chunk in enumerate(chunks):
        collection.add(
            ids=[f"{file.filename}-{i}"],
            documents=[chunk]
        )

    return {"message": "PDF uploaded and processed successfully."}

@app.post("/query/")
async def query_rag(query: str = Form(...)):
    try:
        results = collection.query(query_texts=[query], n_results=3)

        if "documents" not in results or not results["documents"][0]:
            return {"response": "No relevant documents found."}

        context = " ".join([doc for doc in results["documents"][0] if doc])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
            ]
        )

        ai_response = response.choices[0].message.content if response.choices else "Error generating response."

        return {"response": ai_response}
    
    except Exception as e:
        return {"response": f"Error processing query: {str(e)}"}


