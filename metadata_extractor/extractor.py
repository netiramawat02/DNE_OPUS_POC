from pydantic import BaseModel, Field
from typing import Optional
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import settings
import json
import logging
import requests

logger = logging.getLogger(__name__)

class ContractMetadata(BaseModel):
    title: Optional[str] = Field(None, description="Title of the contract")
    vendor: Optional[str] = Field(None, description="Name of the vendor or provider")
    client: Optional[str] = Field(None, description="Name of the client or customer")
    start_date: Optional[str] = Field(None, description="Start date of the contract")
    end_date: Optional[str] = Field(None, description="End date or expiry date")
    renewal_terms: Optional[str] = Field(None, description="Brief summary of renewal terms")
    contract_id: Optional[str] = Field(None, description="Contract ID number if present")

class MetadataExtractor:
    def __init__(self, llm=None):
        if llm:
            self.llm = llm
        else:
            api_key = settings.PERPLEXITY_API_KEY
            if not api_key:
                raise ValueError("Perplexity API Key is missing. Please set the PERPLEXITY_API_KEY environment variable.")

            self.llm = PerplexityLLM(api_key=api_key, model=settings.PERPLEXITY_MODEL)

    def extract(self, text: str) -> ContractMetadata:
        prompt = """
        You are an expert legal contract analyzer.
        Extract the following metadata from the contract text provided below.
        Return ONLY a valid JSON object with the following keys:
        title, vendor, client, start_date, end_date, renewal_terms, contract_id.

        Format dates as YYYY-MM-DD if possible.
        If a field is not found, set it to null.

        Contract Text:
        """

        # Truncate text to avoid token limits (rudimentary approach)
        text_context = text[:10000]

        messages = [
            SystemMessage(content="You extract metadata from contracts in JSON format."),
            HumanMessage(content=prompt + "\n\n" + text_context)
        ]

        try:
            response = self.llm.invoke(messages)
            content = response.content.strip()

            # Clean up Markdown formatting if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            data = json.loads(content.strip())
            return ContractMetadata(**data)
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return ContractMetadata()


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