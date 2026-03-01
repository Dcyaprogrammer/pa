from dotenv import load_dotenv
import re
import os
from llm import OpenAICompatibleClient
from tools import get_weather, get_attraction
from system_prompt import AGENT_SYSTEM_PROMPT

load_dotenv()
API_KEY = os.environ.get("MOONSHOT_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
BASE_URL = "https://api.moonshot.cn/v1"
MODEL_ID = "kimi-k2-turbo-preview"

llm = OpenAICompatibleClient(model=MODEL_ID, api_key=API_KEY, base_url=BASE_URL)
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction
}

user_prompt = "Hello, please help me check the weather in Beijing today, then recommend a good attraction to go to."
prompt_history = [f"User: {user_prompt}"]

print(f"User input: {user_prompt}\n" + "="*40)

for i in range(5):
    print(f"---loop: {i+1}---\n")

    full_prompt = "\n".join(prompt_history)
    llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)
    match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', 
                        llm_output, re.DOTALL)
    if match:
        truncated = match.group(1).strip()
        if truncated != llm_output.strip():
            llm_output = truncated
            print("Have truncated additional Thought-Action pairs")
    print(f"LLM output: {llm_output}\n")
    prompt_history.append(llm_output)

    action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
    if not action_match:
        observation = "Error: cannot find Action"
        observation_str = f"Observation: {observation}"
        print(f"{observation_str}\n")
        prompt_history.append(observation_str)
        continue
    action_str = action_match.group(1).strip()

    if action_str.startswith("Finish"):
        final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
        print(f"Final answer: {final_answer}\n")
        break

    tool_name = re.search(r"(\w+)\(", action_str).group(1)
    args_str = re.search(r"\((.*)\)", action_str).group(1)
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

    if tool_name in available_tools:
        observation = available_tools[tool_name](**kwargs)
    else:
        observation = f"Error: tool {tool_name} not found"
    
    observation_str = f"Observation: {observation}"
    print(f"{observation_str}\n")
    prompt_history.append(observation_str)
