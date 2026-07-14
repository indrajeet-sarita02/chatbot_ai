import streamlit as st
import uuid
from graph.graph import run_graph
from graph.state import ChatState
from db.connection import get_connection
from db.schema import create_tables
from db.seed import seed

st.set_page_config(page_title="ShopEase AI Assistant By Indrajeet", page_icon="🛍️", layout="wide")

conn = get_connection()
create_tables(conn)
seed()
conn.close()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = "GUEST"
if "user_name" not in st.session_state:
    st.session_state.user_name = "Guest"
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

with st.sidebar:
    st.markdown("### 🛍️ ShopEase")

    st.markdown("#### 👤 User Login")
    user_option = st.selectbox(
        "Select user:",
        options=["Guest", "Rajesh Kumar (U1001)", "Priya Sharma (U1002)"],
        index=0
    )
    if "Rajesh" in user_option:
        st.session_state.user_id = "U1001"
        st.session_state.user_name = "Rajesh Kumar"
    elif "Priya" in user_option:
        st.session_state.user_id = "U1002"
        st.session_state.user_name = "Priya Sharma"
    else:
        st.session_state.user_id = "GUEST"
        st.session_state.user_name = "Guest"

    st.markdown(f"**Logged in as:** {st.session_state.user_name}")

    st.markdown("#### 💡 Try asking:")
    sample_queries = [
        "Where is my order?",
        "Show me Bluetooth headphones under ₹3000",
        "What is today's weather in Delhi?",
        "Recommend me a laptop",
        "Cancel my order ORD-1001",
        "What is your return policy?",
        "Compare iPhone and Samsung",
        "Has my refund been processed?",
    ]
    for q in sample_queries:
        if st.button(q):
            st.session_state.pending_query = q

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())[:8]

st.markdown("""
<style>
* { font-family: 'Inter', sans-serif; box-sizing: border-box; }

.phone-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 85vh;
}

.phone {
    width: 420px;
    height: 820px;
    background: #fff;
    border-radius: 40px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0,0,0,.18);
}

/* Header */
.header {
    padding: 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #075E54;
    border-bottom: 1px solid #075E54;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 15px;
}

.back-icon {
    font-size: 30px;
    color: white;
    cursor: pointer;
}

.avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: url("https://picsum.photos/100") center/cover;
}

.company-name {
    font-size: 20px;
    font-weight: 700;
    color: white;
}

.verify-badge {
    background: #25D366;
    color: #fff;
    width: 54px;
    height: 40px;
    border-radius: 22px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 22px;
}

/* Chat area */
.chat {
    flex: 1;
    overflow-y: auto;
    padding: 18px;
    background: #e5ddd5;
}

.message {
    display: flex;
    margin-bottom: 18px;
}

.left-msg { justify-content: flex-start; }
.right-msg { justify-content: flex-end; }

.bubble {
    max-width: 78%;
    padding: 14px 18px;
    border-radius: 22px;
    font-size: 16px;
    line-height: 1.5;
    word-wrap: break-word;
}

.bubble-bot {
    background: #FFFFFF;
    border: 1px solid #e0e0e0;
    border-radius: 22px 22px 22px 5px;
    color: #303030;
}

.bubble-user {
    background: #DCF8C6;
    color: #303030;
    border-radius: 22px 22px 5px 22px;
}

.small-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: url("https://picsum.photos/101") center/cover;
    align-self: flex-end;
    margin-right: 10px;
    flex-shrink: 0;
}

/* Footer */
.footer {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 12px;
    border-top: 1px solid #eee;
    background: #f0f0f0;
}

.footer-icon {
    font-size: 24px;
    color: #25D366;
    cursor: pointer;
}

.footer-input {
    flex: 1;
}

.footer-input .stTextInput {
    margin: 0 !important;
    padding: 0 !important;
}

.footer-input .stTextInput > div {
    margin: 0 !important;
    padding: 0 !important;
}

.footer-input input {
    border-radius: 25px !important;
    border: none !important;
    padding: 10px 16px !important;
    background: #fff !important;
    font-size: 15px !important;
    box-shadow: none !important;
}

.footer-send {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: #128C7E;
    color: #fff;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 20px;
    cursor: pointer;
    flex-shrink: 0;
    border: none;
}

.footer-send:hover { background: #0e6d62; }

.footer-send button {
    width: 44px !important;
    height: 44px !important;
    border-radius: 50% !important;
    background: #128C7E !important;
    color: #fff !important;
    border: none !important;
    padding: 0 !important;
    font-size: 20px !important;
    min-width: unset !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.footer-send button:hover { background: #0e6d62 !important; }
.footer-send button p { margin: 0 !important; font-size: 20px !important; }
.footer-send button svg, .footer-send button img { display: none !important; }

/* Remove right-side space */
.stApp .main .block-container {
    max-width: 100% !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

/* Make form inline with no padding */
.stForm {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}

.stForm [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}

.stForm [data-testid="column"] {
    padding: 0 !important;
}

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer { display: none !important; }
.stApp > header { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Build chat messages HTML
def build_chat_html():
    html = '<div class="chat" id="chat-area">'
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            html += '<div class="message right-msg"><div class="bubble bubble-user">'
            html += msg["content"]
            html += '</div></div>'
        else:
            html += '<div class="message left-msg">'
            html += '<div class="small-avatar"></div>'
            html += '<div class="bubble bubble-bot">'
            html += msg["content"]
            html += '</div></div>'
    html += '</div>'
    return html

# Phone container
st.markdown('<div class="phone-wrapper">', unsafe_allow_html=True)
st.markdown('<div class="phone">', unsafe_allow_html=True)

# Header
st.markdown(f'''
<div class="header">
    <div class="header-left">
        <div class="back-icon">&#10094;</div>
        <div class="avatar"></div>
        <div class="company-name">{st.session_state.user_name}</div>
    </div>
    <div class="verify-badge">&#10003;</div>
</div>
''', unsafe_allow_html=True)

# Chat messages
st.markdown(build_chat_html(), unsafe_allow_html=True)

# Footer with input
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown('<div class="footer-icon">☰</div>', unsafe_allow_html=True)
st.markdown('<div class="footer-icon">📷</div>', unsafe_allow_html=True)
st.markdown('<div class="footer-input">', unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([7, 1], gap="small")
    with cols[0]:
        prompt = st.text_input(
            "Message",
            key="chat_input",
            label_visibility="collapsed",
            placeholder="Aa"
        )
    with cols[1]:
        submitted = st.form_submit_button("➤", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

query = None
if submitted and prompt:
    query = prompt
elif st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    initial_state = ChatState(
        messages=[{"role": "user", "content": query}],
        user_id=st.session_state.user_id,
        session_id=st.session_state.session_id,
        intent=None,
        confidence=None,
        entities={},
        context={"history": ""},
        requires_auth=False,
        is_authenticated=st.session_state.user_id != "GUEST",
        response=None,
        escalation_needed=False,
    )

    result = run_graph(initial_state)
    response = result.response or "I'm sorry, I couldn't process that."

    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.expander("🔍 Debug Info"):
        st.json({
            "intent": result.intent,
            "confidence": result.confidence,
            "entities": result.entities,
            "user_id": st.session_state.user_id,
            "session_id": st.session_state.session_id,
            "escalated": result.escalation_needed
        })

    st.rerun()
