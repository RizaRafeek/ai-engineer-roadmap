from langchain_core.tools import tool
from langchain_groq import ChatGroq
from state import RouterState

llm = ChatGroq(model = "llama-3.3-70b-versatile")

@tool
def calculate(expression):
    """Evaluates a mathematical expression and returns the numeric result. Use this for any arithmetic, statistics, or calculation involving numbers (e.g. averages, sums, percentages, growth rates). Do NOT use this for non-numeric requests or requests that don't involve a calculable expression."""
    try:
        answer = eval(expression, {"__builtins__": {}})
        return answer
    except Exception as e:
        return "Error: invalid expression" 

llm_with_tools =  llm.bind_tools([calculate])

def data_analysis_specialist_node(state: RouterState):
    prompt = f"""
    You are a data-analysis specialist. Use the calculate tool for any arithmetic, statistics, or numerical computation needed to answer the request. Do not attempt to compute results yourself — always use the tool for calculations.
    Request: {state['user_message']}
    """
    response = llm_with_tools.invoke(prompt)
    print(response.tool_calls)
    if response.tool_calls:
        result = calculate.invoke(response.tool_calls[0]["args"])             #in @tool the parameter value(expression) gets stored in args
        final_prompt = f"""
        The calculation result is {result}. Write a clear answer to the original question: {state['user_message']}
        """
        final_response = llm.invoke(final_prompt)
        return{"final_answer" : final_response.content}
    else:
        return {"final_answer": "No Calculation was performed-Invalid expression"}      #all the reponse is expected to be dic(final_answer is specified as dict)

    