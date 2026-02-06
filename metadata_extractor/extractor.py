from pydantic import BaseModel, Field
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import settings
import json
import logging

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
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                openai_api_key=settings.OPENAI_API_KEY or "sk-placeholder",
                temperature=0
            )

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
