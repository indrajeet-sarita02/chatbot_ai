# AI-Powered Ecommerce Customer Support Chatbot — Skill Document

**Tech Stack:** Python, LangChain, LangGraph, SQLite, Streamlit  
**Version:** 1.0

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI (Web)                       │
│  User Input → Session State → Message History Display        │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    LangGraph Agent Graph                      │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│  │ ChatNode │→→│ Intent   │→→│  Action  │→→│ Response    │  │
│  │          │  │ Router   │  │  Executor│  │ Generator   │  │
│  └─────────┘  └──────────┘  └──────────┘  └─────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│              Agentic SQLite Query Layer                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐    │
│  │ SQLite DB│ │ SQLite   │ │ Weather  │ │ FAQ direct  │    │
│  │ (Orders, │ │ Product  │ │ API Tool │ │ SQL query   │    │
│  │ Products,│ │ Queries  │ │          │ │             │    │
│  │ Users,   │ │          │ │          │ │             │    │
│  │ FAQ)     │ │          │ │          │ │             │    │
│  └──────────┘ └──────────┘ └──────────┘ └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

Each agent writes **raw SQL** against SQLite to fulfill the customer's request. No vector store, no RAG — just direct database queries.

---

## 2. Project Structure

```
chatbot_ecommerce/
├── app.py                    # Streamlit entry point
├── graph/
│   ├── __init__.py
│   ├── state.py              # LangGraph state schema
│   ├── nodes.py              # Graph node functions
│   ├── edges.py              # Conditional edge logic
│   └── graph.py              # Graph compilation
├── agents/
│   ├── __init__.py
│   ├── intent_router.py      # LLM intent classification
│   ├── order_agent.py        # Order queries — direct SQL
│   ├── product_agent.py      # Product search/recommend — direct SQL
│   ├── account_agent.py      # Account queries — direct SQL
│   ├── shipping_agent.py     # Shipping queries — direct SQL
│   ├── payment_agent.py      # Payment queries — direct SQL
│   ├── weather_agent.py      # Weather queries — external API
│   ├── faq_agent.py          # FAQ/policy — direct SQL LIKE search
│   └── escalation_agent.py   # Human handoff
├── tools/
│   ├── __init__.py
│   ├── weather_tool.py       # OpenWeatherMap API
│   └── helpers.py            # Formatting helpers
├── db/
│   ├── __init__.py
│   ├── connection.py         # Connection manager
│   ├── schema.py             # SQLite schema definitions
│   └── seed.py               # Sample data seeder
├── prompts/
│   ├── __init__.py
│   └── intent_prompts.py     # Intent classification prompt
├── utils/
│   ├── __init__.py
│   └── config.py             # Env / config loader
├── requirements.txt
└── .env
```

---

## 3. SQLite Database Schema (`db/schema.py`)

```python
import sqlite3

def get_connection(db_path="chatbot_ecommerce.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def create_tables(conn):
    conn.executescript("""
    -- Users
    CREATE TABLE IF NOT EXISTS users (
        user_id        TEXT PRIMARY KEY,
        name           TEXT NOT NULL,
        email          TEXT UNIQUE NOT NULL,
        phone          TEXT,
        password_hash  TEXT NOT NULL,
        is_guest       INTEGER DEFAULT 0,
        preferred_lang TEXT DEFAULT 'en',
        created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Addresses
    CREATE TABLE IF NOT EXISTS addresses (
        address_id  TEXT PRIMARY KEY,
        user_id     TEXT REFERENCES users(user_id),
        label       TEXT,
        street      TEXT,
        city        TEXT,
        state       TEXT,
        pincode     TEXT,
        is_default  INTEGER DEFAULT 0
    );

    -- Categories
    CREATE TABLE IF NOT EXISTS categories (
        category_id   TEXT PRIMARY KEY,
        name          TEXT NOT NULL,
        parent_id     TEXT REFERENCES categories(category_id)
    );

    -- Products
    CREATE TABLE IF NOT EXISTS products (
        product_id    TEXT PRIMARY KEY,
        name          TEXT NOT NULL,
        description   TEXT,
        category_id   TEXT REFERENCES categories(category_id),
        price         REAL NOT NULL,
        mrp           REAL,
        stock         INTEGER DEFAULT 0,
        rating        REAL DEFAULT 0,
        review_count  INTEGER DEFAULT 0,
        brand         TEXT,
        specs         TEXT,           -- JSON
        images        TEXT,           -- JSON array
        is_active     INTEGER DEFAULT 1,
        created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Orders
    CREATE TABLE IF NOT EXISTS orders (
        order_id        TEXT PRIMARY KEY,
        user_id         TEXT REFERENCES users(user_id),
        order_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount    REAL NOT NULL,
        discount        REAL DEFAULT 0,
        final_amount    REAL NOT NULL,
        status          TEXT DEFAULT 'confirmed',
        payment_status  TEXT DEFAULT 'pending',
        payment_method  TEXT,
        shipping_charge REAL DEFAULT 0,
        delivery_address_id TEXT REFERENCES addresses(address_id),
        courier         TEXT,
        tracking_number TEXT,
        estimated_delivery DATE,
        delivered_date  DATE,
        cancellation_reason TEXT,
        return_reason   TEXT,
        refund_amount   REAL,
        refund_date     DATE
    );

    -- Order Items
    CREATE TABLE IF NOT EXISTS order_items (
        item_id     TEXT PRIMARY KEY,
        order_id    TEXT REFERENCES orders(order_id),
        product_id  TEXT REFERENCES products(product_id),
        quantity    INTEGER DEFAULT 1,
        unit_price  REAL NOT NULL,
        subtotal    REAL NOT NULL
    );

    -- Cart
    CREATE TABLE IF NOT EXISTS cart (
        cart_id    TEXT PRIMARY KEY,
        user_id    TEXT REFERENCES users(user_id),
        product_id TEXT REFERENCES products(product_id),
        quantity   INTEGER DEFAULT 1,
        added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Wishlist
    CREATE TABLE IF NOT EXISTS wishlist (
        user_id    TEXT REFERENCES users(user_id),
        product_id TEXT REFERENCES products(product_id),
        added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, product_id)
    );

    -- Reviews
    CREATE TABLE IF NOT EXISTS reviews (
        review_id   TEXT PRIMARY KEY,
        user_id     TEXT REFERENCES users(user_id),
        product_id  TEXT REFERENCES products(product_id),
        rating      INTEGER CHECK(rating BETWEEN 1 AND 5),
        comment     TEXT,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Coupons
    CREATE TABLE IF NOT EXISTS coupons (
        coupon_code  TEXT PRIMARY KEY,
        description  TEXT,
        discount_pct REAL,
        max_discount REAL,
        min_cart     REAL,
        valid_from   DATE,
        valid_to     DATE,
        usage_limit  INTEGER DEFAULT 1,
        used_count   INTEGER DEFAULT 0
    );

    -- Loyalty Points
    CREATE TABLE IF NOT EXISTS loyalty_points (
        user_id    TEXT PRIMARY KEY REFERENCES users(user_id),
        points     INTEGER DEFAULT 0,
        tier       TEXT DEFAULT 'silver'
    );

    -- Chat History
    CREATE TABLE IF NOT EXISTS chat_history (
        session_id  TEXT NOT NULL,
        role        TEXT NOT NULL,
        message     TEXT NOT NULL,
        intent      TEXT,
        confidence  REAL,
        timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- FAQ Knowledge Base (queried directly via SQL LIKE)
    CREATE TABLE IF NOT EXISTS faq (
        faq_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        question    TEXT NOT NULL,
        answer      TEXT NOT NULL,
        category    TEXT,
        lang        TEXT DEFAULT 'en',
        keywords    TEXT
    );

    -- Company Info
    CREATE TABLE IF NOT EXISTS company_info (
        key   TEXT PRIMARY KEY,
        value TEXT
    );
    """)
    conn.commit()
```

