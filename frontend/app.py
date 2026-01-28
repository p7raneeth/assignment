# app.py
import streamlit as st
from api_client import upload_pdf, query_rag
from components import render_chat, render_sources
from config import UPLOAD_ENDPOINT, QUERY_ENDPOINT

st.set_page_config(page_title="PDF QA Chatbot", layout="wide")

st.title("📄 PDF QA Chatbot")

# -------------------------------
# Session state
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# -------------------------------
# Sidebar: PDF Upload
# -------------------------------
with st.sidebar:
    st.header("📄 Upload PDFs")

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        accept_multiple_files=False
    )

    if uploaded_file and st.button("Upload"):
        with st.spinner("Uploading and processing PDF..."):
            try:
                response = upload_pdf(uploaded_file, UPLOAD_ENDPOINT)
                st.success(response["message"])
                st.session_state.uploaded_files.append(uploaded_file.name)
            except Exception as e:
                st.error(str(e))

    if st.session_state.uploaded_files:
        st.subheader("Uploaded Files")
        for f in st.session_state.uploaded_files:
            st.write(f"✅ {f}")

# -------------------------------
# Main Chat UI
# -------------------------------
render_chat(st.session_state.chat_history)

query = st.chat_input("Ask a question about your documents")

if query:
    # Show user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": query
    })

    with st.spinner("Thinking..."):
        try:
            payload = {
                "query": query,
                "conversation_history": st.session_state.chat_history[:-1],
                "top_k": 3
            }

            response = query_rag(payload, QUERY_ENDPOINT)

            # Assistant message
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response["answer"]
            })

            st.rerun()

        except Exception as e:
            st.error(str(e))

# -------------------------------
# Render latest sources
# -------------------------------
if st.session_state.chat_history:
    if "sources" in locals():
        render_sources(response.get("sources", []))
