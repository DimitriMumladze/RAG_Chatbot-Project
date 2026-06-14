"""
app_streamlit.py — მარტივი ვებ-ინტერფეისი (არასავალდებულო).

გაშვება:
    python -m src.ingest
    streamlit run app_streamlit.py
"""
import streamlit as st
from src.rag import RAGPipeline


@st.cache_resource
def get_pipeline():
    """მოდელი/ბაზა ერთხელ ჩაიტვირთოს და გადანახული დარჩეს."""
    return RAGPipeline()


st.set_page_config(page_title="IBSU მიღების ჩატბოტი", page_icon="🎓")
st.title("🎓 მიღების ჩატბოტი (DEMO)")
st.caption("RAG არქიტექტურაზე დაფუძნებული პროტოტიპი — სადემონსტრაციო მონაცემები.")

rag = get_pipeline()

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("დასვით კითხვა მიღების შესახებ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("ვამუშავებ..."):
            out = rag.answer(prompt)
        st.markdown(out["answer"])
        with st.expander("გამოყენებული წყაროები"):
            for s in out["sources"]:
                st.write(f"- **{s['question']}** _(მსგავსება: {s['similarity']})_")
    st.session_state.messages.append({"role": "assistant", "content": out["answer"]})