### Seed Sample Data (`db/seed.py`)

```python
import uuid
from datetime import date, timedelta
from db.connection import get_connection

def seed():
    conn = get_connection()
    create_tables(conn)

    users = [
        ("U1001", "Rajesh Kumar", "rajesh@example.com", "9876543210", "hashed_pwd_1", 0),
        ("U1002", "Priya Sharma", "priya@example.com", "9876543211", "hashed_pwd_2", 0),
        ("GUEST", "Guest User", "guest@example.com", "", "guest", 1),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO users VALUES (?,?,?,?,?,?,?,?)",
        [(u[0], u[1], u[2], u[3], u[4], u[5], "en", "2025-01-01") for u in users]
    )

    addresses = [
        ("A001", "U1001", "Home", "12 MG Road", "Mumbai", "Maharashtra", "400001", 1),
        ("A002", "U1002", "Work", "45 Bannerghatta", "Bangalore", "Karnataka", "560076", 1),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO addresses VALUES (?,?,?,?,?,?,?,?)", addresses
    )

    cats = [
        ("CAT-ELEC", "Electronics", None),
        ("CAT-PHN", "Mobile Phones", "CAT-ELEC"),
        ("CAT-LAP", "Laptops", "CAT-ELEC"),
        ("CAT-AUD", "Audio", "CAT-ELEC"),
        ("CAT-FSH", "Fashion", None),
        ("CAT-HOM", "Home & Kitchen", None),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO categories VALUES (?,?,?)", cats
    )

    products = [
        ("P100", "iPhone 15", "Latest Apple smartphone", "CAT-PHN", 79999, 89900, 50, 4.5, 120, "Apple", '{"color":"Black","storage":"128GB"}', '["img1.jpg"]', 1),
        ("P101", "Samsung Galaxy S24", "Flagship Android phone", "CAT-PHN", 74999, 84999, 30, 4.3, 85, "Samsung", '{"color":"Titanium Gray","storage":"256GB"}', '["img2.jpg"]', 1),
        ("P102", "MacBook Air M3", "Lightweight laptop M3 chip", "CAT-LAP", 114999, 129900, 20, 4.7, 200, "Apple", '{"ram":"16GB","storage":"512GB"}', '["img3.jpg"]', 1),
        ("P103", "Sony WH-1000XM5", "Noise cancelling headphones", "CAT-AUD", 29990, 34990, 100, 4.6, 300, "Sony", '{"type":"Over-ear","battery":"30hrs"}', '["img4.jpg"]', 1),
        ("P104", "Bluetooth Speaker", "Portable waterproof speaker", "CAT-AUD", 2499, 3999, 200, 4.1, 50, "Boat", '{"power":"10W","battery":"12hrs"}', '["img5.jpg"]', 1),
    ]
    conn.executemany(
        """INSERT OR IGNORE INTO products
           (product_id,name,description,category_id,price,mrp,stock,rating,review_count,brand,specs,images,is_active)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", products
    )

    today = date.today()
    orders = [
        ("ORD-1001", "U1001", "2026-07-01", 79999.0, 0, 79999.0, "shipped", "paid", "Credit Card", 0, "A001", "BlueDart", "BLD123456", str(today + timedelta(days=2)), None, None, None, None, None),
        ("ORD-1002", "U1001", "2026-06-28", 29990.0, 500, 29490.0, "delivered", "paid", "UPI", 0, "A001", "Delhivery", "DLV789012", str(today - timedelta(days=5)), str(today - timedelta(days=3)), None, None, None, None),
        ("ORD-1003", "U1002", "2026-07-02", 114999.0, 2000, 112999.0, "confirmed", "pending", "EMI", 0, "A002", None, None, str(today + timedelta(days=7)), None, None, None, None, None),
    ]
    conn.executemany(
        """INSERT OR IGNORE INTO orders
           (order_id,user_id,order_date,total_amount,discount,final_amount,status,payment_status,payment_method,shipping_charge,delivery_address_id,courier,tracking_number,estimated_delivery,delivered_date,cancellation_reason,return_reason,refund_amount,refund_date)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", orders
    )

    items = [
        ("OI-001", "ORD-1001", "P100", 1, 79999, 79999.0),
        ("OI-002", "ORD-1002", "P103", 1, 29990, 29990.0),
        ("OI-003", "ORD-1003", "P102", 1, 114999, 114999.0),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO order_items VALUES (?,?,?,?,?,?)", items
    )

    faqs = [
        ("How do I return a product?", "You can return any product within 30 days of delivery. Go to Your Orders, select the item and click Return.", "returns", "en"),
        ("What is your refund policy?", "Refunds are processed within 5-7 business days after the returned item is received at our warehouse.", "returns", "en"),
        ("How can I track my order?", "Go to Your Orders and click Track Package next to your order. You can also use the tracking number on the courier's website.", "shipping", "en"),
        ("What payment methods do you accept?", "We accept Credit/Debit Cards, UPI, Net Banking, EMI, and Wallet payments.", "payments", "en"),
        ("How do I cancel my order?", "Orders can be cancelled within 24 hours of placing. Go to Your Orders and click Cancel.", "orders", "en"),
        ("What is your delivery time?", "Standard delivery takes 3-5 business days. Express delivery is available in 1-2 business days.", "shipping", "en"),
        ("How do I contact customer support?", "Call us at 1800-123-4567 or email support@ecommerce.com. We are available 24/7.", "contact", "en"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO faq (question,answer,category,lang) VALUES (?,?,?,?)", faqs
    )

    info = [
        ("company_name", "ShopEase Ecommerce Pvt Ltd"),
        ("about_us", "ShopEase is India's leading online shopping platform offering millions of products across categories."),
        ("business_hours", "Customer Support: 24x7 | Store hours: Open 365 days"),
        ("privacy_policy", "We value your privacy. Your data is encrypted and never shared with third parties without consent."),
        ("terms", "By using our platform you agree to our terms and conditions. All sales are subject to our return policy."),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO company_info (key,value) VALUES (?,?)", info
    )

    conn.execute(
        "INSERT OR IGNORE INTO coupons VALUES ('WELCOME10','10% off for new users',10,500,999,'2025-01-01','2026-12-31',10000,0)"
    )
    conn.execute(
        "INSERT OR IGNORE INTO coupons VALUES ('FREEDEL','Free delivery on orders above ₹500',0,0,500,'2025-01-01','2026-12-31',10000,0)"
    )

    conn.commit()
    conn.close()
    print("Database seeded successfully.")
```

