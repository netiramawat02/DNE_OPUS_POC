from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from rag_engine.vector_store import RAGEngine
from config.settings import settings
from typing import Dict, Any

class ChatEngine:
    def __init__(self, rag_engine: RAGEngine, llm=None):
        self.rag_engine = rag_engine
        if llm:
            self.llm = llm
        else:
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                raise ValueError("OpenAI API Key is missing. Please set the OPENAI_API_KEY environment variable.")

            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                openai_api_key=api_key,
                temperature=0
            )

    def process_query(self, query: str, contract_id: str = None) -> Dict[str, Any]:
        # Check if any contracts are indexed
        if self.rag_engine.is_empty:
            return {
                "answer": "No contracts have been indexed. Please upload a readable PDF contract first.",
                "source_documents": []
            }

        # Retrieve context
        filter_dict = None
        if contract_id:
            filter_dict = {"contract_id": contract_id}

        docs = self.rag_engine.search(query, filter=filter_dict)

        # Format context
        context_parts = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Unknown')
            content = doc.page_content
            context_parts.append(f"--- Segment {i+1} from {source} ---\n{content}\n")

        context = "\n".join(context_parts)

        if not context:
            msg = "I couldn't find any relevant information in the uploaded contracts to answer your question."
            if contract_id:
                msg = "I couldn't find any relevant information in the selected contract to answer your question."
            return {
                "answer": msg,
                "source_documents": []
            }

        # Generate answer
        system_prompt = """You are an AI assistant for IT Admin Teams specializing in contract analysis.
        Answer the user's question based strictly on the provided context.
        If the answer is not in the context, say "I cannot find this information in the contracts provided."

        When answering:
        1. Be precise with dates, names, and clauses.
        2. Cite the contract name if multiple are present in context.
        3. Quote the relevant clause if applicable.
        """

        user_message = f"""
        Context:
        {context}

        Question:
        {query}
        """

        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ])
            answer = response.content
        except Exception as e:
            answer = f"Error generating answer: {e}"

        return {
            "answer": answer,
            "source_documents": docs
        }
