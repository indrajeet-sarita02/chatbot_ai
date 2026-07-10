from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from utils.config import OPENAI_API_KEY
import json, re

INTENTS = [
    "order_status", "order_tracking", "order_cancel",
    "refund_status", "return_status",
    "product_search", "product_recommend", "product_compare",
    "product_review", "product_availability",
    "cart_info", "wishlist_info",
    "shipping_charges", "delivery_date",
    "payment_status", "payment_methods", "emi_options",
    "coupons", "offers", "loyalty",
    "weather_current", "weather_forecast",
    "faq_general", "company_info", "contact_info",
    "login_help", "password_reset", "address_manage",
    "greeting", "farewell", "thanks", "unknown"
]

INTENT_PROMPT_TEMPLATE = """You are an intent classifier for an ecommerce chatbot.
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
    "tracking_number": "extracted if present",
    "compare_products": ["list", "of", "product", "names", "if comparing"]
  }}
}}"""

def classify_intent(user_message, context):
    try:
        llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
        prompt = PromptTemplate(
            template=INTENT_PROMPT_TEMPLATE,
            input_variables=["message", "conversation_history", "intents"]
        )
        result = llm.invoke(prompt.format(
            message=user_message,
            conversation_history=context.get("history", ""),
            intents=", ".join(INTENTS)
        ))
        parsed = json.loads(result.content.strip())
        intent = parsed.get("intent", "unknown")
        confidence = float(parsed.get("confidence", 0.0))
        entities = parsed.get("entities", {})
    except Exception:
        intent = _fallback_intent(user_message)
        confidence = 0.5
        entities = _extract_entities_fallback(user_message, intent)
    return intent, confidence, entities

def _fallback_intent(msg):
    msg_lower = msg.lower()

    if re.search(r'\b(hi|hello|hey)\b', msg_lower) or any(w in msg_lower for w in ["good morning", "good evening"]):
        return "greeting"
    if any(w in msg_lower for w in ["bye", "goodbye", "thanks", "thank you"]):
        return "farewell"

    if any(w in msg_lower for w in ["cancel"]):
        return "order_cancel"
    if any(w in msg_lower for w in ["refund", "money back"]):
        return "refund_status"

    if "return policy" in msg_lower or "return" in [w for w in msg_lower.split() if w in ("return", "returns")]:
        if any(w in msg_lower for w in ["policy", "how do i", "what is", "can i"]):
            return "faq_general"
        return "return_status"

    if any(w in msg_lower for w in ["order", "track", "delivery", "where is", "shipment"]):
        return "order_status"

    if any(w in msg_lower for w in ["weather", "temperature", "rain", "humid", "wind"]):
        return "weather_current"

    if any(w in msg_lower for w in ["recommend", "suggest", "best"]):
        return "product_recommend"
    if any(w in msg_lower for w in ["compare", "vs", "versus", "difference"]):
        return "product_compare"
    if any(w in msg_lower for w in ["search", "show", "find", "bluetooth", "under", "price"]):
        return "product_search"

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

    if any(w in msg_lower for w in ["contact", "call", "phone", "email", "support"]):
        return "contact_info"
    if any(w in msg_lower for w in ["about", "company", "privacy", "terms"]):
        return "company_info"
    if any(w in msg_lower for w in ["policy", "how to", "what is", "how do"]):
        return "faq_general"

    return "faq_general"

def _extract_entities_fallback(msg, intent):
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
    if intent in ("weather_current", "weather_forecast"):
        city_match = re.search(r'weather\s+(?:like\s+)?(?:in|at|for)\s+([A-Za-z\s]+)', msg, re.IGNORECASE)
        if not city_match:
            city_match = re.search(r'(?:in|at|for)\s+([A-Za-z\s]+?)\s*(?:\?|$)', msg, re.IGNORECASE)
        if city_match:
            entities["city"] = city_match.group(1).strip()
    track_match = re.search(r'tracking\s*(?:number|id|no)?[:\s]*([A-Za-z0-9]+)', msg, re.IGNORECASE)
    if track_match:
        entities["tracking_number"] = track_match.group(1)
    return entities
