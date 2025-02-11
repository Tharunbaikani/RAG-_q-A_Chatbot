

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
                {"role": "system", "content": "You are an AI assistant and your name is Black Hole Created by Tharun."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
            ]
        )

        ai_response = response.choices[0].message.content if response.choices else "Error generating response."

        return {"response": ai_response}
    
    except Exception as e:
        return {"response": f"Error processing query: {str(e)}"}





# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.middleware.cors import CORSMiddleware
# import os
# import shutil
# from dotenv import load_dotenv
# from langchain.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import Chroma
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.chat_models import ChatOpenAI
# from langchain.schema import HumanMessage, SystemMessage

# # Load environment variables
# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# if not OPENAI_API_KEY:
#     raise ValueError("OpenAI API key is missing. Set it in the .env file.")

# app = FastAPI()

# # Enable CORS for frontend communication
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize LangChain components
# vector_db_path = "vector_db"
# os.makedirs(vector_db_path, exist_ok=True)

# # Initialize the embedding model
# embedding_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

# # Load vector store
# vector_store = Chroma(persist_directory=vector_db_path, embedding_function=embedding_model)

# # OpenAI chat model
# llm = ChatOpenAI(model_name="gpt-3.5-turbo", api_key=OPENAI_API_KEY)


# @app.get("/")
# def read_root():
#     return {"message": "Hello, FastAPI with LangChain is running!"}


# @app.post("/upload/")
# async def upload_pdf(file: UploadFile = File(...)):
#     """Uploads and processes a PDF, storing chunks in the vector database."""
#     temp_dir = "temp"
#     os.makedirs(temp_dir, exist_ok=True)
    
#     file_path = os.path.join(temp_dir, file.filename)
    
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
    
#     # Load and split PDF text
#     loader = PyPDFLoader(file_path)
#     documents = loader.load()
    
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
#     chunks = text_splitter.split_documents(documents)

#     # Add to vector database
#     vector_store.add_documents(chunks)

#     return {"message": "PDF uploaded and processed successfully."}


# @app.post("/query/")
# async def query_rag(query: str = Form(...)):
#     """Handles user queries with retrieval-augmented generation (RAG)."""
#     try:
#         # Retrieve relevant documents
#         docs = vector_store.similarity_search(query, k=3)
#         context = "\n\n".join([doc.page_content for doc in docs]) if docs else "No relevant documents found."

#         # Generate response using OpenAI LLM
#         messages = [
#             SystemMessage(content="You are an AI assistant that answers user queries based on provided context."),
#             HumanMessage(content=f"Context: {context}\n\nQuestion: {query}")
#         ]
        
#         response = llm(messages)
#         ai_response = response.content if response else "Error generating response."

#         return {"response": ai_response}
    
#     except Exception as e:
#         return {"response": f"Error processing query: {str(e)}"}
