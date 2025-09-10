from langchain_core.tools import tool


@tool
def get_current_weather(location: str) -> str:
    """Get the current weather in a given location"""
    # For demonstration purposes, we'll return a static response.
    # In a real implementation, you would call a weather API here.
    print("Tool used: get_current_weather")
    return f"The current weather in {location} is sunny with a temperature of 25°C."


@tool
def get_news(topic: str) -> str:
    """Get the latest news on a given topic"""
    # For demonstration purposes, we'll return a static response.
    # In a real implementation, you would call a news API here.
    print("Tool used: get_news")
    return f"The latest news on {topic} is that AI is transforming the tech industry."