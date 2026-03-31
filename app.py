import streamlit as st
import anthropic
from pypdf import PdfReader
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quest Carpets Assistant",
    page_icon="https://questcarpet.com.au/wp-content/uploads/web-logo-1.jpg",
    layout="wide"
)

# ── Branding CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Main background */
.main {
    background-color: #f5f3f0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #1a2744 !important;
}

/* All sidebar text white */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stCaption {
    color: rgba(255,255,255,0.9) !important;
}

/* Sidebar text area */
section[data-testid="stSidebar"] textarea {
    background-color: rgba(255,255,255,0.08) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
    font-size: 0.85em !important;
}
section[data-testid="stSidebar"] textarea:focus {
    border-color: #c8973a !important;
    box-shadow: 0 0 0 2px rgba(200,151,58,0.3) !important;
}
section[data-testid="stSidebar"] textarea::placeholder {
    color: rgba(255,255,255,0.4) !important;
}

/* Sidebar file uploader */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background-color: rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 12px !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
    color: rgba(255,255,255,0.85) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background-color: #c8973a !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
}

/* Sidebar clear button */
section[data-testid="stSidebar"] .stButton > button {
    background-color: rgba(255,255,255,0.1) !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 20px !important;
    font-weight: 500 !important;
    width: 100% !important;
    padding: 8px 20px !important;
    transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(200,151,58,0.3) !important;
    border-color: #c8973a !important;
}

/* Divider */
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15) !important;
}

/* Doc badges */
.doc-badge {
    display: inline-block;
    background: rgba(200,151,58,0.25);
    border: 1px solid rgba(200,151,58,0.5);
    border-radius: 20px;
    padding: 4px 12px;
    margin: 3px 2px;
    font-size: 0.82em;
    color: white !important;
}
.base-badge {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 4px 12px;
    margin: 3px 2px;
    font-size: 0.82em;
    color: rgba(255,255,255,0.85) !important;
}

