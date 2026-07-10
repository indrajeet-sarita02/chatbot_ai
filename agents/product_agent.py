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
        conn.close()
        return "\n".join(lines)

    elif intent == "product_recommend":
        results = conn.execute(
            "SELECT * FROM products WHERE is_active=1 AND stock>0 ORDER BY rating DESC, review_count DESC LIMIT 5"
        ).fetchall()
        lines = ["Top recommendations for you:\n"]
        for p in results:
            lines.append(f"• {p['name']} — ₹{p['price']:.0f} ⭐{p['rating']} ({p['review_count']} reviews)")
        conn.close()
        return "\n".join(lines)

    elif intent == "product_compare":
        compare_list = entities.get("compare_products", [])
        if not compare_list:
            return "Please tell me which products to compare."
        lines = [f"📊 Comparison: {' vs '.join(p.capitalize() for p in compare_list)}\n"]
        for pname in compare_list:
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
        conn.close()
        return "\n".join(lines)

    elif intent == "product_availability":
        p = conn.execute(
            "SELECT name, stock FROM products WHERE name LIKE ?", (f"%{name}%",)
        ).fetchone()
        conn.close()
        if not p:
            return f"I couldn't find a product matching '{name}'."
        if p["stock"] > 0:
            return f"✅ {p['name']} is in stock! Available quantity: {p['stock']} units."
        return f"❌ {p['name']} is currently out of stock."

    conn.close()
    return "I can help you find products. What are you looking for?"
