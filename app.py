"""
app.py — Streamlit chat UI for the AI Municipality Assistant (Den Haag).

Run locally:
    streamlit run app.py

Requires:
    - data/chroma/ populated by running `python ingest.py` first
    - a Groq API key, either as the GROQ_API_KEY environment variable or
      entered in the sidebar (also works with Streamlit secrets when deployed)
"""

import os
import subprocess
import streamlit as st
from rag import answer_question, CHROMA_DIR

st.set_page_config(page_title="Den Haag Municipality Assistant", page_icon="🏛️", layout="centered")

# On a fresh deployment (e.g. Streamlit Community Cloud), data/chroma/ won't
# exist yet since it's a build artifact and is gitignored. Build it once on
# first launch so the app is usable without a manual ingest step.
if not os.path.isdir(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
    with st.spinner("First-time setup: building the document index..."):
        subprocess.run(["python", os.path.join(os.path.dirname(__file__), "ingest.py")], check=True)

st.title("🏛️ Den Haag Municipality Assistant")
st.caption(
    "Ask about moving/address registration, parking permits, passports, "
    "waste collection, or municipal taxes. Answers are grounded only in "
    "the ingested denhaag.nl pages — this is a portfolio demo, not an "
    "official municipal service."
)

with st.sidebar:
    st.header("Settings")
    default_key = os.environ.get("GROQ_API_KEY", "")
    api_key = st.text_input(
        "Groq API key",
        value=default_key,
        type="password",
        help="Get a free key at console.groq.com. Not stored anywhere.",
    )
    st.markdown("---")
    st.markdown(
        "**Scope of this demo:** a small set of Den Haag municipality pages "
        "(moving, parking, passports, waste, taxes). Ask something outside "
        "that scope and the assistant should decline rather than guess."
    )
    st.markdown(
        "[Source code on GitHub](#) · [denhaag.nl](https://www.denhaag.nl/en)"
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📄 Sources used"):
                for s in msg["sources"]:
                    st.markdown(f"**{s['title']}** (similarity distance: {s['distance']})")
                    if s["url"]:
                        st.markdown(f"[{s['url']}]({s['url']})")
                    st.markdown(f"> {s['snippet']}...")
                    st.markdown("---")

question = st.chat_input("e.g. How do I register a change of address in Den Haag?")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if not api_key:
            answer_text = "Please enter a Groq API key in the sidebar to get an answer."
            sources = []
            with st.spinner(""):
                st.markdown(answer_text)
        else:
            with st.spinner("Searching municipal documents..."):
                try:
                    result = answer_question(question, groq_api_key=api_key)
                    answer_text = result["answer"]
                    sources = result["sources"]
                except Exception as e:
                    answer_text = (
                        f"Something went wrong reaching the ChromaDB index or the LLM: {e}\n\n"
                        "Make sure you've run `python ingest.py` first."
                    )
                    sources = []

            st.markdown(answer_text)
            if sources:
                with st.expander("📄 Sources used"):
                    for s in sources:
                        st.markdown(f"**{s['title']}** (similarity distance: {s['distance']})")
                        if s["url"]:
                            st.markdown(f"[{s['url']}]({s['url']})")
                        st.markdown(f"> {s['snippet']}...")
                        st.markdown("---")

    st.session_state.messages.append(
        {"role": "assistant", "content": answer_text, "sources": sources}
    )
