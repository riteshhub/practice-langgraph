from dotenv import load_dotenv
from typing import TypedDict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

article = """Technology is very important today and people use it for many things like phones, computers, and internet. There are many kinds of technology and it helps people to do work faster and easier. Without technology, life would be hard because we need it for communication, entertainment, and work. For example, phones help us talk to friends and family any time, and computers help with school and jobs. The internet is also very useful because it has a lot of information and you can find almost everything on it. But sometimes technology can cause problems too. Like, people might spend too much time on their phones or computers and not enough time outside or with other people. Also, some technology can be expensive and not everyone can afford it. Another problem is that technology can break or stop working, which can make people sad or angry. Even though technology has some problems, it still makes life better in many ways. It helps doctors find out what is wrong with patients and helps cars run better. People keep making new technology to make things even easier and faster. In future, technology will probably keep getting better and help people more. It is important to learn how to use technology in good ways and not just waste time on it. Overall, technology is a big part of the world and affects how we live every day."""

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.1,
    max_output_tokens=1024
)

prompt = PromptTemplate(
    template="Evaluate the provided {article} on a scale of 1 to 10 based on {parameter}. Return only the numeric score.",
    input_variables=['article','parameter']
    )

parser = StrOutputParser()

# define state
class ArticleEvalState(TypedDict):
    article: str
    language_usage_score: int
    clarity_of_thoughts_score: int
    content_depth_score: int
    final_score: float

def get_language_usage_score(state: ArticleEvalState):
    chain = prompt | llm | parser
    result = chain.invoke({"article":state['article'], "parameter": "language usage"})
    return {'language_usage_score': int(result)}

def get_clarity_of_thoughts_score(state: ArticleEvalState):
    chain = prompt | llm | parser
    result = chain.invoke({"article":state['article'], "parameter": "clarity of thoughts"})
    return {'clarity_of_thoughts_score': int(result)}

def get_content_depth_score(state: ArticleEvalState):
    chain = prompt | llm | parser
    result = chain.invoke({"article":state['article'], "parameter": "content depth"})
    return {'content_depth_score': int(result)}

def get_final_score(state: ArticleEvalState):
    score = (state["clarity_of_thoughts_score"] + state['content_depth_score'] + state['language_usage_score'])/3
    return {"final_score": round(score,2)}


# define graph
graph = StateGraph(ArticleEvalState)

# define nodes
graph.add_node("get_language_usage_score", get_language_usage_score)
graph.add_node("get_clarity_of_thoughts_score", get_clarity_of_thoughts_score)
graph.add_node("get_content_depth_score", get_content_depth_score)
graph.add_node("get_final_score", get_final_score)

# define edges
graph.add_edge(START, "get_language_usage_score")
graph.add_edge(START, "get_clarity_of_thoughts_score")
graph.add_edge(START, "get_content_depth_score")
graph.add_edge("get_language_usage_score", "get_final_score")
graph.add_edge("get_clarity_of_thoughts_score", "get_final_score")
graph.add_edge("get_content_depth_score", "get_final_score")
graph.add_edge("get_final_score", END)

# compile graph
workflow = graph.compile()
print(workflow.get_graph().print_ascii()) # to see graph visually

# execute graph
result = workflow.invoke({"article": article})

print(result['final_score'])
