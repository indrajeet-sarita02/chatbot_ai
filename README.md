# 🛍️ ShopEase AI Assistant

AI-powered ecommerce customer support chatbot built with **LangChain**, **LangGraph**, **Streamlit**, and **SQLite**.

## Features

- **Order Management** — status, tracking, cancellation, refunds
- **Product Search & Recommendations** — filter by name, price, category; compare products
- **Account Queries** — profile, addresses, wishlist
- **FAQ & Company Info** — policy lookup via SQL `LIKE` search
- **Weather** — current conditions & 3-day forecast (OpenWeatherMap)
- **Intent Routing** — LLM classifies user intent; falls back to regex + human escalation
- **No RAG / Vector Store** — agents write raw SQL directly against SQLite

## Architecture

```
User Input → identify_user → route_intent (LLM) → action node → generate_response → output
                                                     │
                                          (order, product, account,
                                           weather, faq, escalate)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Agent Orchestration | LangGraph (custom sequential graph) |
| Intent Classification | OpenAI GPT-4o-mini |
| Database | SQLite (single file) |
| External API | OpenWeatherMap |

## Project Structure

```
├── app.py                  # Streamlit entry point
├── graph/                  # LangGraph: state, nodes, edges, graph
├── agents/                 # Intent router + domain agents (order, product, account, weather, faq)
├── tools/                  # External API tools (weather)
├── db/                     # SQLite connection, schema, seed data
├── prompts/                # LLM intent classification prompts
├── utils/                  # Config loader
├── requirements.txt
└── .env                    # API keys
```

## Getting Started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and WEATHER_API_KEY

# 3. Run the app
streamlit run app.py
```

The SQLite database and seed data are created automatically on first run.

## Quick Demo Queries

- *"Where is my order?"*
- *"Show me Bluetooth headphones under ₹3000"*
- *"What is today's weather in Delhi?"*
- *"Recommend me a laptop"*
- *"Cancel my order ORD-1001"*
- *"What is your return policy?"*
- *"Compare iPhone and Samsung"*

## Database

SQLite with tables: `users`, `addresses`, `categories`, `products`, `orders`, `order_items`, `cart`, `wishlist`, `reviews`, `coupons`, `loyalty_points`, `chat_history`, `faq`, `company_info`.

Seeded with 8 users, 25 products, 20 orders, 12 FAQ entries (incl. Hindi), 7 coupons, and loyalty points.
