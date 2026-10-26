import streamlit as st
import ollama
import psycopg
from pgvector.psycopg import register_vector

st.set_page_config(page_title="FutureCare Medicaid Assistant", page_icon="⚖️")
st.title("LTC Medicaid & Billing Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar_icon = "🧑‍💼" if message["role"] == "user" else "🩺"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a Medicaid or facility billing question..."):
    
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🩺"):
        try:
            conn = psycopg.connect("dbname=medicaid user=admin password=password host=127.0.0.1", autocommit=True)
            register_vector(conn)
            
            with st.spinner("Searching regulations..."):
                query_embedding = ollama.embed(model='nomic-embed-text', input=f"search_query: {prompt}").embeddings[0]
                result = conn.execute(
                    'SELECT filename, content FROM comar_rules ORDER BY embedding <=> %s::vector LIMIT 5', 
                    (query_embedding,)
                ).fetchall()

            context = ""
            if result:
                with st.expander("View Retrieved Sources"):
                    for row in result:
                        st.markdown(f"**Source:** `{row[0]}`\n> {row[1]}")
                        context += f"--- Source File: {row[0]} ---\n{row[1]}\n\n"
            
            system_instruction = f"""You are a Maryland Medicaid and Long-Term Care administrative expert. 
            Answer the user's question accurately using ONLY the provided regulatory and operational context. 
            If the answer cannot be determined from the context, state: 'The provided documentation does not contain this information.'
            
            Context:
            {context}"""

            messages_for_api = [{"role": "system", "content": system_instruction}] + st.session_state.messages

            response_stream = ollama.chat(model='llama3.2', messages=messages_for_api, stream=True)
            
            def stream_parser():
                for chunk in response_stream:
                    yield chunk['message']['content']
                    
            full_response = st.write_stream(stream_parser())
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Database or AI Connection Error: {e}")
