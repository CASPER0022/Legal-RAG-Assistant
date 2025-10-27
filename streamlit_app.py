import streamlit as st
import json
from typing import List, Dict, Any

# Import your core function
from output import generate_answer


def format_parsed_result(parsed: Dict[str, Any]) -> str:
    lines: List[str] = []
    answer = parsed.get("answer") or parsed.get("answer_text") or "(no answer)"
    lines.append("Answer:")
    lines.append(f"  {answer}")
    lines.append("")

    lterms = parsed.get("legal_terms") or []
    lines.append("Legal terms found:")
    if lterms:
        for lt in lterms:
            term = lt.get("term", "")
            article = lt.get("article", "")
            quote = lt.get("quote", "")
            source = lt.get("source", "")
            lines.append(f"- {term}")
            if article:
                lines.append(f"    Article: {article}")
            if source:
                lines.append(f"    Source: {source}")
            if quote:
                qshort = quote.strip().replace("\n", " ")
                if len(qshort) > 300:
                    qshort = qshort[:297] + "..."
                lines.append(f"    Quote: {qshort}")
            lines.append("")
    else:
        lines.append("  None found")
        lines.append("")

    rarts = parsed.get("relevant_articles") or []
    lines.append("Relevant articles:")
    if rarts:
        for ra in rarts:
            art = ra.get("article", "")
            reason = ra.get("reason", "")
            lines.append(f"- {art}: {reason}")
        lines.append("")
    else:
        lines.append("  None found")
        lines.append("")

    # Note: 'sources' are intentionally omitted from the UI per user request.
    conf = parsed.get("confidence")
    if conf:
        lines.append(f"Confidence: {conf}")

    return "\n".join(lines)


def main():
    st.set_page_config(page_title="Legal Ease Chat", layout="wide")
    st.title("Legal Ease — Chat")

    # Initialize session-only history: list of messages {role: 'user'|'assistant', 'content': str, 'raw': any}
    if "history" not in st.session_state:
        st.session_state.history = []

    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        if st.button("New chat"):
            st.session_state.history = []
        if st.button("Clear stored history file"):
            try:
                import os

                if os.path.exists("chat_history.json"):
                    os.replace("chat_history.json", "chat_history.json.bak")
                    st.success("Moved existing chat_history.json to chat_history.json.bak")
                else:
                    st.info("No chat_history.json found on disk.")
            except Exception as e:
                st.error(f"Could not clear history file: {e}")

        st.markdown("---")
        st.write("This interface keeps chat history only for the current session. Use New chat to start fresh.")

    # Chat area: render prior messages in order
    chat_placeholder = st.container()

    with chat_placeholder:
        for msg in st.session_state.history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            raw = msg.get("raw")
            # Use streamlit chat components
            if role == "user":
                with st.chat_message("user"):
                    st.write(content)
            else:
                with st.chat_message("assistant"):
                    if isinstance(raw, dict):
                        # formatted view, plus expander for raw json (hide 'sources' field)
                        st.markdown("""
**Assistant (structured):**
""")
                        st.code(format_parsed_result(raw))
                        with st.expander("Raw JSON"):
                            raw_copy = dict(raw)
                            raw_copy.pop("sources", None)
                            st.json(raw_copy)
                    else:
                        st.write(content)

    # Input using chat_input for native ChatGPT-like behavior
    user_input = st.chat_input("Type your question and press Enter...")
    if user_input:
        # append user message so it shows immediately in the chat area
        st.session_state.history.append({"role": "user", "content": user_input, "raw": None})

        # create an assistant placeholder immediately so the user sees feedback
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.info("Thinking...")

        # call the heavy function (blocks) and then update the placeholder in-place
        try:
            resp = generate_answer(user_input)
        except Exception as e:
            resp = {"answer_text": f"Error: {e}"}

        # replace placeholder with final assistant content
        if isinstance(resp, dict):
            assistant_content = resp.get("answer") or resp.get("answer_text") or "(no answer)"
            # update placeholder with formatted structured output
            try:
                placeholder.code(format_parsed_result(resp))
                # also show raw JSON below inside the same placeholder area
                with st.expander("Raw JSON"):
                    st.json(resp)
            except Exception:
                placeholder.write(assistant_content)

            # store into session history
            st.session_state.history.append({"role": "assistant", "content": assistant_content, "raw": resp})
        else:
            assistant_content = str(resp)
            placeholder.write(assistant_content)
            st.session_state.history.append({"role": "assistant", "content": assistant_content, "raw": None})

        # Streamlit will re-run and render full chat history including this new assistant message


if __name__ == "__main__":
    main()
