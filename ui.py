import streamlit as st
import ollama
import psycopg
from pgvector.psycopg import register_vector

st.set_page_config(page_title="Medicaid RAG", page_icon="⚖️")
st.title("Maryland Medicaid & LTC Assistant")

question = st.text_input("Ask a regulatory or operational question:")

if st.button("Search") and question:
    with st.spinner("Searching regulations..."):
        try:
            # Connect to your local PostgreSQL container
            conn = psycopg.connect("dbname=medicaid user=admin password=password host=127.0.0.1", autocommit=True)
            register_vector(conn)
            
            # Embed the user question
            query_embedding = ollama.embed(model='nomic-embed-text', input=f"search_query: {question}").embeddings[0]
            
            # Retrieve top 5 matching rules
            result = conn.execute(
                'SELECT filename, content FROM comar_rules ORDER BY embedding <=> %s::vector LIMIT 5', 
                (query_embedding,)
            ).fetchall()
            
            if not result:
                st.warning("No relevant context found in database.")
            else:
                context = ""
                # Build an expandable UI element to view the raw source files
                with st.expander("View Retrieved Sources"):
                    for row in result:
                        st.markdown(f"**Source:** `{row[0]}`\n> {row[1]}")
                        context += f"--- Source File: {row[0]} ---\n{row[1]}\n\n"
                
                prompt = f"""You are a Maryland Medicaid and Long-Term Care administrative expert. 
                Answer the user's question accurately using ONLY the provided regulatory and operational context. 
                Cite the source file and any specific rules, limits, or guidelines mentioned. 
                If the answer cannot be determined from the context, state: 'The provided documentation does not contain this information.'
                
                Context:
                {context}
                
                Question: {question}
                """
                
                # Query Llama 3.2 via the Windows API
                response = ollama.generate(model='llama3.2', prompt=prompt)
                
                st.success("Expert Response")
                st.write(response.response)
                
        except Exception as e:
            st.error(f"System Error: {e}")
