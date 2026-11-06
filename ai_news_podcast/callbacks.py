"""Guardrail callbacks that run before / after tool calls.

before_tool_callback  -> can modify the tool args or block the call (by returning a dict)
after_tool_callback   -> can enrich the tool response (e.g. add an audit trail)
"""
import re
from urllib.parse import urlparse

from . import config


def block_unwanted_domains_callback(tool, args, tool_context):
    """Blocks searches that explicitly target low-quality / non-news domains."""
    if tool.name == "google_search":
        query = args.get("query", "").lower()
        for domain in config.BLOCKED_DOMAINS:
            if f"site:{domain}" in query or domain in query:
                print(f"BLOCKED: query targets blocked domain '{domain}': '{query}'")
                return {
                    "error": "blocked_source",
                    "reason": f"Searches targeting {domain} are not allowed. Please search for professional news sources.",
                }
    return None


def filter_news_sources_callback(tool, args, tool_context):
    """Restricts google_search queries to a whitelist of trusted news domains."""
    if tool.name == "google_search":
        original_query = args.get("query", "")
        if any(f"site:{d}" in original_query.lower() for d in config.WHITELIST_DOMAINS):
            return None
        whitelist_part = " OR ".join(f"site:{d}" for d in config.WHITELIST_DOMAINS)
        args["query"] = f"{original_query} {whitelist_part}"
        print(f"MODIFIED query to enforce whitelist: '{args['query']}'")
    return None


def enforce_data_freshness_callback(tool, args, tool_context):
    """Appends a recency hint (last week) to google_search queries."""
    if tool.name == "google_search":
        query = args.get("query", "")
        if "tbs=qdr:w" not in query:
            args["query"] = f"{query} tbs=qdr:w"
            print(f"MODIFIED query for freshness: '{args['query']}'")
    return None


def initialize_process_log(tool_context):
    """Ensure the process_log list exists in session state."""
    if "process_log" not in tool_context.state:
        tool_context.state["process_log"] = []


def inject_process_log_after_search(tool, args, tool_context, tool_response):
    """After a search, record which domains were sourced and expose the log to the LLM."""
    if tool.name == "google_search" and isinstance(tool_response, str):
        initialize_process_log(tool_context)

        urls = re.findall(r"https?://[^\s/]+", tool_response)
        unique_domains = sorted({urlparse(u).netloc for u in urls})

        if unique_domains:
            sourcing_log = f"Action: Sourced news from the following domains: {', '.join(unique_domains)}."
            tool_context.state["process_log"] = [sourcing_log] + tool_context.state["process_log"]

        final_log = tool_context.state["process_log"]
        print(f"CALLBACK LOG: Injecting process log into tool response: {final_log}")
        return {"search_results": tool_response, "process_log": final_log}
    return tool_response
