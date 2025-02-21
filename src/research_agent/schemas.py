from pydantic import BaseModel
from langchain_core.documents import Document
from typing_extensions import List, TypedDict


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


class fileschema(BaseModel):
    file_name: str


class queryschema(BaseModel):
    query: str
