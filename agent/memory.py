# agent/memory.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from dotenv import load_dotenv

load_dotenv()

# Setup ChromaDB 
MEMORY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory", "chroma_store")

embedding_fn = embedding_functions.DefaultEmbeddingFunction()

client = chromadb.PersistentClient(path=MEMORY_PATH)

collection = client.get_or_create_collection(
    name="coding_solutions"
)

# Core Functions

def save_solution(task: str, code: str, explanation: str) -> None:
    """
    Save a successful coding solution to memory.
    """
    # Use task as the document ID (sanitized)
    doc_id = task[:50].replace(" ", "_").replace("/", "_")

    collection.upsert(
        documents=[task],
        metadatas=[{
            "code": code,
            "explanation": explanation
        }],
        ids=[doc_id]
    )
    print(f"Solution saved to memory: {task[:50]}...")


def retrieve_similar(task: str, n_results: int = 2) -> list:
    """
    Retrieve similar past solutions for a given task.
    Returns list of dicts with task, code, explanation.
    """
    try:
        results = collection.query(
            query_texts=[task],
            n_results=n_results
        )

        solutions = []
        for i, doc in enumerate(results["documents"][0]):
            solutions.append({
                "task": doc,
                "code": results["metadatas"][0][i]["code"],
                "explanation": results["metadatas"][0][i]["explanation"]
            })

        return solutions

    except Exception:
        return []  # return empty if nothing in memory yet


def format_memory_context(solutions: list) -> str:
    """
    Formats retrieved solutions into a string to inject into prompts.
    """
    if not solutions:
        return ""

    context = "Here are similar solutions from memory that may help:\n\n"
    for i, s in enumerate(solutions, 1):
        context += f"--- Past Solution {i} ---\n"
        context += f"Task: {s['task']}\n"
        context += f"Code:\n{s['code']}\n\n"

    return context


def list_all_solutions() -> list:
    """
    List all saved solutions (for debugging/display).
    """
    results = collection.get()
    solutions = []
    for i, doc in enumerate(results["documents"]):
        solutions.append({
            "task": doc,
            "code": results["metadatas"][i]["code"]
        })
    return solutions


def clear_memory() -> None:
    """
    Wipe all saved solutions from memory.
    """
    client.delete_collection("coding_solutions")
    print("Memory cleared.")