import requests
from langchain_core.messages import SystemMessage, HumanMessage
from rag_engine.vector_store import RAGEngine
from config.settings import settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ChatEngine:
    def __init__(self, rag_engine: RAGEngine, llm=None):
        self.rag_engine = rag_engine
        if llm:
            self.llm = llm
        else:
            api_key = settings.PERPLEXITY_API_KEY
            if not api_key:
                raise ValueError("Perplexity API Key is missing. Please set the PERPLEXITY_API_KEY environment variable.")
            self.llm = PerplexityLLM(api_key=api_key, model=settings.PERPLEXITY_MODEL)

    def process_query(self, query: str, contract_id: str = None) -> Dict[str, Any]:
        # Retrieve context if contracts are indexed
        docs = []
        if not self.rag_engine.is_empty:
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

        # Determine System Prompt and User Message based on context availability
        if not context:
            system_prompt = """You are an AI assistant for IT Admin Teams specializing in contract analysis.
            Currently, no relevant information was found in the contracts (or no contracts are indexed).

            Your instructions:
            1. If the user is greeting you (e.g., "Hi", "Hello"), respond politely and introduce yourself as a contract analysis assistant.
            2. If the user is asking a general question not related to a specific contract, you may answer based on general knowledge.
            3. If the user is asking a specific question about a contract, politely explain that you cannot find the information in the available documents and suggest they upload the relevant contract.
            """
            user_message = f"Question:\n{query}"
        else:
            system_prompt = """You are an AI assistant for IT Admin Teams specializing in contract analysis.
            Answer the user's question based strictly on the provided context.
            If the answer is not in the context, say "I cannot find this information in the contracts provided."

            When answering:
            1. Be precise with dates, names, and clauses.
            2. Cite the contract name if multiple are present in context.
            3. Quote the relevant clause if applicable.
            """
            user_message = f"Context:\n{context}\n\nQuestion:\n{query}"

        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ])
            answer = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            answer = f"Error generating answer: {e}"
            logger.error(f"LLM Error: {e}")

        return {
            "answer": answer,
            "source_documents": docs
        }


class PerplexityLLM:
    """Wrapper for Perplexity API"""
    
    def __init__(self, api_key: str, model: str = "llama-2-70b-chat"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.perplexity.ai"
    
    def invoke(self, messages):
        """Invoke Perplexity API with messages"""
        # Convert LangChain message format to Perplexity format
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                formatted_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                formatted_messages.append({"role": "user", "content": msg.content})
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": formatted_messages,
                    "temperature": 0
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # Create a response object with .content attribute
            class PerplexityResponse:
                def __init__(self, content):
                    self.content = content
            
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return PerplexityResponse(answer)
        except requests.exceptions.RequestException as e:
            logger.error(f"Perplexity API Error: {e}")
            raise