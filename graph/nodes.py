def identify_user(state):
    user_id = state.user_id
    is_authenticated = user_id is not None and user_id != "GUEST"
    state.is_authenticated = is_authenticated
    return state

def route_intent(state):
    from agents.intent_router import classify_intent
    last_msg = state.messages[-1]["content"] if state.messages else ""
    intent, confidence, entities = classify_intent(last_msg, state.context)
    state.intent = intent
    state.confidence = confidence
    entities["original_message"] = last_msg
    state.entities = entities
    return state

def execute_order_action(state):
    from agents.order_agent import handle_order_query
    response = handle_order_query(state.user_id, state.entities, state.intent)
    state.response = response
    return state

def execute_product_action(state):
    from agents.product_agent import handle_product_query
    response = handle_product_query(state.entities, state.intent)
    state.response = response
    return state

def execute_account_action(state):
    from agents.account_agent import handle_account_query
    response = handle_account_query(state.user_id, state.entities)
    state.response = response
    return state

def execute_weather_action(state):
    from agents.weather_agent import handle_weather_query
    response = handle_weather_query(state.entities, state.intent)
    state.response = response
    return state

def execute_faq_action(state):
    from agents.faq_agent import handle_faq_query
    response = handle_faq_query(state.entities, state.intent)
    state.response = response
    return state

def generate_response(state):
    from db.connection import get_connection
    response_text = state.response or "I'm sorry, I couldn't process your request."
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_history (session_id, role, message, intent) VALUES (?,?,?,?)",
        (state.session_id, "assistant", response_text, state.intent)
    )
    conn.commit()
    conn.close()
    state.messages.append({"role": "assistant", "content": response_text})
    state.response = response_text
    return state

def escalate_to_human(state):
    response_text = (
        "I'm sorry, I couldn't confidently answer your query. "
        "Let me connect you with a human support agent. "
        "Please expect a call or email shortly."
    )
    state.response = response_text
    state.escalation_needed = True
    state.messages.append({"role": "assistant", "content": response_text})
    return state
