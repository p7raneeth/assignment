# components.py
import streamlit as st

def render_chat(history):
    for message in history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])


def render_sources(sources):
    if not sources:
        return

    with st.expander("📄 Sources"):
        for i, src in enumerate(sources, 1):
            st.markdown(
                f"""
**Source {i} (Page {src.get("page_number", "N/A")})**  
Score: `{src["score"]:.4f}`  

{src["content"]}
"""
            )
