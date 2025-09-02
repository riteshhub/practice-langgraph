import uuid
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.1,
    max_output_tokens=1024
)

parser = StrOutputParser()

# define state
class ChatState(TypedDict):
    messages: Annotated[list[str], add_messages]

# define methods
def ask_question(state: ChatState):
    query = input("You: ")
    return {"messages": [HumanMessage(content=query)]}

def generate_answer(state: ChatState):
    new_message = state["messages"]
    chain = llm | parser
    result = chain.invoke(new_message)
    print("AI: ", result)
    return {"messages": [AIMessage(content=result)]}

def check_user_input(state: ChatState):
    new_message = state["messages"][-1].content
    if new_message.lower() in ["exit", "quit", "bye"]:
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

memory = MemorySaver()

workflow = graph.compile(checkpointer=memory)

session_id = str(uuid.uuid4())
chatbot_config = {"configurable": {"thread_id": session_id}}

result = workflow.invoke({"messages": ""}, config=chatbot_config)