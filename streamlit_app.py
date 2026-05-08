import streamlit as st
import json
from typing import List, Dict, Any
from output import generate_answer

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="LegalEase AI",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS for Premium Look
    st.markdown("""
        <style>
        .main {
            background-color: #0e1117;
        }
        .stChatMessage {
            background-color: #1e2227;
            border-radius: 15px;
            margin-bottom: 10px;
            border: 1px solid #30363d;
        }
        .stMarkdown h1 {
            color: #58a6ff;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }
        .legal-card {
            background-color: #161b22;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #238636;
            margin-bottom: 10px;
        }
        .legal-term {
            color: #d2a8ff;
            font-weight: bold;
        }
        .legal-article {
            color: #79c0ff;
            font-size: 0.9em;
        }
        .sidebar .sidebar-content {
            background-color: #161b22;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("⚖️ LegalEase — RAG Advisor")
    st.markdown("---")

    if "history" not in st.session_state:
        st.session_state.history = []

    with st.sidebar:
        st.header("🛠️ Dashboard")
        st.info("Advanced RAG: Hybrid Search + FlashRank Reranking enabled.")
        
        if st.button("🆕 New Conversation", use_container_width=True):
            st.session_state.history = []
            st.rerun()
            
        st.markdown("---")
        st.subheader("Metrics (Live)")
        st.metric("Model", "GPT-4o-mini")
        st.metric("Retrieval", "Hybrid + Rerank")
        
        with st.expander("About LegalEase"):
            st.write("""
                LegalEase uses state-of-the-art Retrieval Augmented Generation (RAG) to provide accurate legal guidance.
                - **Dense Retrieval**: Sentence Transformers
                - **Re-ranking**: FlashRank (Cross-Encoders)
                - **LLM**: GPT-4o-mini
            """)

    # Chat display
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.write(msg["content"])
            else:
                raw = msg.get("raw")
                if isinstance(raw, dict):
                    st.markdown(f"### Answer\n{raw.get('answer', 'No answer found.')}")
                    
                    if raw.get("legal_terms"):
                        st.markdown("#### 📚 Relevant Legal Terms")
                        for term in raw["legal_terms"]:
                            st.markdown(f"""
                                <div class="legal-card">
                                    <span class="legal-term">{term.get('term', 'N/A')}</span><br/>
                                    <span class="legal-article">Citation: {term.get('article', 'N/A')}</span><br/>
                                    <p style='font-style: italic; color: #8b949e; font-size: 0.9em;'>"{term.get('quote', '')}"</p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                    if raw.get("relevant_articles"):
                        with st.expander("📖 View Referenced Articles"):
                            for art in raw["relevant_articles"]:
                                st.markdown(f"**{art.get('article')}**: {art.get('reason')}")
                    
                    st.caption(f"Confidence Level: {raw.get('confidence', 'Unknown')}")
                else:
                    st.write(msg["content"])

    # Chat Input
    user_input = st.chat_input("Ask a legal question...")
    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing legal documents and re-ranking results..."):
                try:
                    resp = generate_answer(user_input)
                    st.session_state.history.append({"role": "assistant", "content": "", "raw": resp})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating answer: {e}")

if __name__ == "__main__":
    main()
