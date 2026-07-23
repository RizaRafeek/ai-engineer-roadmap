from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from state import SpecialistType, RouterState

llm = ChatGroq(model="llama-3.3-70b-versatile")

class Router(BaseModel):                 #just defining the shape of router(schema)
    specialist : SpecialistType
    reasoning : str

def router_node(state : RouterState):
    prompt = f"You are a router that classifies user requests into exactly one specialist category.Categories:- code: requests to write, explain, debug, or review code/programming logic.research: requests needing current, factual, or real-world information (news, prices, people, events). data_analysis: requests involving calculations, statistics, or analyzing structured/tabular dataClassify the following request into exactly one category, and briefly explain why. Request: {state['user_message']}"
    result = llm.with_structured_output(Router).invoke(prompt)
    return{"specialist": result.specialist, "reasoning": result.reasoning}

def next_node(state: RouterState):
    #f state["specialist"] == "code":
    #   return "code"
    #lif state["specialist"] == "research":
    #   return "research"
    #lif state["specialist"] == "ata_analysis":
    #   return "data_analysis"
    return state["specialist"].value