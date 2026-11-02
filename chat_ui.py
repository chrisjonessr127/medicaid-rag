"""Local Streamlit UI. Not intended for remote/unauthenticated public access."""
import streamlit as st
from rag_core import answer_question

st.set_page_config(page_title="Local RAG Demo", page_icon="📚")
st.title("Local RAG — Fictional Document Demo")
st.warning("Synthetic test policies only. Not real healthcare or benefits advice. "
           "Do not upload proprietary or personal records.")

if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask about the fictional demo process...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching fictional documents locally..."):
                result, sources = answer_question(question)
            st.markdown(result)
            if sources:
                with st.expander("View retrieved fictional sources"):
                    for name, paragraph in sources:
                        st.markdown(f"**{name}**\n\n> {paragraph}")
            st.session_state.messages.append({"role": "assistant", "content": result})
        except Exception as exc:
            st.error(f"Local AI or database error: {exc}")
