from langgraph.graph import StateGraph, END, MessagesState       #messagestate- message history, end - no tool then return text , stategraph -container for the graph
from langchain_groq import ChatGroq                       #chatgroq - speaks langchains language thangroqs sdk 
from langchain_core.tools import tool                     #lets you turn plain python function into langraph/langchain tools
from langgraph.prebuilt import ToolNode
from datetime import datetime
import os
import json

llm = ChatGroq(model ="llama-3.3-70b-versatile")          #the chatgroq looks up your environment variable which will match the groq_api_key if it exists and fetches them themselves 
              
@tool                                                     #it aavoids the need for building the tools dictionary
def log_session(topic: str, duration_minutes: int):
    """Logs a study session, but only when the user describes actively studying a computer science or mathematics topic (e.g. DSA, algorithms, graph theory).Do NOT call this for physical activities like cycling, or statements that don't describe any study activity, like mentioning where someone lives."""
    date = datetime.now().isoformat() 
    if os.path.exists("sessions.json"):          
        with open("sessions.json", "r")as f:  
            sessions = json.load(f)   
    else:
        sessions = []
    sessions.append({"topic" : topic, "duration_minutes" :duration_minutes, "date": date})
    with open('sessions.json', 'w') as f:
        json.dump(sessions,f)

#print(log_session.name)
#print(log_session.description)
#print(log_session.args)

llm_with_tools = llm.bind_tools([log_session])            #telling the llm the tools available for it

def agent_node(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"])     #like chat.completions.. where the conversation is sent to the model and gets back a reposne
    return {"messages": [response]}                         #here is the new message to add to add called the response  - messages : auto-appending field in Messagestate

tool_node = ToolNode([log_session])


#test_response = llm_with_tools.invoke([{"role" : "user", "content" : " I studied array for 45 minutes"}])
#print(test_response)
#print(test_response.tool_calls)

def should_continue(state: MessagesState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:    #if it contain any tool calls                   
                                          #After the tool execution wwhich is the logging the control goes back to the agent(thinking) so it can check whether there is something else i need to do instead of going straight to exit after the tool execution which will eliminate the secomd question
        return "tools"              #it tells the langgraph to routr to the one named "tools" if that string is returned
    else:
        return END
    
graph = StateGraph(MessagesState)      #creates an empty graph-builder - messagestate tells that this graph is growing list of messages

graph.add_node("agent", agent_node)    #createing nodes ("the name you call this node even from elsewhere in the program", the actual function runs when this node is reached)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")         #whenever the graph is called with fresh convo start with agent node

graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END : END})  #if should_continue returned tools go to the tools node else go to end

graph.add_edge("tools", "agent")        #after tools done running go back to agent again

app = graph.compile()                   #compiles the graph with everything we have stated above

result = app.invoke({"messages" : [{"role": "user", "content": "I studied arrays for 30 minutes"}]})   #start with this ,this runs until the node reaches end, result-what the graph produces when it reach end
print(result["messages"][-1].content)   
print(len(result["messages"]))              