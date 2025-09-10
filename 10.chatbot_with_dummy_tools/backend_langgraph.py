import sqlite3
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt.tool_node import ToolNode, tools_condition
from langchain_tools import get_current_weather, get_news

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.1,
    max_output_tokens=1024
)

tools = [get_current_weather, get_news]

llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools)

# define state
class ChatState(TypedDict):
    messages: Annotated[list[str], add_messages]

# define methods
def chat_node(state: ChatState):
    message = state["messages"]
    result = llm_with_tools.invoke(message)
    return {"messages": [result]}

sql_conn = sqlite3.connect(".db/chat_history.db", check_same_thread=False)

# define memory
memory = SqliteSaver(conn=sql_conn)

# define graph
graph = StateGraph(ChatState)

# define nodes
graph.add_node("chat", chat_node)
graph.add_node("tools", tool_node)

# define edges
graph.add_edge(START, "chat")
graph.add_conditional_edges("chat", tools_condition)
graph.add_edge("tools", "chat")

chatbot = graph.compile(checkpointer=memory)

# print(chatbot.get_graph().print_ascii())

chatbot_config = {"configurable": {"thread_id": "thread1"}}
result = chatbot.invoke({"messages": [HumanMessage(content="hello")]}, config=chatbot_config)
# result = chatbot.invoke({"messages": [HumanMessage(content="what is the latest news on Cricket")]}, config=chatbot_config)
# result = chatbot.invoke({"messages": [HumanMessage(content="get me today's weather for Indore")]}, config=chatbot_config)
# result = chatbot.invoke({"messages": [HumanMessage(content="what is the latest news of Indore and also get the current weather for the city")]}, config=chatbot_config)
print(result["messages"][-1].content)