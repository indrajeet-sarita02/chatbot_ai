from db.connection import get_connection

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
        return "📋 Here are your orders:\n\n" + "\n\n".join(_format_order(r) for r in rows)

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
        conn.close()
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
        f"• Status: {row['status'].title()}\n"
        f"• Payment: {row['payment_status'].title()}\n"
        f"• Amount: ₹{row['final_amount']:.2f}\n"
        f"• Delivery: {row['estimated_delivery'] or 'N/A'}\n"
        f"• Courier: {row['courier'] or 'Yet to be assigned'}\n"
        f"• Tracking: {row['tracking_number'] or 'N/A'}"
    )
