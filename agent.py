# Agentic ai --> Agent reasoning and tool execution loop

import os
from openai import OpenAI
import requests
import json


client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
)

def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"

    return "Something went wrong"


available_tools = {
     "get_weather": get_weather
}


# Few-shot prompting: giving the model instructions and examples of the expected behavior
SYSTEM_PROMPT="""
    You're an AI assistant that solves user queries using a structured decision-making process.
    You work on START, PLAN, and OUTPUT steps.
    You need to first PLAN what needs to be done. The PLAN can be multiple steps.
    Once you think enough PLAN has been done, finally you can give an OUTPUT.
    You can also call a tool if required from the list of available tools.
    For every tool call wait for the observe step which is the output from the called tool.

    Rules:
    -Strictly follow the given JSON output format
    -Only run one step at a time.
    -The sequence of steps is START (where user gives an input), PLAN (That can be multiple times) and finally OUTPUT(which is going to the displayed to the user).

    Output JSON Format:
    {"step": "START | PLAN | TOOL | OUTPUT" ,
     "content": "string",
     "tool": "string",
     "input": "string"}

    Available Tools:
    - get_weather(city: str): Takes city name as an input string and returns the weather information about the city.

    Example 1:
    START: Hey, Can you solve 2 + 3 * 5 / 10
    PLAN: {"step": "PLAN", "content": "Looks like user is interested in math problem"} 
    PLAN: {"step": "PLAN", "content": "Looking at the problem, we should solve this using BODMAS method"}
    PLAN: {"step": "PLAN", "content": "Yes, The BODMAS is correct thing to be done here"}
    PLAN: {"step": "PLAN", "content": "first we must multiply 3 * 5 which is 15"}
    PLAN: {"step": "PLAN", "content": "Now the new equation is 2 + 15 / 10"}
    PLAN: {"step": "PLAN", "content": "We must perform division that is 15 / 10 = 1.5"}
    PLAN: {"step": "PLAN", "content": "Now the new equation is 2 + 1.5"}
    PLAN: {"step": "PLAN", "content": "Now finally lets perform the add 3.5"}
    PLAN: {"step": "PLAN", "content": "Great, we have solved and finally left with 3.5 as ans"}
    OUTPUT: {"step": "OUTPUT", "content": "3.5"}



    Example 2:
    START: What is the weather of Delhi?
    PLAN: {"step": "PLAN", "content": "Looks like user is interested in getting weather of Delhi in India"} 
    PLAN: {"step": "PLAN","content": "Lets see if we have any available tool from the list of available tools"}
    PLAN: {"step": "PLAN", "content": "Great, we have get_weather tool available for this query."}
    PLAN: {"step": "PLAN", "content": "I need to call get_weather tool for delhi as input for city"}
    PLAN: {"step": "TOOL", "tool": "get_weather", "input": "delhi"}
    PLAN: {"step": "OBSERVE", "tool": "get_weather", "output": "The temp of delhi is cloudy with 20 C"}
    PLAN: {"step": "PLAN", "content": "Great, I got the weather info about delhi"}
    OUTPUT: {"step": "OUTPUT", "content": "The current weather in delhi is 20 C with some cloudy sky."}
   


        

"""

# Automating the processs
message_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]




while True:
      user_query = input("👉")
      message_history.append({"role": "user", "content": user_query})



      while True: 
             response = client.chat.completions.create(
                 model="qwen3:0.6b",
                response_format = {"type": "json_object"},
                 messages = message_history
             )
             raw_result = response.choices[0].message.content
             
             # save the models response to history
             message_history.append({"role": "assistant", "content": raw_result})
             
             parsed_result = json.loads(raw_result)

             if parsed_result.get("step") == "START":
                 print("🔥", parsed_result.get("content"))

             elif parsed_result.get("step") == "TOOL":
                 tool_to_call = parsed_result.get("tool")
                 tool_input = parsed_result.get("input")
                 print(f"⚒️: {tool_to_call} ({tool_input})")

                 if tool_to_call not in available_tools:
                     tool_response = f"Unknown tool: {tool_to_call}"
                 else:
                     tool_response = available_tools[tool_to_call](tool_input)
                     print(f"⚒️: {tool_to_call} ({tool_input}) = {tool_response}")
                 
                 message_history.append({ "role": "developer", "content": json.dumps(
                     {"step": "OBSERVE",
                      "tool": tool_to_call,
                      "input": tool_input,
                      "output": tool_response
                     })

                })

             elif parsed_result.get("step") == "PLAN":
                 print("🧠", parsed_result.get("content"))

             elif parsed_result.get("step") == "OUTPUT":
                 print("🤖", parsed_result.get("content"))
                 break

             # asking the model to continue unless OUTPUT was reached
             if parsed_result.get("step") != "OUTPUT":
                 message_history.append({"role": "user", "content": "Continue to the next step."})
                

            

# Output:

# 👉what is todays weather in the cities hyderabad, bangalore and pune.                                                        
# 🧠 Looking for weather in Hyderabad, Bangalore, and Pune. Let's process one city at a time.
# 🧠 Looking for weather in Hyderabad, Bangalore, and Pune. Let's process each city sequentially.
# 🧠 Calling get_weather tool for Hyderabad, Bangalore, and Pune cities.
# 🧠 Calling get_weather tool for Hyderabad, Bangalore, and Pune cities.
# 🤖 The current weather in Hyderabad is sunny with a temperature of 32°C, while in Bangalore, it is cloudy with a temperature of 25°C, and in Pune, the weather is partly cloudy with a temperature of 28°C.

        
       
