from langchain_groq import ChatGroq
from state import RouterState

llm = ChatGroq(model = "llama-3.3-70b-versatile")
def code_specialist_node(state: RouterState):
    prompt = f"You are a coding specialist. Help with the following request by writing clear, correct code and explaining your reasoning briefly. If the request involves debugging, identify the likely cause of the issue before suggesting a fix. Request: {state['user_message']}"
    response = llm.invoke(prompt)
    return{"final_answer": response.content}