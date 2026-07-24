from nodes.router import router_node
from nodes.code_specialist import code_specialist_node

initial_state = {
    "user_message": "Write a Python function that checks if a string is a palindrome"
}

#routing_decision = router_node(initial_state)
#print("router's decision:", routing_decision)

code_answer = code_specialist_node(initial_state)
print("code final answer:", code_answer)