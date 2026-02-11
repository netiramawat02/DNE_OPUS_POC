from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config.settings import settings
from typing import List
import os

class RAGEngine:
    def __init__(self, embeddings=None):
        if embeddings:
            self.embeddings = embeddings
        else:
            # Default to OpenAI Embeddings
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                raise ValueError("OpenAI API Key is missing. Please set the OPENAI_API_KEY environment variable.")

            self.embeddings = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_key=api_key
            )

        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def index_documents(self, text: str, source: str):
        """
        Splits text and adds to vector store.
        """
        chunks = self.text_splitter.split_text(text)
        if not chunks:
            return

        documents = [Document(page_content=chunk, metadata={"source": source}) for chunk in chunks]

        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vector_store.add_documents(documents)

    def search(self, query: str, k: int = 3) -> List[Document]:
        """
        Retrieves relevant documents.
        """
        if not self.vector_store:
            return []
        return self.vector_store.similarity_search(query, k=k)

    def clear(self):
        """
        Clears the in-memory index.
        """
        self.vector_store = None
