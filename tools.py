import requests
from tavily import TavilyClient
from config import TAVILY_API_KEY


def get_weather(city: str) -> str:

    url = f"https://wttr.in/{city}?format=j1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        current_condition = data["current_condition"][0]
        weather_desc = current_condition["weatherDesc"][0]["value"]
        temp_c = current_condition["temp_C"]

        return f"{city} current weather is {weather_desc} with temperature {temp_c} degrees Celsius"

    except requests.RequestException as e:
        return f"Error fetching weather data: {e}"
    except (KeyError, IndexError) as e:
        return f"Error parsing weather data: {e}"


def get_attraction(city: str, weather:str) -> str:

    api_key = TAVILY_API_KEY
    if not api_key:
        return "Error: TAVILY_API_KEY not found in environment variables"
    
    tavily = TavilyClient(api_key=api_key)
    query = f" The best recommended attraction to go to and why in {city} with {weather}"
    
    try:
        response = tavily.search(query=query, search_depth="basic", include_answer=True)

        if response.get("answer"):
            return response["answer"]

        formatted_results = []
        for result in response.get("results", []):
            formatted_results.append(f"- {result['title']}: {result['content']}")

        if not formatted_results:
            return "No attractions found."

        return "\n".join(formatted_results)

    except Exception as e:
        return f"Error fetching attraction data: {e}"