---

## 4. LangGraph State & Graph

### State Definition (`graph/state.py`)

```python
from typing import TypedDict, Annotated, Optional, List
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages: Annotated[List[dict], add_messages]
    user_id: Optional[str]
    session_id: str
    intent: Optional[str]
    confidence: Optional[float]
    entities: dict
    context: dict
    requires_auth: bool
    is_authenticated: bool
    response: Optional[str]
    escalation_needed: bool
```

### Graph Nodes (`graph/nodes.py`)

```python
from langchain_core.messages import HumanMessage, AIMessage
import json

def identify_user(state: ChatState) -> dict:
    user_id = state.get("user_id")
    is_authenticated = user_id is not None and user_id != "GUEST"
    return {"is_authenticated": is_authenticated}

def route_intent(state: ChatState) -> dict:
    from agents.intent_router import classify_intent
    last_msg = state["messages"][-1].content if state["messages"] else ""
    intent, confidence, entities = classify_intent(last_msg, state["context"])
    return {"intent": intent, "confidence": confidence, "entities": entities}

def execute_order_action(state: ChatState) -> dict:
    from agents.order_agent import handle_order_query
    response = handle_order_query(state["user_id"], state["entities"], state["intent"])
    return {"response": response}

def execute_product_action(state: ChatState) -> dict:
    from agents.product_agent import handle_product_query
    response = handle_product_query(state["entities"], state["intent"])
    return {"response": response}

def execute_account_action(state: ChatState) -> dict:
    from agents.account_agent import handle_account_query
    response = handle_account_query(state["user_id"], state["entities"])
    return {"response": response}

def execute_shipping_action(state: ChatState) -> dict:
    from agents.shipping_agent import handle_shipping_query
    response = handle_shipping_query(state["user_id"], state["entities"])
    return {"response": response}

def execute_payment_action(state: ChatState) -> dict:
    from agents.payment_agent import handle_payment_query
    response = handle_payment_query(state["user_id"], state["entities"])
    return {"response": response}

def execute_weather_action(state: ChatState) -> dict:
    from agents.weather_agent import handle_weather_query
    response = handle_weather_query(state["entities"])
    return {"response": response}

def execute_faq_action(state: ChatState) -> dict:
    from agents.faq_agent import handle_faq_query
    response = handle_faq_query(state["entities"], state["intent"])
    return {"response": response}

def generate_response(state: ChatState) -> dict:
    from db.connection import get_connection
    response_text = state.get("response", "I'm sorry, I couldn't process your request.")
    ai_msg = AIMessage(content=response_text)
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_history (session_id, role, message, intent) VALUES (?,?,?,?)",
        (state["session_id"], "assistant", response_text, state.get("intent"))
    )
    conn.commit()
    conn.close()
    new_messages = state["messages"] + [ai_msg]
    return {"messages": new_messages, "response": response_text}

def escalate_to_human(state: ChatState) -> dict:
    response_text = (
        "I'm sorry, I couldn't confidently answer your query. "
        "Let me connect you with a human support agent. "
        "Please expect a call or email shortly."
    )
    ai_msg = AIMessage(content=response_text)
    new_messages = state["messages"] + [ai_msg]
    return {"messages": new_messages, "response": response_text, "escalation_needed": True}
```

