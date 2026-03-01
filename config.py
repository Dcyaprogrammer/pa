from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.environ.get("MOONSHOT_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
BASE_URL = "https://api.moonshot.cn/v1"
MODEL_ID = "kimi-k2-turbo-preview"
