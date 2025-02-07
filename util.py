import os
from typing import TypeVar, Union
import re

from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def llm_tool_use(
    prompt: str,
    system_prompt: str = "",
    tools=[],
    model="claude-3-5-sonnet-20241022",
    tool_choice={"type": "auto"},
) -> Union[str, dict]:
    messages = [{"role": "user", "content": prompt}]
    response = client.messages.create(
        system=system_prompt, model=model, messages=messages, max_tokens=1000, tool_choice=tool_choice, tools=tools
    )

    last_content_block = response.content[-1]
    if last_content_block.type == "text":
        print("Claude did NOT call a tool")
        return last_content_block.text
    elif last_content_block.type == "tool_use":
        print("Claude wants to use a tool")
        return {"input": last_content_block.input, "name": last_content_block.name}


def llm_call(
    prompt: str,
    system_prompt: str = "",
    tools=[],
    model="claude-3-5-sonnet-20241022",
) -> str:
    """
    Calls the model with the given prompt and returns the response.

    Args:
        prompt (str): The user prompt to send to the model.
        system_prompt (str, optional): The system prompt to send to the model. Defaults to "".
        model (str, optional): The model to use for the call. Defaults to "claude-3-5-sonnet-20241022".

    Returns:
        str: The response from the language model.
    """
    messages = [{"role": "user", "content": prompt}]
    response = client.messages.create(
        model=model,
        tools=tools,
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
        temperature=0.1,
    )
    return response.content[0].text


def extract_xml(text: str, tag: str) -> str:
    """
    Extracts the content of the specified XML tag from the given text. Used for parsing structured responses

    Args:
        text (str): The text containing the XML.
        tag (str): The XML tag to extract content from.

    Returns:
        str: The content of the specified XML tag, or an empty string if the tag is not found.
    """
    match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return match.group(1) if match else ""