### Conditional Edges (`graph/edges.py`)

```python
from graph.state import ChatState

def should_escalate(state: ChatState) -> str:
    confidence = state.get("confidence", 0.0)
    if confidence < 0.4:
        return "escalate"
    return state.get("intent", "faq")

def requires_auth_check(state: ChatState) -> str:
    auth_intents = {"order_status", "order_cancel", "order_tracking",
                    "refund_status", "cart", "wishlist", "account"}
    if state.get("intent") in auth_intents and not state.get("is_authenticated"):
        return "prompt_login"
    return "proceed"
```

### Graph Compilation (`graph/graph.py`)

```python
from langgraph.graph import StateGraph, END
from graph.state import ChatState
from graph.nodes import (
    identify_user, route_intent,
    execute_order_action, execute_product_action,
    execute_account_action, execute_shipping_action,
    execute_payment_action, execute_weather_action,
    execute_faq_action, generate_response, escalate_to_human
)
from graph.edges import should_escalate, requires_auth_check

def build_graph() -> StateGraph:
    workflow = StateGraph(ChatState)

    workflow.add_node("identify_user", identify_user)
    workflow.add_node("route_intent", route_intent)
    workflow.add_node("order", execute_order_action)
    workflow.add_node("product", execute_product_action)
    workflow.add_node("account", execute_account_action)
    workflow.add_node("shipping", execute_shipping_action)
    workflow.add_node("payment", execute_payment_action)
    workflow.add_node("weather", execute_weather_action)
    workflow.add_node("faq", execute_faq_action)
    workflow.add_node("generate", generate_response)
    workflow.add_node("escalate", escalate_to_human)

    workflow.set_entry_point("identify_user")
    workflow.add_edge("identify_user", "route_intent")

    workflow.add_conditional_edges(
        "route_intent",
        should_escalate,
        {
            "order": "order",
            "product": "product",
            "account": "account",
            "shipping": "shipping",
            "payment": "payment",
            "weather": "weather",
            "faq": "faq",
            "escalate": "escalate",
        }
    )

    action_nodes = ["order", "product", "account", "shipping", "payment",
                    "weather", "faq", "escalate"]
    for node in action_nodes:
        workflow.add_edge(node, "generate")

    workflow.add_edge("generate", END)
    return workflow.compile()

chat_graph = build_graph()
```

---

## 5. Intent Router (`agents/intent_router.py`)

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from prompts.intent_prompts import INTENT_CLASSIFICATION_PROMPT
import json, re

INTENTS = [
    "order_status", "order_tracking", "order_cancel",
    "refund_status", "return_status", "exchange_status",
    "product_search", "product_recommend", "product_compare",
    "product_review", "product_availability",
    "cart_info", "wishlist_info",
    "shipping_charges", "shipping_tracking", "delivery_date",
    "payment_status", "payment_methods", "emi_options",
    "coupons", "offers", "loyalty",
    "weather_current", "weather_forecast",
    "faq_general", "company_info", "contact_info",
    "login_help", "password_reset", "address_manage",
    "greeting", "farewell", "thanks", "unknown"
]

def classify_intent(user_message: str, context: dict) -> tuple:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_template(INTENT_CLASSIFICATION_PROMPT)
    chain = prompt | llm
    result = chain.invoke({
        "message": user_message,
        "conversation_history": context.get("history", ""),
        "intents": ", ".join(INTENTS)
    })
    try:
        parsed = json.loads(result.content)
        intent = parsed.get("intent", "unknown")
        confidence = float(parsed.get("confidence", 0.0))
        entities = parsed.get("entities", {})
    except (json.JSONDecodeError, ValueError):
        intent = _fallback_intent(user_message)
        confidence = 0.5
        entities = _extract_entities_fallback(user_message, intent)
    return intent, confidence, entities

def _fallback_intent(msg: str) -> str:
    msg_lower = msg.lower()
    if any(w in msg_lower for w in ["order", "track", "delivery", "where is", "shipment"]):
        return "order_status"
    if any(w in msg_lower for w in ["cancel"]):
        return "order_cancel"
    if any(w in msg_lower for w in ["refund", "money back"]):
        return "refund_status"
    if any(w in msg_lower for w in ["return"]):
        return "return_status"
    if any(w in msg_lower for w in ["weather", "temperature", "rain", "humid", "wind"]):
        return "weather_current"
    if any(w in msg_lower for w in ["recommend", "suggest", "best"]):
        return "product_recommend"
    if any(w in msg_lower for w in ["search", "show", "find", "bluetooth", "under ₹", "price"]):
        return "product_search"
    if any(w in msg_lower for w in ["compare", "vs", "versus", "difference"]):
        return "product_compare"
    if any(w in msg_lower for w in ["cart", "bag"]):
        return "cart_info"
    if any(w in msg_lower for w in ["wishlist", "saved"]):
        return "wishlist_info"
    if any(w in msg_lower for w in ["shipping charge", "delivery charge", "shipping cost"]):
        return "shipping_charges"
    if any(w in msg_lower for w in ["payment", "pay", "emi"]):
        return "payment_status"
    if any(w in msg_lower for w in ["coupon", "offer", "discount", "sale"]):
        return "offers"
    if any(w in msg_lower for w in ["hi", "hello", "hey"]):
        return "greeting"
    if any(w in msg_lower for w in ["bye", "goodbye"]):
        return "farewell"
    return "faq_general"

