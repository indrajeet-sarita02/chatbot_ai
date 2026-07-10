from db.connection import get_connection

def handle_faq_query(entities: dict, intent: str) -> str:
    conn = get_connection()

    if intent in ("company_info", "contact_info"):
        if "contact" in entities.get("query", "").lower() or intent == "contact_info":
            hours = conn.execute(
                "SELECT value FROM company_info WHERE key='business_hours'"
            ).fetchone()
            conn.close()
            return (
                "📞 Contact Us\n"
                "Phone: 1800-123-4567\n"
                "Email: support@ecommerce.com\n"
                f"{hours['value'] if hours else 'Available 24/7'}"
            )
        about = conn.execute(
            "SELECT value FROM company_info WHERE key='about_us'"
        ).fetchone()
        conn.close()
        return about["value"] if about else "Welcome to our ecommerce platform!"

    query = entities.get("query", "")
    if not query:
        query = entities.get("original_message", "")

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

    category_map = {
        "return": ("returns",),
        "refund": ("returns",),
        "track": ("shipping",),
        "payment": ("payments",),
        "cancel": ("orders",),
        "delivery": ("shipping",),
        "contact": ("contact",),
    }
    for word, (cat,) in category_map.items():
        if word in query.lower():
            row = conn.execute(
                "SELECT answer FROM faq WHERE category=? LIMIT 1", (cat,)
            ).fetchone()
            if row:
                conn.close()
                return row["answer"]

    conn.close()
    return "I don't have a specific answer for that. Would you like to speak with a human agent?"
