from nodes.router import router_node
from nodes.code_specialist import code_specialist_node
from nodes.research_specialist import research_specialist_node
from nodes.data_analysis_specialist import data_analysis_specialist_node

initial_state = {
    "user_message": "Write a Python function that checks if a string is a palindrome"
}
research_q = {
    "user_message": "What is the current inflation rate in dubai?"
}
data_analysis_q = {
    "user_message": "Calculate the average of these numbers: 4, 8, 15, 16, 23, 42"
}

#routing_decision = router_node(initial_state)
#print("router's decision:", routing_decision)

#code_answer = code_specialist_node(initial_state)
#print("code final answer:", code_answer)

research_answer = research_specialist_node(research_q)
print("research final answer:", research_answer)

data_analysis_answer = data_analysis_specialist_node(data_analysis_q)
print("data analysis final answer:" ,data_analysis_answer)