def _extract_entities_fallback(msg: str, intent: str) -> dict:
    entities = {}
    order_match = re.search(r'(ORD[-]?\d+)', msg, re.IGNORECASE)
    if order_match:
        entities["order_id"] = order_match.group(1)
    product_match = re.search(r'(iPhone|Samsung|MacBook|Sony|Boat|headphone|speaker|laptop)',
                              msg, re.IGNORECASE)
    if product_match:
        entities["product_name"] = product_match.group(1)
    price_match = re.search(r'(?:under|below|less than|upto|<=?)\s*₹?\s*(\d[\d,]*)', msg, re.IGNORECASE)
    if price_match:
        entities["max_price"] = float(price_match.group(1).replace(",", ""))
    city_match = re.search(r'weather\s+(?:in|at|for)\s+([A-Za-z\s]+)', msg, re.IGNORECASE)
    if city_match:
        entities["city"] = city_match.group(1).strip()
    track_match = re.search(r'tracking\s*(?:number|id|no)?[:\s]*([A-Za-z0-9]+)', msg, re.IGNORECASE)
    if track_match:
        entities["tracking_number"] = track_match.group(1)
    return entities
```

### Intent Prompt (`prompts/intent_prompts.py`)

```python
INTENT_CLASSIFICATION_PROMPT = """You are an intent classifier for an ecommerce chatbot.
Classify the user's message into exactly one of these intents:
{intents}

Conversation history:
{conversation_history}

User message: {message}

Respond ONLY with a JSON object:
{{
  "intent": "intent_name",
  "confidence": 0.0-1.0,
  "entities": {{
    "order_id": "extracted if present",
    "product_name": "extracted if present",
    "city": "extracted if present",
    "max_price": 0.0,
    "min_price": 0.0,
    "category": "extracted if present",
    "tracking_number": "extracted if present"
  }}
}}"""
```

---

## 6. Agent Implementations — All Use Direct SQL Against SQLite

### Order Agent (`agents/order_agent.py`)

```python
from db.connection import get_connection
from datetime import datetime

def handle_order_query(user_id: str, entities: dict, intent: str) -> str:
    conn = get_connection()
    order_id = entities.get("order_id")

    if intent == "order_status":
        if order_id:
            row = conn.execute(
                "SELECT * FROM orders WHERE order_id=? AND user_id=?", (order_id, user_id)
            ).fetchone()
            if not row:
                return "I couldn't find that order. Please check your order ID."
            return _format_order(row)
        rows = conn.execute(
            "SELECT * FROM orders WHERE user_id=? ORDER BY order_date DESC", (user_id,)
        ).fetchall()
        if not rows:
            return "You have no orders yet."
        return "Here are your orders:\n\n" + "\n---\n".join(_format_order(r) for r in rows)

    elif intent == "order_tracking":
        if not order_id:
            return "Please provide your order ID to track."
        row = conn.execute(
            "SELECT * FROM orders WHERE order_id=? AND user_id=?", (order_id, user_id)
        ).fetchone()
        if not row:
            return "Order not found."
        return (
            f"📍 Tracking for Order #{row['order_id']}\n"
            f"Courier: {row['courier'] or 'N/A'}\n"
            f"Tracking No: {row['tracking_number'] or 'N/A'}\n"
            f"Status: {row['status'].title()}\n"
            f"Estimated Delivery: {row['estimated_delivery'] or 'N/A'}"
        )

    elif intent == "order_cancel":
        if not order_id:
            return "Please provide the order ID you want to cancel."
        row = conn.execute(
            "SELECT * FROM orders WHERE order_id=? AND user_id=?", (order_id, user_id)
        ).fetchone()
        if not row:
            return "Order not found."
        if row["status"] in ("shipped", "delivered"):
            return f"Order {order_id} has already been {row['status']} and cannot be cancelled."
        if row["status"] == "cancelled":
            return f"Order {order_id} is already cancelled."
        conn.execute(
            "UPDATE orders SET status='cancelled', cancellation_reason=? WHERE order_id=?",
            (entities.get("reason", "Cancelled by user"), order_id)
        )
        conn.commit()
        return f"Order {order_id} has been successfully cancelled. Refund will be processed within 5-7 business days."

    elif intent == "refund_status":
        if not order_id:
            return "Please provide your order ID to check refund status."
        row = conn.execute(
            "SELECT * FROM orders WHERE order_id=? AND user_id=?", (order_id, user_id)
        ).fetchone()
        if not row:
            return "Order not found."
        if row["refund_amount"]:
            return (
                f"Refund for Order {order_id}:\n"
                f"Amount: ₹{row['refund_amount']:.2f}\n"
                f"Status: {row['payment_status']}\n"
                f"Date: {row['refund_date'] or 'Processing'}\n"
                f"Method: {row['payment_method']}"
            )
        return f"No refund has been initiated for Order {order_id}."

    conn.close()
    return "I can help with your order. Please provide more details."

def _format_order(row) -> str:
    return (
        f"📦 Order #{row['order_id']}\n"
        f"Status: {row['status'].title()}\n"
        f"Payment: {row['payment_status'].title()}\n"
        f"Amount: ₹{row['final_amount']:.2f}\n"
        f"Delivery: {row['estimated_delivery'] or 'N/A'}\n"
        f"Courier: {row['courier'] or 'Yet to be assigned'}\n"
        f"Tracking: {row['tracking_number'] or 'N/A'}"
    )
```

### Product Agent (`agents/product_agent.py`)

```python
from db.connection import get_connection
import json

