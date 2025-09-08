from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.1,
    max_output_tokens=1024
)

parser = StrOutputParser()

# define state
class ChatState(TypedDict):
    messages: str

# define methods
def ask_question(state: ChatState):
    query = input("You: ")
    return {"messages": query}

def generate_answer(state: ChatState):
    chain = llm | parser
    result = chain.invoke(state["messages"])
    print("AI: ", result)
    return {"messages": result}

def check_user_input(state: ChatState):
    if state["messages"] and state["messages"].lower() in ["exit", "quit", "bye"]:
        return "stop"
    else:
        return "continue"

# define graph
graph = StateGraph(ChatState)

# define nodes
graph.add_node("ask_question", ask_question)
graph.add_node("generate_answer", generate_answer)

# define edges
graph.add_edge(START, "ask_question")
graph.add_conditional_edges("ask_question", check_user_input, {
    "stop": END,
    "continue": "generate_answer"
})
graph.add_edge("generate_answer", "ask_question")

workflow = graph.compile()

result = workflow.invoke({"messages": ""})