from graph.state import ChatState
from graph.nodes import (
    identify_user, route_intent,
    execute_order_action, execute_product_action,
    execute_account_action, execute_weather_action,
    execute_faq_action, generate_response, escalate_to_human
)

INTENT_NODE_MAP = {
    "order_status": "order",
    "order_tracking": "order",
    "order_cancel": "order",
    "refund_status": "order",
    "return_status": "order",
    "product_search": "product",
    "product_recommend": "product",
    "product_compare": "product",
    "product_availability": "product",
    "product_review": "product",
    "cart_info": "product",
    "wishlist_info": "account",
    "shipping_charges": "faq",
    "delivery_date": "faq",
    "payment_status": "faq",
    "payment_methods": "faq",
    "emi_options": "faq",
    "coupons": "faq",
    "offers": "faq",
    "loyalty": "faq",
    "weather_current": "weather",
    "weather_forecast": "weather",
    "faq_general": "faq",
    "company_info": "faq",
    "contact_info": "faq",
    "login_help": "faq",
    "password_reset": "faq",
    "address_manage": "account",
    "greeting": "faq",
    "farewell": "faq",
    "thanks": "faq",
}

NODE_FN_MAP = {
    "order": execute_order_action,
    "product": execute_product_action,
    "account": execute_account_action,
    "weather": execute_weather_action,
    "faq": execute_faq_action,
}

def run_graph(state):
    state = identify_user(state)
    state = route_intent(state)

    if state.confidence is None or state.confidence < 0.4:
        state = escalate_to_human(state)
    else:
        node_name = INTENT_NODE_MAP.get(state.intent, "faq")
        node_fn = NODE_FN_MAP.get(node_name, execute_faq_action)
        state = node_fn(state)

    state = generate_response(state)
    return state
