from typing import TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.1,
    max_output_tokens=200
)

class CustomerSupportState(TypedDict):
    user_query: str
    issue_type: str
    response: str

def get_issue_type(state: CustomerSupportState) -> str:
    prompt = PromptTemplate(
        input_variables=["user_query"],
        template="Given the user query: {user_query}, choose one issue type from ['technical', 'billing', 'general']. Only reply with the type.",
    )
    chain = prompt | llm | StrOutputParser()
    issue_type = chain.invoke({"user_query": state["user_query"]})
    return {"issue_type": issue_type}

def handle_technical_issue(state: CustomerSupportState) -> str:
    prompt = PromptTemplate(
        input_variables=["user_query"],
        template="Given the user query: {user_query}, provide a solution for a technical issue.",
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"user_query": state["user_query"]})
    return {"response": response}

def handle_billing_issue(state: CustomerSupportState) -> str:
    prompt = PromptTemplate(
        input_variables=["user_query"],
        template="Given the user query: {user_query}, provide a solution for a billing issue.",
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"user_query": state["user_query"]})
    return {"response": response}

def handle_general_issue(state: CustomerSupportState) -> str:
    prompt = PromptTemplate(
        input_variables=["user_query"],
        template="Given the user query: {user_query}, provide a solution for a general issue.",
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"user_query": state["user_query"]})
    return {"response": response}

def route_issue(state: CustomerSupportState) -> str:
    issue_type = state["issue_type"]
    if issue_type == "technical":
        return "handle_technical_issue"
    elif issue_type == "billing":
        return "handle_billing_issue"
    else:
        return "handle_general_issue"

graph = StateGraph(CustomerSupportState)

graph.add_node("get_issue_type", get_issue_type)
graph.add_node("handle_technical_issue", handle_technical_issue)
graph.add_node("handle_billing_issue", handle_billing_issue)
graph.add_node("handle_general_issue", handle_general_issue)

graph.add_edge(START, "get_issue_type")
graph.add_conditional_edges("get_issue_type", route_issue)
graph.add_edge("handle_technical_issue", END)
graph.add_edge("handle_billing_issue", END)
graph.add_edge("handle_general_issue", END)

workflow = graph.compile()

result = workflow.invoke({"user_query": "I need help with my billing issue."})
print(result)
