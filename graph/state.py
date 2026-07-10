class ChatState:
    def __init__(self, **kwargs):
        self.messages = kwargs.get("messages", [])
        self.user_id = kwargs.get("user_id", None)
        self.session_id = kwargs.get("session_id", "")
        self.intent = kwargs.get("intent", None)
        self.confidence = kwargs.get("confidence", None)
        self.entities = kwargs.get("entities", {})
        self.context = kwargs.get("context", {})
        self.requires_auth = kwargs.get("requires_auth", False)
        self.is_authenticated = kwargs.get("is_authenticated", False)
        self.response = kwargs.get("response", None)
        self.escalation_needed = kwargs.get("escalation_needed", False)
