from fastapi import FastAPI, File, UploadFile
from .pdf_parser import extract_text_from_pdf
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from research_agent.schemas import fileschema, queryschema
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from research_agent.prompt import *

from dotenv import load_dotenv

load_dotenv()

import os

api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=api_key, temperature=0.5)

app = FastAPI()
# FAISS database path and embedding model
FAISS_DB_PATH = "vector_db"
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)  # Replace with your actual embedding model

# Load FAISS only once
# memory = ConversationBufferMemory(k=5, memory_key="chat_history", return_messages=True)

# prompt = ChatPromptTemplate(
#     [
#         MessagesPlaceholder(variable_name="chat_history"),
#         HumanMessagePromptTemplate.from_template("{prompt_template}"),
#     ]
# )

# PROMPT = PromptTemplate(
#     template=prompt_template, input_variables=["context", "question"]
# )
# chain_type_kwargs = {"prompt": prompt}

# chain_type_kwargs = {"prompt": PROMPT}


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


os.makedirs(FAISS_DB_PATH, exist_ok=True)


@app.get("/")
def hello():
    return {"message": "Hello, World!"}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return {"filename": file.filename, "message": "File uploaded successfully"}


@app.post("/process/")
async def process_document(filename: fileschema):
    file_path = os.path.join(UPLOAD_DIR, filename.file_name)

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    text = extract_text_from_pdf(file_path)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    text_chunks = text_splitter.split_text(text)

    faiss_db = FAISS.from_texts(text_chunks, embedding_model)

    faiss_db.save_local(FAISS_DB_PATH)

    return {"message": "Document processed successfully and stored in vector DB"}


@app.get("/query/")
async def query_document(question: queryschema):
    faiss_db = FAISS.load_local(
        FAISS_DB_PATH, embedding_model, allow_dangerous_deserialization=True
    )
    # retriever = faiss_db.as_retriever()
    # retriever = faiss_db.similarity_search(question.query, k=5)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="refine",
        retriever=faiss_db.as_retriever(search_kwargs={"k": 5}),
    )
    # qa_chain = RetrievalQA.from_chain_type(
    #     llm=llm,
    #     chain_type="refine",  # Other options: "map_reduce", "refine"
    #     retriever=retriever,  # Pass the retriever object
    # )
    # docs = faiss_db.similarity_search(question.query, k=3)
    response = qa_chain.run(question.query)
    print(response)

    return {"result": response}
