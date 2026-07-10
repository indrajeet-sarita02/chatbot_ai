from db.connection import get_connection

def handle_account_query(user_id: str, entities: dict) -> str:
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return "Please log in to access your account information."

    intent = entities.get("account_intent", "")

    if "address" in intent:
        addrs = conn.execute(
            "SELECT * FROM addresses WHERE user_id=?", (user_id,)
        ).fetchall()
        if not addrs:
            conn.close()
            return "You have no saved addresses."
        lines = ["Your saved addresses:\n"]
        for a in addrs:
            d = " (Default)" if a["is_default"] else ""
            lines.append(f"• [{a['label']}]{d} {a['street']}, {a['city']}, {a['state']} - {a['pincode']}")
        conn.close()
        return "\n".join(lines)

    elif "profile" in intent:
        conn.close()
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
        conn.close()
        if not items:
            return "Your wishlist is empty."
        lines = ["❤️ Your Wishlist:\n"]
        for it in items:
            stock = "In Stock" if it["stock"] > 0 else "Out of Stock"
            lines.append(f"• {it['name']} — ₹{it['price']:.0f} ⭐{it['rating']} | {stock}")
        return "\n".join(lines)

    conn.close()
    return "I can help with your account. What would you like to know?"
