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

/* Chat layout */
.chat-wrapper {
    max-width: 700px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    height: 90vh;
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,.08);
}

.chat-header {
    padding: 16px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #075E54;
    color: #fff;
}

.chat-header h2 {
    font-size: 18px;
    font-weight: 600;
}

.chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 10px 20px;
    background: #f5f0eb;
}

.message {
    display: flex;
    margin-bottom: 16px;
}

.left-msg { justify-content: flex-start; }
.right-msg { justify-content: flex-end; }

.bubble {
    max-width: 75%;
    padding: 12px 16px;
    border-radius: 16px;
    font-size: 15px;
    line-height: 1.5;
    word-wrap: break-word;
}

.bot-bubble {
    background: #fff;
    color: #303030;
    border-radius: 16px 16px 16px 4px;
    box-shadow: 0 1px 2px rgba(0,0,0,.08);
}

.user-bubble {
    background: #DCF8C6;
    color: #303030;
    border-radius: 16px 16px 4px 16px;
}

.chat-footer {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-top: 1px solid #e0e0e0;
    background: #f0f0f0;
}

.chat-footer .stForm {
    flex: 1;
}

.chat-footer .stTextInput {
    margin: 0 !important;
    padding: 0 !important;
}

.chat-footer input {
    border-radius: 24px !important;
    border: none !important;
    padding: 12px 18px !important;
    font-size: 15px !important;
    background: #fff !important;
    outline: none !important;
    box-shadow: none !important;
}

.send-btn-wrap button {
    width: 44px !important;
    height: 44px !important;
    border-radius: 50% !important;
    background: #25D366 !important;
    color: #fff !important;
    border: none !important;
    padding: 0 !important;
    font-size: 20px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-width: unset !important;
}

.send-btn-wrap button:hover { background: #1da851 !important; }

/* Remove default Streamlit spacing */
.stApp .main .block-container {
    max-width: 100% !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

.stForm { border: none !important; padding: 0 !important; background: transparent !important; }
.stForm [data-testid="stForm"] { border: none !important; padding: 0 !important; background: transparent !important; }
.stForm [data-testid="column"] { padding: 0 !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
.stApp > header { display: none !important; }
.stAppDeployButton { display: none !important; }
section[data-testid="stSidebar"] + section { padding-top: 0 !important; }
.stMainBlockContainer { padding-top: 0 !important; }
.appview-container .main .block-container { padding-top: 0 !important; padding-bottom: 0 !important; }
header[data-testid="stHeader"] { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Build chat messages HTML
def build_chat_html():
    html = '<div class="chat-area" id="chat-area">'
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            html += '<div class="message right-msg"><div class="bubble user-bubble">' + msg["content"] + '</div></div>'
        else:
            html += '<div class="message left-msg"><div class="bubble bot-bubble">' + msg["content"] + '</div></div>'
    html += '</div>'
    return html

# Main chat container
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

# Header
st.markdown('<div class="chat-header"><h2>🛍️ ShopEase Assistant</h2><span>✓</span></div>', unsafe_allow_html=True)

# Chat messages
st.markdown(build_chat_html(), unsafe_allow_html=True)

# Footer
st.markdown('<div class="chat-footer">', unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([7, 1], gap="small")
    with cols[0]:
        prompt = st.text_input(
            "Message",
            key="chat_input",
            label_visibility="collapsed",
            placeholder="Type a message..."
        )
    with cols[1]:
        st.markdown('<div class="send-btn-wrap">', unsafe_allow_html=True)
        submitted = st.form_submit_button("➤", use_container_width=True)
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

    st.rerun()
