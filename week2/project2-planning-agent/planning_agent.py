from typing import TypedDict, Annotated                  #dictionary with fixed known shape(exactly these field,with these types),  annoted - add extra piece of information alongside the type
from langgraph.graph.message import add_messages       #to append the messages
from operator import add
from pydantic import BaseModel, Field                    #used to describe the exact structure I want the LLM output to take
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import json
from datetime import datetime

llm = ChatGroq(model="llama-3.3-70b-versatile")

def log_transition(node_name, state_before, state_after):            #utility you'll call around your actual nodes. It takes three things: the name of the node that just ran, the state before it ran, and the state after.
    entry = {
        "timestamp": datetime.now().isoformat(),                     #to convert into string to make it json serializable
        "node": node_name,
        "state_after": {k: v for k, v in state_after.items() if k != "chat_history"}   #avoided chat_history because its growing with the same info
    }
    with open("trace_log.jsonl", "a") as f:
        f.write(json.dumps(entry, default= str) + "\n")


class PlanningState(TypedDict):                          # atype like messagestate which has the custom shape - using typedict
    chat_history: Annotated[list, add_messages]             #messag is a list - when new value in messags - use add_message(Annotated doing this work) - without these the messages might overwrite instead of append
    sub_questions: list[str]
    gathered_info: Annotated[list[str], add]            #add is for others, add_message for only message field
    enough_info: bool
    final_answer: str
    loop_count: Annotated[int, add]
#print(PlanningState)

class SubQuestions(BaseModel):                          #a new pydantic modell called subquestions - BaseModel:gives the class all its validation power
    questions: list[str] = Field(description="A list of focused sub-questions that together fully answer the user's original question")      #field - like annotation:type + extra idea

#the model will be told:"your response must be a JSON object with exactly one field called questions, containing a list of strings, where each string is a focused sub-question."
#force structure at the source - instead of dealing with its dirtiness later

question_llm = llm.with_structured_output(SubQuestions)    #the output has to be of like SubQuestions defined - no other option

def planner_node(state: PlanningState):
    result = question_llm.invoke(state["chat_history"])        #.invoke - sends the convo to the model  -state["messages"] : pulls out conversation hstory so far
    return {"sub_questions": result.questions}          #question is the attribute of class SubQuestions so accessed via.

#test_state = {"chat_history": [{"role": "user", "content": "Compare LangGraph vs CrewAI for production use"}], "sub_questions": [], "gathered_info": []}
#result = planner_node(test_state)
#print(result)

class Answers(BaseModel):
    answers: list[str] = Field(description = "A list of answers, one for each sub-question provided, in the exact same order as the sub-questions were given. The list must contain exactly as many answers as there were sub-questions."
    )

answer_llm = llm.with_structured_output(Answers)

def tool_execution_node(state: PlanningState):
    questions_text = "\n".join(state["sub_questions"])
    try:
        result = answer_llm.invoke(f"Answer each of these sub-questions:\n{questions_text}")
        return {"gathered_info": result.answers,  "loop_count": 1}
    except Exception as e:
        print(f"Tool-execution failed: {e}")
        answers = [f"[Failed to generate an answer: {e}]"] * len(state["sub_questions"])
        return {"gathered_info": answers, "loop_count": 1}

#test_state = {
#    "chat_history": [{"role": "user", "content": "What are the key features of CrewAI"}],
#    "sub_questions": [
#        "What are the key features of CrewAI?"
#    ],
#    "gathered_info": []
#}
#result = tool_execution_node(test_state)
#print(result)

class Reflection(BaseModel):
    enough_info: bool = Field(description="A raw JSON boolean — true or false, never the string 'true' or 'false'. True only if every sub-question has a substantive, non-placeholder answer that directly addresses it, and nothing important from the original question is left uncovered. False if any answer is missing, generic, a failure placeholder like '[Failed to generate an answer]', or clearly doesn't address its sub-question.")

reflection_llm = llm.with_structured_output(Reflection)

def reflection_node(state: PlanningState):
    qa_pairs = "\n".join(f"Q: {q}\nA: {a}" for q, a in zip(state["sub_questions"], state["gathered_info"]))  #zip-mapping question 1- answer 1, q-question(first list, a-answer(secomdlist))
    prompt = f"Here is the research so far:\n{qa_pairs}\n\nIs this enough information to fully answer the question?"  #saved in prompt for reuse in every attempt
    for attempt in range(2):
        try:
            result = reflection_llm.invoke(prompt)
            return { "enough_info": result.enough_info}
        except Exception as e:
            print(f"Reflection attempt {attempt + 1} failed: {e}")
    print("Reflection failed twice - defaulting to False (assume more gathering needed)")    #to let us know it has tried twicw but still there is no enough info
    return {"enough_info": False}

