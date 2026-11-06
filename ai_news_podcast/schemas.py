"""Pydantic schemas that keep the agent's structured report consistent."""
from typing import List

from pydantic import BaseModel, Field


class NewsStory(BaseModel):
    """A single news story with its context."""

    company: str = Field(description="Company name associated with the story (e.g., 'Nvidia', 'OpenAI'). Use 'N/A' if not applicable.")
    ticker: str = Field(description="Stock ticker for the company (e.g., 'NVDA'). Use 'N/A' if private or not found.")
    summary: str = Field(description="A brief, one-sentence summary of the news story.")
    why_it_matters: str = Field(description="A concise explanation of the story's significance or impact.")
    financial_context: str = Field(description="Current stock price and change, e.g., '$950.00 (+1.5%)'. Use 'No financial data' if not applicable.")
    source_domain: str = Field(description="The source domain of the news, e.g., 'techcrunch.com'.")
    process_log: str = Field(description="populate the `process_log` field in the schema with the `process_log` list from the `google_search` tool's output.")


class AINewsReport(BaseModel):
    """A structured report of the latest AI news."""

    title: str = Field(default="AI Research Report", description="The main title of the report.")
    report_summary: str = Field(description="A brief, high-level summary of the key findings in the report.")
    stories: List[NewsStory] = Field(description="A list of the individual news stories found.")
