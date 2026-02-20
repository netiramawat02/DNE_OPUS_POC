from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
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
            # Use free HuggingFace embeddings (no API key needed)
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL
            )

        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def index_documents(self, text: str, source: str, metadata: dict = None) -> bool:
        """
        Splits text and adds to vector store.
        Returns True if documents were indexed, False otherwise.
        """
        chunks = self.text_splitter.split_text(text)
        if not chunks:
            return False

        doc_metadata = {"source": source}
        if metadata:
            doc_metadata.update(metadata)

        documents = [Document(page_content=chunk, metadata=doc_metadata) for chunk in chunks]

        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vector_store.add_documents(documents)
        return True

    @property
    def is_empty(self) -> bool:
        """Checks if the vector store is empty."""
        return self.vector_store is None

    def search(self, query: str, k: int = 3, filter: dict = None) -> List[Document]:
        """
        Retrieves relevant documents.
        """
        if self.is_empty:
            return []
        return self.vector_store.similarity_search(query, k=k, filter=filter)

    def clear(self):
        """
        Clears the in-memory index.
        """
        self.vector_store = None