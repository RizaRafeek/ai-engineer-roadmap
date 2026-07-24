from tavily import TavilyClient
from state import RouterState
from langchain_groq import ChatGroq
import os

llm = ChatGroq(model = "llama-3.3-70b-versatile")
tavily = TavilyClient(api_key= os.environ.get("TAVILY_API_KEY"))

def research_specialist_node(state: RouterState):
    search_response = tavily.search(state["user_message"])
    search_content = "\n\n".join([item["content"] for item in search_response["results"]])    
    prompt = f"""
    You are a research specialist. Use the search results below to answer the user's question accurately. If the search results don't contain enough information to answer confidently, say so explicitly rather than guessing. Search results:{search_content}
    Question: {state['user_message']}
    """
    llm_response = llm.invoke(prompt)
    return {"final_answer": llm_response.content}             #response2will have all the metadata which is not that required
