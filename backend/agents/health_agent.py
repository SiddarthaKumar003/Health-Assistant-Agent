# import os
# from typing import Annotated, TypedDict

# from dotenv import load_dotenv

# from langchain_groq import ChatGroq
# from langchain_core.messages import AnyMessage
# from langgraph.graph.message import add_messages


# load_dotenv()


# class HealthState(TypedDict):
#     messages: Annotated[list[AnyMessage], add_messages]


# llm = ChatGroq(
#     model="openai/gpt-oss-120b",
#     temperature=0
# )

# from backend.tools.medical_tools import (
#     emergency_check,
#     symptom_information,
#     medical_information,
# )


# tools = [
#     emergency_check,
#     symptom_information,
#     medical_information,
# ]

# llm_with_tools = llm.bind_tools(tools)

# from langchain_core.messages import SystemMessage


# SYSTEM_PROMPT = """
# You are HealthMate, a health information assistant.

# Your role is to provide general health information and help users
# understand health-related topics.

# IMPORTANT SAFETY RULES:

# 1. Do not claim to diagnose a disease.
# 2. Do not prescribe medication.
# 3. Do not tell users to start, stop, or change prescription medication.
# 4. Do not present uncertain information as a medical fact.
# 5. If the user describes a potential emergency, prioritize urgent
#    professional medical evaluation.
# 6. Ask relevant follow-up questions when necessary.
# 7. Clearly communicate uncertainty.
# 8. Encourage professional medical evaluation when appropriate.

# You have access to health information tools. Use them when useful.
# """


# def health_agent(state: HealthState):

#     messages = [
#         SystemMessage(content=SYSTEM_PROMPT),
#         *state["messages"]
#     ]

#     response = llm_with_tools.invoke(messages)

#     return {
#         "messages": [response]
#     }

#     from langgraph.prebuilt import ToolNode


# tool_node = ToolNode(tools)

# from langgraph.graph import END


# def should_continue(state: HealthState):

#     last_message = state["messages"][-1]

#     if getattr(last_message, "tool_calls", None):
#         return "tools"

#     return END

# from langgraph.graph import StateGraph, START

# builder = StateGraph(HealthState)

# builder.add_node("health_agent", health_agent)
# builder.add_node("tools", tool_node)

# builder.add_edge(START, "health_agent")

# builder.add_conditional_edges(
#     "health_agent",
#     should_continue,
#     {
#         "tools": "tools",
#         END: END,
#     }
# )

# builder.add_edge("tools", "health_agent")

# health_graph = builder.compile()

# def ask_health_agent(message: str):

#     result = health_graph.invoke(
#         {
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": message
#                 }
#             ]
#         }
#     )

#     return result["messages"][-1].content
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from backend.tools.doctor_finder import find_nearby_doctors

from backend.tools.medical_tools import (
    emergency_check,
    symptom_information,
    medical_information,
)


load_dotenv()

from typing import Optional
class HealthState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    latitude: Optional[float]
    longitude: Optional[float]


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


tools = [
    emergency_check,
    symptom_information,
    medical_information,
    find_nearby_doctors,
]


llm_with_tools = llm.bind_tools(tools)


SYSTEM_PROMPT = """
You are HealthMate, a health information assistant.

Your role is to provide general health information and help users
understand health-related topics.

IMPORTANT SAFETY RULES:

1. Do not claim to diagnose a disease.
2. Do not prescribe medication.
3. Do not tell users to start, stop, or change prescription medication.
4. Do not present uncertain information as a medical fact.
5. If the user describes a potential emergency, prioritize urgent
   professional medical evaluation.
6. Ask relevant follow-up questions when necessary.
7. Clearly communicate uncertainty.
8. Encourage professional medical evaluation when appropriate.

NEARBY HEALTHCARE RULES:

9. If the user explicitly asks for a nearby doctor, clinic,
   hospital, or healthcare provider, use the find_nearby_doctors tool
   when latitude and longitude are available.

10. Never invent a doctor's name, address, phone number, distance,
    rating, opening hours, or Maps link.

11. If location information is unavailable, tell the user that
    location permission is required to find nearby providers.

12. Nearby provider search results are directory information.
    Do not describe a provider as medically superior based only
    on rating, distance, or search ranking.

13. If the situation appears to be an emergency, do not delay
    emergency guidance while searching for routine healthcare.

You have access to health information tools. Use them when useful.
"""


def health_agent(state: HealthState):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"]
    ]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }


tool_node = ToolNode(tools)


def should_continue(state: HealthState):

    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return END


builder = StateGraph(HealthState)

builder.add_node("health_agent", health_agent)
builder.add_node("tools", tool_node)

builder.add_edge(START, "health_agent")

builder.add_conditional_edges(
    "health_agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    }
)

builder.add_edge("tools", "health_agent")


health_graph = builder.compile()


from typing import Optional


def ask_health_agent(
    message: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
):
 
    result = health_graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ],
            "latitude": latitude,
            "longitude": longitude,
        }
    )

    return result["messages"][-1].content
