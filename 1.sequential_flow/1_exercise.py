from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# define state
class MultiplyState(TypedDict):
    first_number: int
    second_number: int
    answer: int


def do_multiply(state: MultiplyState) -> MultiplyState:
    a = state['first_number']
    b = state['second_number']
    c = a*b
    state['answer'] = c
    return state

# define graph
graph = StateGraph(state_schema=MultiplyState)

# define nodes
node = graph.add_node('do_multiply', do_multiply)

# define edges
graph.add_edge(START, "do_multiply")
graph.add_edge("do_multiply", END)

# compile graph
workflow = graph.compile()
print(workflow.get_graph().print_ascii())

# execute graph
result = workflow.invoke({'first_number': 8, 'second_number': 5})
print(result)



