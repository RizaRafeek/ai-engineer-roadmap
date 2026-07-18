from datetime import datetime
import os
from groq import Groq
import json

client = Groq(
    api_key = os.getenv("GROQ_API_KEY")
)
tools=[
    {
        "type" : "function",
        "function" : {
            "name" : "log_session",
            "description" : "Logs a study session, but only when the user describes actively studying a computer science or mathematics topic (e.g. DSA, algorithms, graph theory).Do NOT call this for physical activities like cycling, or statements that don't describe any study activity, like mentioning where someone lives.",
            "parameters" : {
                "type" : "object",
                "properties": {
                    "topic" : {"type" : "string"},
                    "duration_minutes" : {"type" : "integer"},
                },
                "required" : ["topic", "duration_minutes"]
            }
        }
    } 
]

def log_session(topic, duration_minutes):
    date = datetime.now().isoformat()             #datetime return as it is not jsoon serializable so we convert into string
    if os.path.exists("../sessions.json"):
        with open("../sessions.json", "r")as f:      #r enables us to open the existing file and read it . with - safety-automatically closes file
            sessions = json.load(f)              #reads the file's json text and turns it into a real python list stored in sessions
    else:
        sessions = []
    sessions.append({"topic" : topic, "duration_minutes" :duration_minutes, "date": date})
    with open('../sessions.json', 'w') as f:
        json.dump(sessions,f)
    #first we opened it in read mode and then converted those json ones to python dict and added to the list, if not actually existing we created a blank list where we appended the topic to the list in memory and later used "w" to permanently add to the session list

test_prompts = [
    "I logged 2 hours of DP today",
    "spent 30 minutes on graph",
    "what's 2+2",
    "We live in mumbai",
    "Is the stadium large?",
    "Solidified my understanding of algorithms for 1 hour",
    "solved dsa problems for 2 hours",
    "studied graph theory for 30 minutes",
    "revised dynamic programming for 1 hour",
    "cycled for 20 minutes in the park",
    "ran through the dsa problems for 30 minutes"]

for prompt in test_prompts:
    messages = [{"role" : "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model = "llama-3.3-70b-versatile",
            messages = messages,
            tools = tools)
    except Exception as e:
        print(f"API call failed for prompt '{prompt}' : {e}")
        continue                                           #skip to the next prompt,domt crash

    if response.choices[0].message.tool_calls:     #if the moddel has called any tool then continue else move to the else block
        tool_call = response.choices[0].message.tool_calls[0]               #it gives you an idea which tool the model pointed
        if tool_call.function.name == "log_session":
            args = json.loads(tool_call.function.arguments)                 #it converts the json file into dict which has the required files extratcted from user's prompt by the model
            log_session(args["topic"], args["duration_minutes"])             #calling the function  with the required parameters
            print(f"Logged : {args['topic']} for {args['duration_minutes']} minutes")
        else:
            print(f"Model tried to call unknown tool: {tool_call}")
    else:
        print(response.choices[0].message.content)                  #the model gives the content or gives the tool call .so if the tool call is empty then it clearly returned content