def handle_product_query(entities: dict, intent: str) -> str:
    conn = get_connection()
    name = entities.get("product_name", "")
    max_price = entities.get("max_price", 0)
    min_price = entities.get("min_price", 0)
    category = entities.get("category", "")

    if intent == "product_search":
        query = "SELECT * FROM products WHERE is_active=1 AND stock>0"
        params = []
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if max_price > 0:
            query += " AND price <= ?"
            params.append(max_price)
        if min_price > 0:
            query += " AND price >= ?"
            params.append(min_price)
        if category:
            query += " AND (category_id LIKE ? OR name LIKE ?)"
            params += [f"%{category}%", f"%{category}%"]
        query += " ORDER BY rating DESC LIMIT 10"
        results = conn.execute(query, params).fetchall()
        if not results:
            return "I couldn't find any products matching your criteria."
        lines = ["Here are matching products:\n"]
        for p in results[:5]:
            stock = "In Stock" if p["stock"] > 0 else "Out of Stock"
            lines.append(f"• {p['name']} — ₹{p['price']:.0f} (MRP ₹{p['mrp']:.0f}) ⭐{p['rating']} | {stock}")
        if len(results) > 5:
            lines.append(f"\n...and {len(results) - 5} more.")
        return "\n".join(lines)

    elif intent == "product_recommend":
        results = conn.execute(
            "SELECT * FROM products WHERE is_active=1 AND stock>0 ORDER BY rating DESC, review_count DESC LIMIT 5"
        ).fetchall()
        lines = ["Top recommendations for you:\n"]
        for p in results:
            lines.append(f"• {p['name']} — ₹{p['price']:.0f} ⭐{p['rating']} ({p['review_count']} reviews)")
        return "\n".join(lines)

    elif intent == "product_compare":
        if not entities.get("compare_products"):
            return "Please tell me which products to compare (e.g., 'Compare iPhone and Samsung')."
        products = entities["compare_products"]
        lines = [f"📊 Comparison: {' vs '.join(p.capitalize() for p in products)}\n"]
        for pname in products:
            p = conn.execute(
                "SELECT * FROM products WHERE name LIKE ? LIMIT 1", (f"%{pname}%",)
            ).fetchone()
            if p:
                specs = json.loads(p["specs"]) if isinstance(p["specs"], str) else (p["specs"] or {})
                lines.append(
                    f"• {p['name']}: ₹{p['price']:.0f} | ⭐{p['rating']} | "
                    f"Stock: {p['stock']} | {', '.join(f'{k}: {v}' for k, v in specs.items())}"
                )
            else:
                lines.append(f"• {pname}: Not found")
        return "\n".join(lines)

    elif intent == "product_availability":
        p = conn.execute(
            "SELECT name, stock FROM products WHERE name LIKE ?", (f"%{name}%",)
        ).fetchone()
        if not p:
            return f"I couldn't find a product matching '{name}'."
        if p["stock"] > 0:
            return f"✅ {p['name']} is in stock! Available quantity: {p['stock']} units."
        return f"❌ {p['name']} is currently out of stock."

    conn.close()
    return "I can help you find products. What are you looking for?"
```

### Account Agent (`agents/account_agent.py`)

```python
from db.connection import get_connection

def handle_account_query(user_id: str, entities: dict) -> str:
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    if not user:
        return "Please log in to access your account information."

    intent = entities.get("account_intent", "")

    if "address" in intent:
        addrs = conn.execute(
            "SELECT * FROM addresses WHERE user_id=?", (user_id,)
        ).fetchall()
        if not addrs:
            return "You have no saved addresses."
        lines = ["Your saved addresses:\n"]
        for a in addrs:
            d = " (Default)" if a["is_default"] else ""
            lines.append(f"• [{a['label']}]{d} {a['street']}, {a['city']}, {a['state']} - {a['pincode']}")
        return "\n".join(lines)

    elif "profile" in intent:
        return (
            f"👤 Profile for {user['name']}\n"
            f"Email: {user['email']}\n"
            f"Phone: {user['phone']}\n"
            f"Language: {user['preferred_lang']}"
        )

    elif "wishlist" in intent or entities.get("intent") == "wishlist_info":
        items = conn.execute(
            """SELECT p.name, p.price, p.rating, p.stock
               FROM wishlist w JOIN products p ON w.product_id = p.product_id
               WHERE w.user_id=?""", (user_id,)
        ).fetchall()
        if not items:
            return "Your wishlist is empty."
        lines = ["❤️ Your Wishlist:\n"]
        for it in items:
            lines.append(f"• {it['name']} — ₹{it['price']:.0f} ⭐{it['rating']} {'In Stock' if it['stock'] > 0 else 'Out of Stock'}")
        return "\n".join(lines)

    conn.close()
    return "I can help with your account. What would you like to know?"
```

### FAQ Agent (`agents/faq_agent.py`) — Direct SQL LIKE Queries

```python
from db.connection import get_connection

def handle_faq_query(entities: dict, intent: str) -> str:
    conn = get_connection()

    # Company info / contact — direct SQL lookups
    if intent in ("company_info", "contact_info"):
        if "contact" in entities.get("query", "").lower() or intent == "contact_info":
            hours = conn.execute(
                "SELECT value FROM company_info WHERE key='business_hours'"
            ).fetchone()
            return (
                "📞 Contact Us\n"
                "Phone: 1800-123-4567\n"
                "Email: support@ecommerce.com\n"
                f"{hours['value'] if hours else 'Available 24/7'}"
            )
        about = conn.execute(
            "SELECT value FROM company_info WHERE key='about_us'"
        ).fetchone()
        return about["value"] if about else "Welcome to our ecommerce platform!"

    # FAQ search using SQL LIKE on question + keywords
    query = entities.get("query", "")
    if not query:
        query = entities.get("original_message", "")

    # Break the query into keywords and search FAQ table
    keywords = [w for w in query.lower().split() if len(w) > 2]
    if keywords:
        like_clauses = " OR ".join(["question LIKE ?" for _ in keywords])
        params = [f"%{k}%" for k in keywords]
        row = conn.execute(
            f"SELECT answer FROM faq WHERE {like_clauses} LIMIT 1", params
        ).fetchone()
        if row:
            conn.close()
            return row["answer"]

    # Fallback: search by category keywords
    category_map = {
        "return": ("returns", "How do I return a product?"),
        "refund": ("returns", "What is your refund policy?"),
        "track": ("shipping", "How can I track my order?"),
        "payment": ("payments", "What payment methods do you accept?"),
        "cancel": ("orders", "How do I cancel my order?"),
        "delivery": ("shipping", "What is your delivery time?"),
        "contact": ("contact", "How do I contact customer support?"),
    }
    for word, (cat, fallback_q) in category_map.items():
        if word in query.lower():
            row = conn.execute(
                "SELECT answer FROM faq WHERE category=? LIMIT 1", (cat,)
            ).fetchone()
            if row:
                conn.close()
                return row["answer"]

    conn.close()
    return "I don't have a specific answer for that. Would you like to speak with a human agent?"
