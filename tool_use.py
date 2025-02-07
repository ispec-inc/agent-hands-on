from util import llm_tool_use


def get_weather(location: str) -> str:
    """
    指定された場所の現在の天気を取得する
    """
    return f"天気を取得中... {location}"


def web_search(topic: str) -> str:
    """
    指定されたトピックに関する最新情報を取得する
    """
    return f"Webを検索... {topic}"


web_search_tool = {
    "name": "web_search",
    "description": "A tool to retrieve up to date information on a given topic by searching the web",
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "The topic to search the web for"},
        },
        "required": ["topic"],
    },
}

weather_tool = {
    "name": "get_weather",
    "description": "指定された場所の現在の天気を取得する",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "市と州、例: San Francisco, CA",
            }
        },
        "required": ["location"],
    },
}

if __name__ == "__main__":
    tools = [web_search_tool, weather_tool]

    prompt = input()
    result = llm_tool_use(
        prompt,
        tools=tools,
    )

    functions = {"get_weather": get_weather, "web_search": web_search}

    func = functions[result["name"]]
    print(func(result["input"]))
