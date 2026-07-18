tokens are the basic units 
our text gets cnverted to tokens before feeding into transformers.
the sweet spot where we have a fairly dnese tokenization so we have space to load enough context and also to predict the next is favoured

gpt-2 made more tokens and not good enough for python code
gpt4 handles this issue a little well

LLM Call:
from openai import OpenAI                      -Load the sdk
client = OpenAI(api_key="sk...")               -connecting to api
response = client.chat.completions.create(     -call the model
    model = "gpt-4o",
    temperature = 0.7, 
    messages=[
        {"role" : "user",
        "content" : "What is AI?"}
    ]
)
print(response.choices[0].message.content)     -print the reply


TOOL CALLING APP

import os
from openai import OpenAI
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY)
    base_url = os.getenv("OPENAI_API_BASE)
)
system_message = "You are a helpful personal assistant"
messages=[
    {"role" : "system", "content" : system_messsage},
    {"role": "user", "content" : "What's on my calender today?"}
]
response = client.chat.completions.create(
    model = "openai/gpt-4.1-mini",
    messages = messages, tools = tools,
)
if response.choices[0].finish_reason == "tool_calls":
    msg = response.coices[0].message
    messages.append(msg)
    for tc in msg.tool_calls:
        result = execute_tool(tc.function_name,
            json.loads(tc.function.arguments))
        messages.append({"role": "tool",
            "tools_call_id": tc.id, "content" : result})
    final = client.chat.completions.create(
        model ="openai/gpt-4.1-mini",
        messages=messages, tools=tools
    )
    print(final.choices[0].messagee.content)
tools=[
    {
        "type": "function",
        "function" : {
            "name" : "check_calender",
            "description": 'Check calender events.",
            "parameters":{
                "type": "object",
                "properties": {
                    "date": {"type" : "string"}
                },
                "required" : ["date"]
            }
        }
    }
]
def checck_calender(date):
    return "10am: Standup, 2pm: Dentist"
def execute_tool(name,args):
    if name == "check_calender" :
        return check_calender(**args)
    return f"Unknown tool: {name}"


AI Agent LOOP

import os
from openai import OpenAI
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY),
    base_url = os.getenv("OPENAI_API_BASE)
)
messages = [
    {"role" : "system", "content" : "You are a helpful assistant"}
]
messages.append({
    "role" : "user",
    "content" : "What are the three things an ai agent can do that a chatbot cannot?"
})
while True:
    response = client.chat.completions.create(
        model = "openai/gpt-4.1-mini",
        messages=messages
    )
    finish_reason = rsponse.choices[0].finish_reason
    if finish_reason == "stop":
        print(response.choices[0].message.content)
        break
    else:
        break


for multi turn

import os
from openai import OpenAI
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY),
    base_url = os.getenv("OPENAI_API_BASE)
)
messages = [
    {"role" : "system", "content" : "You are a helpful assistant"}
]
questions = [
    "What is an agent?",
    "How is it different from a chatbot?",
    "Give me one example.",
]
for question in questions:
    messages.append({"role" : "user", "content" : question})
    while True:
        response = client.chat.completions.create(
            model = "openai/gpt-4.1-mini",
            messages=messages
        )
        finish_reason = rsponse.choices[0].finish_reason
        if finish_reason == "stop":
            print(response.choices[0].message.content)
            print(f"Q: {question}")
            print(f"A: {reply\n}")
            messages.append({"role" : "assistant",
            "content" : reply})
            break
        else:
            break


5 Compenents of agent


import os
from openai import OpenAI
client = OpenAI(
    api_key = os.getenv["OPENAI_API_KEY"]
    base_url = os.getenv["OPENAI_API_BASE"]
)
model = "openai/gpt-4.1-mini"

messages = [
    {
        "role" : "system",
        "content" : "You are helpful personal assistant.Use your tools when you need real data."
    }
]
tools = [
    {
        "type" : "function",
        "function" : {
            "name" : "check_calender",
            "description": 'Check calender events.",
            "parameters":{
                "type": "object",
                "properties": {
                    "date": {"type" : "string"}
                },
                "required" : ["date"]
            }
        }
    }
]
def checck_calender(date):
    return "10am: Standup, 2pm: Dentist"
        