```

### Weather Agent (`agents/weather_agent.py`)

```python
from tools.weather_tool import get_current_weather, get_weather_forecast

def handle_weather_query(entities: dict) -> str:
    city = entities.get("city", "Mumbai")
    intent_type = entities.get("weather_intent", "current")

    if intent_type == "forecast":
        data = get_weather_forecast(city)
        if "error" in data:
            return f"Could not fetch forecast for {city}: {data['error']}"
        lines = [f"🌤️ Weather Forecast for {city}:\n"]
        for day in data.get("forecast", [])[:3]:
            lines.append(
                f"• {day['date']}: {day['condition']}, "
                f"{day['temp_min']}°C - {day['temp_max']}°C, "
                f"Rain: {day['rain_chance']}%"
            )
        return "\n".join(lines)

    data = get_current_weather(city)
    if "error" in data:
        return f"Could not fetch weather for {city}: {data['error']}"
    return (
        f"🌤️ Current Weather in {city}\n"
        f"Temperature: {data['temp']}°C (Feels like {data['feels_like']}°C)\n"
        f"Condition: {data['condition']}\n"
        f"Humidity: {data['humidity']}%\n"
        f"Wind Speed: {data['wind_speed']} km/h\n"
        f"Rain Chance: {data.get('rain_chance', 'N/A')}%"
    )
```

---

## 7. Tools Layer

### Weather Tool (`tools/weather_tool.py`)

```python
import os
import requests
from utils.config import WEATHER_API_KEY

BASE_URL = "https://api.openweathermap.org/data/2.5"

def get_current_weather(city: str) -> dict:
    try:
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
        resp = requests.get(f"{BASE_URL}/weather", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "condition": data["weather"][0]["description"].title(),
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"] * 3.6,
            "rain_chance": data.get("rain", {}).get("1h", 0),
            "city": data["name"]
        }
    except Exception as e:
        return {"error": str(e)}

def get_weather_forecast(city: str) -> dict:
    try:
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric", "cnt": 3}
        resp = requests.get(f"{BASE_URL}/forecast", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        forecast = []
        seen_dates = set()
        for item in data["list"]:
            date_str = item["dt_txt"].split(" ")[0]
            if date_str not in seen_dates:
                seen_dates.add(date_str)
                forecast.append({
                    "date": date_str,
                    "temp_min": item["main"]["temp_min"],
                    "temp_max": item["main"]["temp_max"],
                    "condition": item["weather"][0]["description"].title(),
                    "rain_chance": item.get("pop", 0) * 100,
                    "humidity": item["main"]["humidity"]
                })
        return {"forecast": forecast, "city": data["city"]["name"]}
    except Exception as e:
        return {"error": str(e)}
```

---

## 8. Streamlit UI (`app.py`)

```python
import streamlit as st
import uuid
from graph.graph import chat_graph
from graph.state import ChatState
from db.connection import get_connection
from db.schema import create_tables
from db.seed import seed

st.set_page_config(page_title="ShopEase AI Assistant", page_icon="🛍️", layout="wide")

# Initialize DB
conn = get_connection()
create_tables(conn)
seed()
conn.close()

# Session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = "GUEST"
if "user_name" not in st.session_state:
    st.session_state.user_name = "Guest"

# Sidebar
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
        "What's in my cart?",
        "Track my shipment",
        "Has my refund been processed?"
    ]
    for q in sample_queries:
        if st.button(q, use_container_width=True, type="tertiary"):
            st.session_state.messages.append({"role": "user", "content": q})

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.rerun()

# Main chat UI
st.title("🛍️ ShopEase AI Assistant")
st.caption("Your 24/7 ecommerce support chatbot — Orders, Products, Weather & more")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me anything about your orders, products, weather..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            initial_state: ChatState = {
                "messages": [{"role": "user", "content": prompt}],
                "user_id": st.session_state.user_id,
                "session_id": st.session_state.session_id,
                "intent": None,
                "confidence": None,
                "entities": {},
                "context": {"history": ""},
                "requires_auth": False,
                "is_authenticated": st.session_state.user_id != "GUEST",
                "response": None,
                "escalation_needed": False,
            }

            result = chat_graph.invoke(initial_state)
            response = result.get("response", "I'm sorry, I couldn't process that.")
            st.markdown(response)

            with st.expander("🔍 Debug Info", expanded=False):
                st.json({
                    "intent": result.get("intent"),
                    "confidence": result.get("confidence"),
                    "entities": result.get("entities"),
                    "user_id": st.session_state.user_id,
                    "session_id": st.session_state.session_id,
                    "escalated": result.get("escalation_needed", False)
                })

    st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("---")
st.caption("Powered by LangGraph + OpenAI • Data stored in SQLite")
```

---

## 9. Configuration & Environment

### `.env`

```
OPENAI_API_KEY=your-openai-api-key
WEATHER_API_KEY=your-openweathermap-api-key
DATABASE_PATH=chatbot_ecommerce.db
```

### `utils/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH", "chatbot_ecommerce.db")
```

### `requirements.txt`

```
streamlit==1.38.0
langchain==0.3.0
langchain-core==0.3.0
langchain-openai==0.2.0
langchain-community==0.3.0
langgraph==0.2.0
openai==1.50.0
requests==2.32.0
python-dotenv==1.0.1
pydantic==2.9.0
```

---

## 10. Running the Application

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Run the app (SQLite DB + seed data created automatically on first run)
streamlit run app.py
```

