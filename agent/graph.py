# agent/graph.py

from agent.memory import save_solution, retrieve_similar, format_memory_context
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TypedDict
from langgraph.graph import StateGraph, END
from agent.tools import write_code, debug_code, explain_code
from agent.prompts import PLANNER_PROMPT, SYSTEM_PROMPT
from agent.tools import call_llm

# 1. State Schema
class AgentState(TypedDict):
    task: str          # original user request
    code: str          # latest generated/fixed code
    error: str         # latest error message (empty if none)
    result: dict       # latest execution result
    explanation: str   # final explanation to show user
    attempts: int      # how many debug attempts so far
    status: str        # WRITE / DEBUG / ANSWER / DONE

MAX_ATTEMPTS = 3       # max debug retries before giving up


# 2. Node Functions 

def planner_node(state: AgentState) -> AgentState:
    """Decides what to do next: WRITE, DEBUG, or ANSWER."""
    print(f"\nPlanner thinking... (attempt {state['attempts']})")

    prompt = PLANNER_PROMPT.format(
        task=state["task"],
        code=state["code"],
        error=state["error"]
    )
    decision = call_llm(prompt).strip().upper()

    # Safety: force valid decision
    if decision not in ["WRITE", "DEBUG", "ANSWER"]:
        decision = "WRITE" if not state["code"] else "DEBUG"

    print(f"Planner decision: {decision}")
    return {**state, "status": decision}


def writer_node(state: AgentState) -> AgentState:
    """Writes fresh code, using memory context if available."""

    # Retrieve similar past solutions
    similar = retrieve_similar(state["task"])
    memory_context = format_memory_context(similar)

    # Inject memory into task if available
    enriched_task = state["task"]
    if memory_context:
        print(f"\nFound {len(similar)} similar solution(s) in memory!")
        enriched_task = f"{memory_context}\nNow solve this task:\n{state['task']}"

    output = write_code(enriched_task)
    result = output["result"]

    return {
        **state,
        "code": output["code"],
        "result": result,
        "error": result["stderr"] if not result["success"] else "",
        "attempts": state["attempts"] + 1
    }

def debugger_node(state: AgentState) -> AgentState:
    """Fixes broken code using the error."""
    output = debug_code(state["code"], state["error"])
    result = output["result"]

    return {
        **state,
        "code": output["code"],
        "result": result,
        "error": result["stderr"] if not result["success"] else "",
        "attempts": state["attempts"] + 1
    }


def explainer_node(state: AgentState) -> AgentState:
    """Explains the final code and saves to memory."""
    explanation = explain_code(state["task"], state["code"])

    # Save successful solutions to memory
    if state["result"].get("success"):
        save_solution(state["task"], state["code"], explanation)

    return {**state, "explanation": explanation, "status": "DONE"}

# 3. Routing Logic

def route(state: AgentState) -> str:
    """Routes to next node based on current state."""

    # Too many attempts — give up and explain what we have
    if state["attempts"] >= MAX_ATTEMPTS:
        print(f"\nMax attempts reached. Moving to explanation.")
        return "explainer"

    # Code ran successfully — explain it
    if state.get("result") and state["result"].get("success"):
        return "explainer"

    # Route based on planner decision
    if state["status"] == "WRITE":
        return "writer"
    elif state["status"] == "DEBUG":
        return "debugger"
    elif state["status"] == "ANSWER":
        return "explainer"

    return "explainer"


# 4. Build the Graph

def build_graph():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("planner", planner_node)
    graph.add_node("writer", writer_node)
    graph.add_node("debugger", debugger_node)
    graph.add_node("explainer", explainer_node)

    # Entry point
    graph.set_entry_point("planner")

    # Edges from planner
    graph.add_conditional_edges("planner", route)

    # After writing/debugging → go back to planner
    graph.add_edge("writer", "planner")
    graph.add_edge("debugger", "planner")

    # Explainer is the end
    graph.add_edge("explainer", END)

    return graph.compile()


# 5. Run Function

def run_agent(task: str) -> dict:
    """Main entry point to run the agent on a task."""
    app = build_graph()

    initial_state: AgentState = {
        "task": task,
        "code": "",
        "error": "",
        "result": {},
        "explanation": "",
        "attempts": 0,
        "status": "WRITE"
    }

    print(f"\n{'='*50}")
    print(f"AutoCoder Agent Starting")
    print(f"Task: {task}")
    print(f"{'='*50}")

    final_state = app.invoke(initial_state)

    print(f"\n{'='*50}")
    print(f"✅ Agent Finished!")
    print(f"{'='*50}")
    print(f"\nExplanation:\n{final_state['explanation']}")

    return final_state



