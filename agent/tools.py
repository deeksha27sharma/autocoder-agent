# agent/tools.py

import os
from groq import Groq
from dotenv import load_dotenv
from sandbox.executor import execute_code, format_result
from agent.prompts import CODE_WRITER_PROMPT, DEBUGGER_PROMPT, EXPLAINER_PROMPT

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")


def call_llm(prompt: str, system: str = "") -> str:
    """Base function to call Groq LLM."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,  # low temp = more deterministic code
    )
    return response.choices[0].message.content.strip()


def clean_code(raw: str) -> str:
    """Strips markdown code fences if LLM wraps code in them."""
    if "```python" in raw:
        raw = raw.split("```python")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]
    return raw.strip()


def write_code(task: str) -> dict:
    """
    Tool 1: Generate Python code for a given task.
    Returns the code and execution result.
    """
    print(f"\nWriting code for: {task}")

    prompt = CODE_WRITER_PROMPT.format(task=task)
    raw_code = call_llm(prompt)
    code = clean_code(raw_code)

    print(f"\nGenerated Code:\n{code}")

    result = execute_code(code)
    print(f"\n{format_result(result)}")

    return {
        "code": code,
        "result": result
    }


def debug_code(code: str, error: str) -> dict:
    """
    Tool 2: Fix broken code using the error message.
    Returns fixed code and new execution result.
    """
    print(f"\nDebugging code. Error: {error[:100]}...")

    prompt = DEBUGGER_PROMPT.format(code=code, error=error)
    raw_fixed = call_llm(prompt)
    fixed_code = clean_code(raw_fixed)

    print(f"\n🔨 Fixed Code:\n{fixed_code}")

    result = execute_code(fixed_code)
    print(f"\n{format_result(result)}")

    return {
        "code": fixed_code,
        "result": result
    }


def explain_code(task: str, code: str) -> str:
    """
    Tool 3: Explain what the final code does in plain English.
    """
    print(f"\nExplaining code...")

    prompt = EXPLAINER_PROMPT.format(task=task, code=code)
    explanation = call_llm(prompt)

    return explanation


