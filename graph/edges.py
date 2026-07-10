from graph.state import ChatState

def should_escalate(state: ChatState) -> str:
    confidence = state.get("confidence", 0.0)
    if confidence < 0.4:
        return "escalate"
    return state.get("intent", "faq")
