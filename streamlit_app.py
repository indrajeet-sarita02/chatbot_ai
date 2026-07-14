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

st.title("🛍️ ShopEase AI Assistant")
st.caption("Your 24/7 ecommerce support chatbot — Orders, Products, Weather & more")

st.markdown("""
<style>
.chat-user {
    background-color: #DCF8C6;
    padding: 10px 15px;
    border-radius: 15px 15px 5px 15px;
    margin: 5px 0;
    max-width: 80%;
    margin-left: auto;
}
.chat-assistant {
    background-color: #FFFFFF;
    border: 1px solid #e0e0e0;
    padding: 10px 15px;
    border-radius: 15px 15px 15px 5px;
    margin: 5px 0;
    max-width: 80%;
    margin-right: auto;
    white-space: pre-wrap;
    font-family: monospace;
}
.chat-container {
    max-height: 500px;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 10px;
    margin-bottom: 20px;
}

.chat-input-wrapper {
    display: flex;
    gap: 8px;
    align-items: center;
}

.chat-input-wrapper .stTextInput {
    flex: 1;
}

.chat-input-wrapper .stTextInput input {
    border-radius: 25px !important;
    border: 1px solid #e0e0e0 !important;
    padding: 10px 16px !important;
    background: #f2f2f2 !important;
}

.chat-input-wrapper .stFormSubmitButton {
    flex-shrink: 0;
}

.chat-input-wrapper .stFormSubmitButton button {
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

.chat-input-wrapper .stFormSubmitButton button:hover {
    background: #1da851 !important;
    color: #fff !important;
}

.chat-input-wrapper .stFormSubmitButton button:active {
    background: #1a9a47 !important;
}

.chat-input-wrapper .stFormSubmitButton button p {
    margin: 0 !important;
    font-size: 20px !important;
}
</style>
""", unsafe_allow_html=True)

chat_html = '<div class="chat-container">'
for msg in st.session_state.messages:
    cls = "chat-user" if msg["role"] == "user" else "chat-assistant"
    chat_html += f'<div class="{cls}">{msg["content"]}</div>'
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

st.markdown('<div class="chat-input-wrapper">', unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([6, 1])
    with cols[0]:
        prompt = st.text_input(
            "Ask me anything about your orders, products, weather...",
            key="chat_input",
            label_visibility="collapsed"
        )
    with cols[1]:
        submitted = st.form_submit_button("➤", use_container_width=True)
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

st.markdown("---")
st.caption("Powered by LangChain + OpenAI • Data stored in SQLite")