---

## 11. LangGraph Flow Diagram

```
[User Input]
     │
     ▼
┌─────────────┐
│ IdentifyUser │ ← checks session / user_id
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ RouteIntent  │ ← LLM classifies intent
└──────┬──────┘
       │
       ├───────  confidence < 0.4  ────→ [Escalate to Human]
       │
       ▼  (based on intent)
┌──────┴──────┐
│             │
│  ┌──────────┼──────────┐
│  ▼          ▼          ▼
│ Order   Product    Weather ...  [one of 8 action nodes]
│  │          │          │
│  │   Each agent writes raw SQL against SQLite   │
│  │   (or calls Weather API)                     │
│  └──────────┼──────────┘
│             ▼
│    ┌──────────────┐
│    │ GenerateResp  │ ← wraps response as AIMessage, saves to chat_history
│    └──────┬───────┘
│           ▼
│       [Response to User]
```

---

## 12. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **No RAG / Vector Store** | All data lives in SQLite; agents query it directly with SQL `LIKE`, `WHERE`, `ORDER BY` — no embeddings or vector search needed |
| **LangGraph over LangChain Agent** | Explicit graph-based flow gives better control over routing, error handling, and debugging |
| **SQLite for data** | Zero setup, portable, single-file; sufficient for MVP and moderate traffic |
| **Each agent writes its own SQL** | Keeps logic self-contained; no shared DAO layer to maintain |
| **LLM-based intent routing** | More flexible than regex-only; handles variations like "Where's my stuff?" → `order_status` |
| **Confidence threshold (0.4)** | Catches most intents; low-confidence falls through to human escalation |
| **Streamlit session state** | Maintains conversation context without a dedicated state server |

---

## 13. Agentic Flow — How Each Query Is Resolved

```
User: "Where is my order?"

  1. route_intent → LLM returns: {"intent": "order_status", "confidence": 0.95, "entities": {}}
  2. execute_order_action → writes SQL:
       SELECT * FROM orders WHERE user_id='U1001' ORDER BY order_date DESC
  3. Formats result → "📦 Order #ORD-1001\nStatus: Shipped\n..."
  4. generate_response → persists to chat_history, returns to UI


User: "What is your return policy?"

  1. route_intent → LLM returns: {"intent": "faq_general", ...}
  2. execute_faq_action → writes SQL:
       SELECT answer FROM faq WHERE question LIKE '%return%' OR question LIKE '%policy%'
  3. Returns matched FAQ answer


User: "What's the weather in Delhi?"

  1. route_intent → {"intent": "weather_current", "entities": {"city": "Delhi"}}
  2. execute_weather_action → calls OpenWeatherMap API
  3. Formats temperature/humidity/wind → returns to user
```

---

## 14. Extending the Skill

| Change | What to Modify |
|--------|---------------|
| Add a new agent (e.g., `loyalty_agent`) | Create `agents/loyalty_agent.py`, add node in `graph/nodes.py` + edge in `graph/graph.py`, add intent in `intent_router.py` |
| Add multi-language FAQ | Add `lang` column filter in `agents/faq_agent.py` SQL queries |
| Switch to PostgreSQL | Replace `db/connection.py` with `psycopg2`; SQL queries remain the same |
| Add cart calculation | Write SQL aggregation in `agents/product_agent.py`: `SELECT SUM(price * quantity) FROM cart JOIN products ...` |
| Add notifications | Add a background thread that polls `orders` table and sends email/SMS |

---

## 15. Mapping BRD → Implementation

| BRD Ref | Requirement | Implementation |
|---------|-------------|---------------|
| FR-001 | User Authentication | `app.py` sidebar user selection, `graph/nodes.py:identify_user` |
| FR-002 | Order Status | `agents/order_agent.py` — `SELECT * FROM orders WHERE user_id=?` |
| FR-003 | Order Tracking | `agents/order_agent.py` — `SELECT courier, tracking_number, status FROM orders` |
| FR-004 | Order Cancellation | `agents/order_agent.py` — `UPDATE orders SET status='cancelled'` |
| FR-005 | Refund Information | `agents/order_agent.py` — `SELECT refund_amount, refund_date FROM orders` |
| FR-006 | Product Search | `agents/product_agent.py` — `SELECT * FROM products WHERE name LIKE ? AND price <= ?` |
| FR-007 | Product Recommendation | `agents/product_agent.py` — `ORDER BY rating DESC, review_count DESC LIMIT 5` |
| FR-008 | Product Comparison | `agents/product_agent.py` — multiple `SELECT` queries by product name |
| FR-009 | Product Availability | `agents/product_agent.py` — `SELECT name, stock FROM products WHERE name LIKE ?` |
| FR-010 | Cart Assistance | `agents/product_agent.py` — `SELECT SUM(price*qty) FROM cart JOIN products` |
| FR-011 | Wishlist | `agents/account_agent.py` — `SELECT ... FROM wishlist JOIN products` |
| FR-012 | Shipping Information | `agents/shipping_agent.py` — `SELECT courier, tracking, estimated_delivery FROM orders` |
| FR-013 | FAQs | `agents/faq_agent.py` — `SELECT answer FROM faq WHERE question LIKE ?` |
| FR-014 | Weather | `agents/weather_agent.py` + `tools/weather_tool.py` — OpenWeatherMap API |
| FR-015 | Human Escalation | `graph/edges.py:should_escalate` — confidence < 0.4 routes to `escalate` node |
| FR-016 | Conversation Memory | LangGraph `add_messages` reducer + `st.session_state.messages` |
| FR-017 | Multi-language | Extend `faq_agent.py` with language parameter in SQL query |
| FR-018 | Notifications | Out of scope for MVP |
