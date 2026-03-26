import streamlit as st
import anthropic
from pypdf import PdfReader

st.set_page_config(page_title="Knowledge Bot", page_icon="💬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fb; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
    h1 { color: #1a1a2e; }
    .doc-badge {
        display: inline-block;
        background: #e8f0fe;
        color: #1a73e8;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 4px 2px;
        font-size: 0.85em;
    }
    section[data-testid="stSidebar"] {
        background-color: #1a1a2e;
        color: white;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label { color: white !important; }
    </style>
""", unsafe_allow_html=True)

client = anthropic.Anthropic()

# Sidebar
with st.sidebar:
    st.title("💬 Knowledge Bot")
    st.caption("Powered by Claude AI")
    st.divider()

    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["txt", "pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.markdown("### 📄 Loaded documents")
        for f in uploaded_files:
            st.markdown(f"✅ {f.name}")

    st.divider()

    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

    st.caption("Built with Streamlit + Anthropic")

# Main area
st.title("Ask anything about your documents")

if not uploaded_files:
    st.info("👈 Upload one or more documents in the sidebar to get started.")
else:
    documents = {}
    for f in uploaded_files:
        if f.name.endswith(".pdf"):
            reader = PdfReader(f)
            documents[f.name] = "\n".join([page.extract_text() for page in reader.pages])
        else:
            documents[f.name] = f.read().decode("utf-8")

    combined = "\n\n---\n\n".join(
        [f"Document: {name}\n\n{text}" for name, text in documents.items()]
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if question := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=1024,
                    system=f"You are a helpful assistant for a business. Answer questions using only the documents below. If the answer isn't in the documents, say so.\n\n{combined}",
                    messages=st.session_state.messages
                )
                reply = response.content[0].text
                st.write(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
