from nodes.router import router_node

initial_state = {
    "user_message": "Calculate the average of this list of numbers: 4, 8, 15, 16, 23, 42"
}

routing_decision = router_node(initial_state)
print("router's decision:", routing_decision)