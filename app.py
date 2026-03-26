import streamlit as st
import anthropic
from pypdf import PdfReader

st.set_page_config(page_title="Knowledge Bot", page_icon="💬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: #fffbf7;
    }

    .stChatMessage {
        border-radius: 18px;
        padding: 4px;
        margin-bottom: 8px;
    }

    .stChatMessage[data-testid="chat-message-user"] {
        background-color: #fff0e0;
    }

    .stChatMessage[data-testid="chat-message-assistant"] {
        background-color: #f0f7ff;
    }

    section[data-testid="stSidebar"] {
        background-color: #ff914d;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    section[data-testid="stSidebar"] .stFileUploader {
        background-color: rgba(255,255,255,0.15);
        border: 2px dashed rgba(255,255,255,0.5);
        border-radius: 16px;
        padding: 10px;
    }

    .stButton > button {
        background-color: white;
        color: #ff914d !important;
        border: none;
        border-radius: 20px;
        padding: 6px 20px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #fff0e0;
    }

    .stChatInput textarea {
        border-radius: 20px;
        border: 2px solid #ffd4b0;
        background-color: white;
    }

    .doc-badge {
        display: inline-block;
        background: rgba(255,255,255,0.25);
        border-radius: 20px;
        padding: 4px 12px;
        margin: 3px 2px;
        font-size: 0.85em;
    }

    h1 {
        color: #c45f1a;
    }
    </style>
""", unsafe_allow_html=True)

client = anthropic.Anthropic()

with st.sidebar:
    st.markdown("## 💬 Knowledge Bot")
    st.caption("Your friendly AI assistant")
    st.divider()

    uploaded_files = st.file_uploader(
        "Upload your documents",
        type=["txt", "pdf"],
        accept_multiple_files=True,
        help="Upload menus, policies, price lists — anything!"
    )

    if uploaded_files:
        st.markdown("**Loaded:**")
        for f in uploaded_files:
            st.markdown(f'<span class="doc-badge">📄 {f.name}</span>', unsafe_allow_html=True)

    st.divider()

    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

    st.caption("Powered by Claude AI ✨")

if not uploaded_files:
    st.markdown("# 👋 Hi there!")
    st.markdown("Upload your business documents in the sidebar and I'll answer any questions about them — instantly.")
    st.markdown("**Great for:** menus, staff policies, price lists, FAQs, and more.")
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

    st.markdown("# 💬 Ask me anything!")
    st.caption(f"I've read {len(documents)} document(s) and I'm ready to help.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if question := st.chat_input("Type your question here..."):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Let me check that for you..."):
                response = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=1024,
                    system=f"You are a warm, friendly assistant for a business. Answer questions using only the documents below. Keep answers concise and helpful. If the answer isn't in the documents, say so kindly.\n\n{combined}",
                    messages=st.session_state.messages
                )
                reply = response.content[0].text
                st.write(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
