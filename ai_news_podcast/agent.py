"""Agent definitions: a root producer agent plus a podcaster sub-agent exposed as a tool."""
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

from . import config
from .callbacks import (
    block_unwanted_domains_callback,
    enforce_data_freshness_callback,
    filter_news_sources_callback,
    inject_process_log_after_search,
)
from .prompts import PODCASTER_INSTRUCTION, ROOT_INSTRUCTION
from .schemas import AINewsReport
from .tools import generate_podcast_audio, get_financial_context, save_news_to_markdown

# Specialist agent: turns a script into multi-speaker audio.
podcaster_agent = Agent(
    name="podcaster_agent",
    model=config.PODCASTER_MODEL,
    instruction=PODCASTER_INSTRUCTION,
    tools=[generate_podcast_audio],
)

# Root agent: researches news, enriches with stock data, writes the report + script,
# then delegates audio generation to the podcaster agent.
root_agent = Agent(
    name="ai_news_researcher",
    model=config.ROOT_MODEL,
    instruction=ROOT_INSTRUCTION,
    tools=[
        google_search,
        get_financial_context,
        save_news_to_markdown,
        AgentTool(agent=podcaster_agent),
    ],
    output_schema=AINewsReport,
    before_tool_callback=[
        block_unwanted_domains_callback,
        filter_news_sources_callback,
        enforce_data_freshness_callback,
    ],
    after_tool_callback=[inject_process_log_after_search],
)
