# ui/app.py

import sys
import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "https://autocoder-agent.onrender.com")

# Page Config
st.set_page_config(
    page_title="AutoCoder Agent",
    page_icon="🤖",
    layout="wide"
)

# Header
st.title("🤖 AutoCoder Agent")
st.caption("An autonomous coding assistant powered by LLaMA 3.3 + LangGraph")
st.divider()

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("⚙️ Agent Info")
    st.markdown("""
    **Model:** LLaMA 3.3 70B (Groq)
    
    **Framework:** LangGraph
    
    **Tools:**
    -  Code Writer
    -  Auto Debugger
    -  Code Explainer
    
    **Max Retries:** 3
    """)

    st.divider()
    st.header("📋 Example Tasks")

    examples = [
        "Write a binary search algorithm",
        "Create a calculator with basic operations",
        "Write a function to check if a string is a palindrome",
        "Sort a list of dictionaries by a key",
        "Write a simple stack implementation"
    ]

    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state.prefill = example

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(message["explanation"])
            with st.expander("View Generated Code"):
                st.code(message["code"], language="python")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Success", "✅ Yes" if message["success"] else "❌ No")
            with col2:
                st.metric("Attempts", message["attempts"])
        else:
            st.markdown(message["content"])

# Chat Input
prefill = st.session_state.pop("prefill", "")
task = st.chat_input("Describe a coding task...")

if prefill and not task:
    task = prefill

if task:
    # Show user message
    with st.chat_message("user"):
        st.markdown(task)
    st.session_state.messages.append({"role": "user", "content": task})

    # Run agent via API
    with st.chat_message("assistant"):
        with st.spinner(" Agent is thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/run",
                    json={"task": task},
                    timeout=120
                )
                if response.status_code == 200:
                    result = response.json()
                else:
                    st.error(f"API error: {response.text}")
                    st.stop()
            except requests.exceptions.Timeout:
                st.error("⏱Request timed out. The API may be waking up, try again in 30 seconds.")
                st.stop()
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
                st.stop()

        # Show results
        st.markdown(result["explanation"])

        with st.expander(" View Generated Code"):
            st.code(result["code"], language="python")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Success", "✅ Yes" if result["success"] else "❌ No")
        with col2:
            st.metric("Attempts", result["attempts"])

    # Save to history
    st.session_state.messages.append({
        "role": "assistant",
        "explanation": result["explanation"],
        "code": result["code"],
        "success": result["success"],
        "attempts": result["attempts"]
    })