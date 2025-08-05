from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# define state
class BMICalciState(TypedDict):
    weight_in_kg: float
    height_in_m: float
    bmi: float
    classification: str


def calculate_bmi(state: BMICalciState):
    height = state['height_in_m']
    weight = state['weight_in_kg']
    bmi = weight/(height)**2
    return {"bmi": round(bmi,1)}


def bmi_classification(state: BMICalciState):
    bmi = state['bmi']
    if bmi < 18.5:
        classification = "Underweight"
    elif bmi >= 18.5 and bmi <= 24.9:
        classification = "Normal"
    elif bmi >= 25 and bmi <= 29.9:
        classification = "Overweight"
    else:
        classification = "Obesity"

    return {"classification": classification}


# define graph
graph = StateGraph(state_schema=BMICalciState)

# define nodes
graph.add_node('calculate_bmi', calculate_bmi)
graph.add_node('classify_bmi', bmi_classification)

# define edges
graph.add_edge(START, "calculate_bmi")
graph.add_edge("calculate_bmi", "classify_bmi")
graph.add_edge("classify_bmi", END)

# compile graph
workflow = graph.compile()
print(workflow.get_graph().print_ascii()) # to see graph visually

# execute graph
result = workflow.invoke({'height_in_m': 1.83, 'weight_in_kg': 73})
print(result)
