"""Report persistence tool."""
from pathlib import Path
from typing import Dict

from .. import config


def save_news_to_markdown(filename: str, content: str) -> Dict[str, str]:
    """
    Saves the given content to a Markdown file in the output directory.

    Args:
        filename: The name of the file to save (e.g., 'ai_research_report.md').
        content: The Markdown-formatted string to write to the file.

    Returns:
        A dictionary with the status of the operation.
    """
    try:
        # The filename comes from the LLM, so strip any directory components.
        safe_name = Path(filename).name
        if not safe_name.endswith(".md"):
            safe_name += ".md"

        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        file_path = config.OUTPUT_DIR / safe_name
        file_path.write_text(content, encoding="utf-8")
        return {
            "status": "success",
            "message": f"Successfully saved news to {file_path.resolve()}",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to save file: {str(e)}"}
