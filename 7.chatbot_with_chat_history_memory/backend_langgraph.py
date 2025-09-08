import uuid
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
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
def chat(state: ChatState):
    message = state["messages"]
    chain = llm | parser
    result = chain.invoke(message)
    return {"messages": [AIMessage(content=result)]}

# define memory
memory = MemorySaver()

# define graph
graph = StateGraph(ChatState)

# define nodes
graph.add_node("chat", chat)

# define edges
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

chatbot = graph.compile(checkpointer=memory)