/* ── Main content headings ── */
h1 { color: #1a2744 !important; }
h2 { color: #1a2744 !important; }
h3 { color: #1a2744 !important; }

/* ── Chat input ── */
div[data-testid="stChatInput"] {
    border: 2px solid #d4c4a8 !important;
    border-radius: 16px !important;
    background-color: white !important;
    padding: 4px 12px !important;
    box-shadow: 0 2px 8px rgba(26,39,68,0.08) !important;
}
div[data-testid="stChatInput"]:focus-within {
    border-color: #c8973a !important;
    box-shadow: 0 2px 12px rgba(200,151,58,0.2) !important;
}

/* ── Chat messages ── */
div[data-testid="stChatMessage"] {
    background-color: white !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 1px 4px rgba(26,39,68,0.06) !important;
    padding: 12px 16px !important;
}

/* ── Welcome cards ── */
.welcome-card {
    background: white;
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 20px;
    border-left: 4px solid #c8973a;
    box-shadow: 0 2px 8px rgba(26,39,68,0.06);
}
.feature-grid {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin-top: 16px;
}
.feature-pill {
    background: #f0ece4;
    border: 1px solid #d4c4a8;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 0.875em;
    color: #1a2744;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# ── Anthropic client ──────────────────────────────────────────────────────────
client = anthropic.Anthropic()

# ── Load base knowledge (questcarpet.txt) ─────────────────────────────────────
BASE_KNOWLEDGE = ""
base_doc_path = os.path.join(os.path.dirname(__file__), "questcarpet.txt")
if os.path.exists(base_doc_path):
    with open(base_doc_path, "r", encoding="utf-8") as f:
        BASE_KNOWLEDGE = f.read()

# ── Default bot instructions ──────────────────────────────────────────────────
DEFAULT_INSTRUCTIONS = """You are a friendly and knowledgeable assistant for Quest Carpets — a Melbourne-based carpet manufacturer established in 1978.

Your role:
- Answer questions about Quest Carpets products, styles, care, and company info
- Be warm, helpful, and professional in your responses
- Keep answers concise and easy to read
- If asked about pricing or where to buy, remind customers that Quest Carpets sells through retailers and suggest they call 1800 337 404 or visit a local carpet retailer
- If a question isn't covered by the documents, say so politely and offer the contact number

Tone: Friendly, knowledgeable, and Australian. Like a helpful team member at a carpet showroom."""

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="text-align:center; padding: 16px 0 8px 0;">
        <img src="https://questcarpet.com.au/wp-content/uploads/web-logo-1.jpg"
             style="max-width: 180px; border-radius: 8px;"
             onerror="this.style.display='none'" />
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🤖 Knowledge Assistant")
    st.caption("Powered by Claude AI")
    st.divider()

    # Bot instructions
    st.markdown("**Bot Instructions**")
    st.caption("Customise how the bot responds")
    custom_instructions = st.text_area(
        "Instructions",
        value=DEFAULT_INSTRUCTIONS,
        height=200,
        label_visibility="collapsed",
        placeholder="Type instructions for the bot here...",
        key="custom_instructions"
    )
    st.divider()

    # Pre-loaded knowledge
    st.markdown("**Knowledge Base**")
    if BASE_KNOWLEDGE:
        st.markdown('<span class="base-badge">📋 Quest Carpets (built-in)</span>', unsafe_allow_html=True)
    else:
        st.caption("⚠️ questcarpet.txt not found in the same folder as app.py")

    # Extra document uploads
    st.caption("Upload extra documents (optional):")
    uploaded_files = st.file_uploader(
        "Extra documents",
        type=["txt", "pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    if uploaded_files:
        for f in uploaded_files:
            st.markdown(f'<span class="doc-badge">📄 {f.name}</span>', unsafe_allow_html=True)

    st.divider()

    if st.button("🗑️  Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Quest Carpets © 2026")

# ── Build combined knowledge ──────────────────────────────────────────────────
documents = {}

# Always include base knowledge
if BASE_KNOWLEDGE:
    documents["Quest Carpets Knowledge Base"] = BASE_KNOWLEDGE

# Add uploaded files
if uploaded_files:
    for f in uploaded_files:
        if f.name.endswith(".pdf"):
            reader = PdfReader(f)
            documents[f.name] = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        else:
            documents[f.name] = f.read().decode("utf-8")

combined = "\n\n---\n\n".join([f"=== {name} ===\n\n{text}" for name, text in documents.items()])

# ── Main area ─────────────────────────────────────────────────────────────────
if not documents:
    # Nothing loaded yet
    st.markdown("""
    <div class="welcome-card">
        <h2 style="margin-top:0; color:#1a2744;">👋 Welcome to Quest Carpets Assistant</h2>
        <p style="color:#555; margin-bottom:16px;">
            Add your <strong>questcarpet.txt</strong> file to the same folder as app.py to get started,
            or upload any document in the sidebar.
        </p>
        <div class="feature-grid">
            <span class="feature-pill">📋 Product info</span>
            <span class="feature-pill">🎨 Carpet styles</span>
            <span class="feature-pill">🧹 Care & maintenance</span>
            <span class="feature-pill">📞 Contact details</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Show header
    doc_count = len(documents)
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
        <h2 style="margin:0; color:#1a2744;">💬 Quest Carpets Assistant</h2>
        <span style="background:#f0ece4; border:1px solid #d4c4a8; border-radius:20px;
                     padding:4px 14px; font-size:0.8em; color:#1a2744; font-weight:500;">
            {doc_count} document{"s" if doc_count > 1 else ""} loaded
        </span>
    </div>
    <p style="color:#666; margin-bottom:20px; font-size:0.9em;">
        Ask me anything about carpets, products, styles, care, or company info.
    </p>
    """, unsafe_allow_html=True)

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    if question := st.chat_input("Ask a question about Quest Carpets..."):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Looking that up..."):
                system_prompt = f"""{custom_instructions}

The following documents contain all the information you have access to. Only answer based on these documents.

{combined}"""

                response = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=1024,
                    system=system_prompt,
                    messages=st.session_state.messages
                )
                reply = response.content[0].text
                st.write(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})