#test_state ={"sub_questions": ["What is data", "Why is it used?"], "gathered_info" :["Data is a collection of raw, unorganized facts, numbers, observations, or symbols","Data is used to transform raw facts into actionable insights."]}
#result = reflection_node(test_state)
#print(result)
#test_state_incomplete = {
#    "sub_questions": ["What is data?", "Why is it used?"],
#    "gathered_info": ["data is collection of information", "[Failed to generate an answer: some error]"]
#}
#result2 = reflection_node(test_state_incomplete)
#print(result2)

def synthesis_node(state: PlanningState):
    original_question = state["chat_history"][0].content             #very first message of chat history
    qa_pairs = "\n".join(f"Q: {q}\nA: {a}" for q, a in zip(state["sub_questions"], state["gathered_info"])) 
    prompt = f"""You are answering this question: {original_question}
    Here is the research gathered to answer it:{qa_pairs}.Write a clear, complete, well-organized answer to the original question, synthesizing the research above into a coherent response. Do not just list the Q&A pairs — weave them into a natural, flowing answer. If any part of the research is marked as failed or incomplete, acknowledge that gap honestly rather than glossing over it."""
    result = llm.invoke(prompt)
    return {"final_answer": result.content}

#test_state = {
#    "chat_history": [HumanMessage(content="What is LangGraph and CrewAI, and how do they compare?")],
#    "sub_questions": ["What is LangGraph?", "What is CrewAI?"],
#    "gathered_info": [
#        "LangGraph is a library for building stateful, multi-step agent workflows as graphs.",
#        "CrewAI is a framework for orchestrating multiple AI agents working together on tasks."
#    ]
#}
#result = synthesis_node(test_state)
#print(result)

def should_continue_gathering(state: PlanningState):
    if state["enough_info"] or state["loop_count"] >= 3:
        return "synthesis"
    else:
        return "tool_execution"
    
graph = StateGraph(PlanningState)

graph.add_node("planner", planner_node)
graph.add_node("tool_execution", tool_execution_node)
graph.add_node("reflection", reflection_node)
graph.add_node("synthesis", synthesis_node)

graph.set_entry_point("planner")

graph.add_edge("planner", "tool_execution")
graph.add_edge("tool_execution", "reflection")
graph.add_conditional_edges("reflection", should_continue_gathering, {"tool_execution" : "tool_execution", "synthesis" : "synthesis"})
graph.add_edge("synthesis", END)

#app = graph.compile()                                   -replacing this with checkpoint and memorysaaver

#result = app.invoke({
#    "chat_history": [HumanMessage(content="Compare LangGraph vs CrewAI for production use")],
#    "sub_questions": [],
#    "gathered_info": [],
#    "enough_info": False,                                 #replacing this with the test call below
#    "final_answer": ""
#})
#print(result["final_answer"])

checkpointer = MemorySaver()                               #creating an instance of langgarph in built memory checkpointsaver(record full graph state after evry step,keyed by conversation(thread_id))
app = graph.compile(checkpointer = checkpointer)           #passing the checkpointer in-use this object to save/restore state across separate .invoke() calls," rather than treating each call as fully independent.

config = {"configurable": {"thread_id": "conversation_1"}}  #the thread_id is just a string label you choose(here cov_1 bcz here we have single user, later we can have conv_2 ,3 etc), identifying which ongoing conversation this call belongs to. Any future .invoke() call using this same thread_id will resume from where this conversation left off.



def run_and_log(input_state, config, call_label):
    final_output = {}                                       #running output dict
    for step in app.stream(input_state, config):              #each node in compiled graph
        for node_name, node_output in step.items():           #from that step.items unpack and get these values
            entry = {
                "timestamp": datetime.now().isoformat(),
                "node": node_name,
                "output": {k: v for k, v in node_output.items() if k != "chat_history"}
            }
            with open("trace_log.jsonl", "a") as f:
                f.write(json.dumps(entry, default=str) + "\n")
            print(f"[{call_label}] {node_name} ran")           #call label - first_call,second call
            final_output.update(node_output)                   #add the node_output into the running dict
    return final_output

result = run_and_log({
    "chat_history": [HumanMessage(content="Compare LangGraph vs CrewAI for production use")],
    "sub_questions": [],
    "gathered_info": [],
    "enough_info": False,
    "final_answer": "",
    "loop_count": 0
}, config, "FIRST CALL")

print("FIRST CALL")
print(result["final_answer"])

result2 = run_and_log({
    "chat_history": [HumanMessage(content="Which one is cheaper?")]
}, config, "SECOND CALL")

print("\nSECOND CALL:")
print(result2["final_answer"])

