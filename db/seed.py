from datetime import date, timedelta
from db.connection import get_connection
from db.schema import create_tables

def seed():
    conn = get_connection()
    create_tables(conn)

    today = date.today()

    users = [
        ("U1001", "Rajesh Kumar", "rajesh@example.com", "9876543210", "hash_pwd_1", 0),
        ("U1002", "Priya Sharma", "priya@example.com", "9876543211", "hash_pwd_2", 0),
        ("U1003", "Amit Verma", "amit@example.com", "9876543212", "hash_pwd_3", 0),
        ("U1004", "Sneha Patel", "sneha@example.com", "9876543213", "hash_pwd_4", 0),
        ("U1005", "Vikram Singh", "vikram@example.com", "9876543214", "hash_pwd_5", 0),
        ("U1006", "Ananya Gupta", "ananya@example.com", "9876543215", "hash_pwd_6", 0),
        ("U1007", "Rohit Joshi", "rohit@example.com", "9876543216", "hash_pwd_7", 0),
        ("U1008", "Neha Kapoor", "neha@example.com", "9876543217", "hash_pwd_8", 0),
        ("GUEST", "Guest User", "guest@example.com", "", "guest", 1),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO users VALUES (?,?,?,?,?,?,?,?)",
        [(u[0], u[1], u[2], u[3], u[4], u[5], "en", "2025-01-01") for u in users]
    )

    addresses = [
        ("A001", "U1001", "Home", "12 MG Road", "Mumbai", "Maharashtra", "400001", 1),
        ("A002", "U1001", "Office", "BKC, Bandra East", "Mumbai", "Maharashtra", "400051", 0),
        ("A003", "U1002", "Work", "45 Bannerghatta", "Bangalore", "Karnataka", "560076", 1),
        ("A004", "U1002", "Home", "JP Nagar 3rd Phase", "Bangalore", "Karnataka", "560078", 0),
        ("A005", "U1003", "Home", "22 Civil Lines", "Delhi", "Delhi", "110054", 1),
        ("A006", "U1004", "Home", "7 MG Road", "Pune", "Maharashtra", "411001", 1),
        ("A007", "U1005", "Home", "88 Park Street", "Kolkata", "West Bengal", "700016", 1),
        ("A008", "U1005", "Office", "Sector V, Salt Lake", "Kolkata", "West Bengal", "700091", 0),
        ("A009", "U1006", "Home", "15 Jubilee Hills", "Hyderabad", "Telangana", "500033", 1),
        ("A010", "U1007", "Home", "55 Gomti Nagar", "Lucknow", "Uttar Pradesh", "226010", 1),
        ("A011", "U1008", "Home", "32 Anna Nagar", "Chennai", "Tamil Nadu", "600040", 1),
        ("A012", "U1008", "Office", "DLF IT Park", "Chennai", "Tamil Nadu", "600032", 0),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO addresses VALUES (?,?,?,?,?,?,?,?)", addresses
    )

    cats = [
        ("CAT-ELEC", "Electronics", None),
        ("CAT-PHN", "Mobile Phones", "CAT-ELEC"),
        ("CAT-LAP", "Laptops", "CAT-ELEC"),
        ("CAT-AUD", "Audio", "CAT-ELEC"),
        ("CAT-WEAR", "Wearables", "CAT-ELEC"),
        ("CAT-FSH", "Fashion", None),
        ("CAT-FSH-M", "Men's Clothing", "CAT-FSH"),
        ("CAT-FSH-W", "Women's Clothing", "CAT-FSH"),
        ("CAT-HOM", "Home & Kitchen", None),
        ("CAT-BKS", "Books", None),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO categories VALUES (?,?,?)", cats
    )

    products = [
        ("P100", "iPhone 15", "Latest Apple smartphone with A16 Bionic chip, 48MP camera", "CAT-PHN", 79999, 89900, 50, 4.5, 120, "Apple", '{"color":"Black","storage":"128GB"}', '["img1.jpg"]', 1),
        ("P101", "Samsung Galaxy S24", "Flagship Android phone with Galaxy AI features, 200MP camera", "CAT-PHN", 74999, 84999, 30, 4.3, 85, "Samsung", '{"color":"Titanium Gray","storage":"256GB"}', '["img2.jpg"]', 1),
        ("P102", "MacBook Air M3", "13.6-inch lightweight laptop with Apple M3 chip, 18hr battery", "CAT-LAP", 114999, 129900, 20, 4.7, 200, "Apple", '{"ram":"16GB","storage":"512GB"}', '["img3.jpg"]', 1),
        ("P103", "Sony WH-1000XM5", "Industry-leading noise cancelling wireless headphones, 30hr battery", "CAT-AUD", 29990, 34990, 100, 4.6, 300, "Sony", '{"type":"Over-ear","battery":"30hrs"}', '["img4.jpg"]', 1),
        ("P104", "Bluetooth Speaker", "Portable waterproof speaker 10W with deep bass", "CAT-AUD", 2499, 3999, 200, 4.1, 50, "Boat", '{"power":"10W","battery":"12hrs"}', '["img5.jpg"]', 1),
        ("P105", "OnePlus Nord 4", "Mid-range 5G phone with 100W charging, 50MP camera", "CAT-PHN", 27999, 32999, 80, 4.2, 45, "OnePlus", '{"color":"Green","storage":"128GB"}', '["img6.jpg"]', 1),
        ("P106", "Dell XPS 15", "Premium laptop with Intel i7, 32GB RAM, OLED display", "CAT-LAP", 159999, 179999, 10, 4.5, 89, "Dell", '{"ram":"32GB","storage":"1TB"}', '["img7.jpg"]', 1),
        ("P107", "Apple AirPods Pro 2", "Wireless earbuds with active noise cancellation, USB-C", "CAT-AUD", 24900, 29900, 150, 4.7, 450, "Apple", '{"type":"In-ear","battery":"6hrs"}', '["img8.jpg"]', 1),
        ("P108", "Apple Watch Series 9", "Smartwatch with health monitoring, GPS, always-on display", "CAT-WEAR", 41900, 45900, 40, 4.5, 180, "Apple", '{"size":"45mm","color":"Midnight"}', '["img9.jpg"]', 1),
        ("P109", "Samsung Galaxy Watch 6", "Smartwatch with body composition, sleep tracking", "CAT-WEAR", 29999, 34999, 60, 4.3, 95, "Samsung", '{"size":"44mm","color":"Silver"}', '["img10.jpg"]', 1),
        ("P110", "Men's Cotton T-Shirt", "Comfortable 100% cotton round neck t-shirt, pack of 3", "CAT-FSH-M", 999, 1499, 500, 4.0, 230, "U.S. Polo", '{"size":"S,M,L,XL","color":"Assorted"}', '["img11.jpg"]', 1),
        ("P111", "Women's Silk Saree", "Elegant Banarasi silk saree with gold border", "CAT-FSH-W", 3999, 6999, 100, 4.4, 67, "Manyavar", '{"color":"Red","length":"6.3m"}', '["img12.jpg"]', 1),
        ("P112", "Non-Stick Cookware Set", "3-piece kitchen set: frypan, saucepan, kadhai with lids", "CAT-HOM", 2499, 3999, 75, 4.2, 120, "Prestige", '{"pieces":"3","material":"Aluminum"}', '["img13.jpg"]', 1),
        ("P113", "The Alchemist by Paulo Coelho", "Bestselling fiction book about following your dreams", "CAT-BKS", 299, 399, 1000, 4.6, 5000, "HarperCollins", '{"pages":"208","language":"English"}', '["img14.jpg"]', 1),
        ("P114", "Gaming Laptop RTX 4060", "Lenovo Legion with i9, RTX 4060, 16GB RAM, 1TB SSD", "CAT-LAP", 134999, 149999, 15, 4.4, 34, "Lenovo", '{"ram":"16GB","storage":"1TB","gpu":"RTX 4060"}', '["img15.jpg"]', 1),
        ("P115", "Fitbit Charge 6", "Fitness tracker with heart rate, SpO2, GPS, 7-day battery", "CAT-WEAR", 13999, 16999, 120, 4.2, 78, "Fitbit", '{"color":"Black","battery":"7days"}', '["img16.jpg"]', 1),
        ("P116", "Men's Formal Shoes", "Leather lace-up formal shoes, comfort sole", "CAT-FSH-M", 2499, 3999, 300, 4.1, 145, "Bata", '{"size":"7-12","color":"Brown,Black"}', '["img17.jpg"]', 1),
        ("P117", "Women's Handbag", "Premium leather handbag with multiple compartments", "CAT-FSH-W", 3299, 4999, 80, 4.3, 92, "Hidesign", '{"color":"Tan","material":"Leather"}', '["img18.jpg"]', 1),
        ("P118", "Mixer Grinder 750W", "3-jar mixer grinder with super-extraction technology", "CAT-HOM", 3499, 4999, 200, 4.4, 320, "Bajaj", '{"jars":"3","power":"750W"}', '["img19.jpg"]', 1),
        ("P119", "Atomic Habits by James Clear", "Bestselling self-help book on habit formation", "CAT-BKS", 399, 499, 800, 4.8, 8200, "Penguin", '{"pages":"320","language":"English"}', '["img20.jpg"]', 1),
        ("P120", "Think and Grow Rich", "Classic personal development book by Napoleon Hill", "CAT-BKS", 199, 299, 1500, 4.5, 3400, "Dover", '{"pages":"233","language":"English"}', '["img21.jpg"]', 1),
        ("P121", "Wireless Mouse", "Ergonomic silent click wireless mouse, 2.4GHz", "CAT-ELEC", 799, 1499, 500, 4.0, 210, "Logitech", '{"type":"Wireless","battery":"12months"}', '["img22.jpg"]', 1),
        ("P122", "USB-C Hub 7-in-1", "Multi-port adapter with HDMI, USB 3.0, SD card reader", "CAT-ELEC", 1999, 2999, 350, 4.3, 180, "Anker", '{"ports":"7","type":"USB-C"}', '["img23.jpg"]', 1),
        ("P123", "Noise Cancelling Earbuds", "Wireless earbuds with ANC, 40hr playback, IPX5", "CAT-AUD", 4499, 6999, 250, 4.2, 95, "boAt", '{"type":"TWS","battery":"40hrs"}', '["img24.jpg"]', 1),
        ("P124", "Men's Denim Jacket", "Classic blue denim jacket, regular fit", "CAT-FSH-M", 1999, 2999, 180, 4.1, 67, "Levi's", '{"size":"S-XXL","color":"Blue"}', '["img25.jpg"]', 1),
        ("P125", "Running Shoes", "Lightweight cushioned running shoes with mesh upper", "CAT-FSH-M", 3999, 5999, 220, 4.4, 156, "Nike", '{"size":"7-12","color":"Black,White"}', '["img26.jpg"]', 1),
    ]
    conn.executemany(
        """INSERT OR IGNORE INTO products
           (product_id,name,description,category_id,price,mrp,stock,rating,review_count,brand,specs,images,is_active)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", products
    )

    orders = [
        ("ORD-1001", "U1001", "2026-07-01", 79999.0, 0, 79999.0, "shipped", "paid", "Credit Card", 0, "A001", "BlueDart", "BLD123456", str(today + timedelta(days=2)), None, None, None, None, None),
        ("ORD-1002", "U1001", "2026-06-28", 29990.0, 500, 29490.0, "delivered", "paid", "UPI", 0, "A001", "Delhivery", "DLV789012", str(today - timedelta(days=5)), str(today - timedelta(days=3)), None, None, None, None),
        ("ORD-1003", "U1002", "2026-07-02", 114999.0, 2000, 112999.0, "confirmed", "pending", "EMI", 0, "A003", None, None, str(today + timedelta(days=7)), None, None, None, None, None),
        ("ORD-1004", "U1002", "2026-06-15", 24900.0, 1000, 23900.0, "delivered", "paid", "Debit Card", 0, "A003", "BlueDart", "BLD456789", str(today - timedelta(days=20)), str(today - timedelta(days=18)), None, None, None, None),
        ("ORD-1005", "U1003", "2026-06-25", 2499.0, 0, 2499.0, "cancelled", "refunded", "UPI", 0, "A005", None, None, None, None, "Changed mind", None, 2499.0, str(today - timedelta(days=10))),
        ("ORD-1006", "U1003", "2026-07-05", 999.0, 0, 999.0, "shipped", "paid", "Wallet", 40, "A005", "Delhivery", "DLV345678", str(today + timedelta(days=1)), None, None, None, None, None),
        ("ORD-1007", "U1004", "2026-07-03", 41900.0, 1500, 40400.0, "shipped", "paid", "Credit Card", 0, "A006", "BlueDart", "BLD789012", str(today + timedelta(days=3)), None, None, None, None, None),
        ("ORD-1008", "U1001", "2026-06-10", 2499.0, 200, 2299.0, "returned", "refunded", "UPI", 0, "A001", "EcomExpress", "ECM123456", str(today - timedelta(days=28)), str(today - timedelta(days=26)), None, "Defective product", 2299.0, str(today - timedelta(days=22))),
        ("ORD-1009", "U1004", "2026-07-04", 74999.0, 3000, 71999.0, "confirmed", "paid", "Net Banking", 0, "A006", None, None, str(today + timedelta(days=6)), None, None, None, None, None),
        ("ORD-1010", "U1002", "2026-07-06", 299.0, 0, 299.0, "confirmed", "pending", "COD", 0, "A003", None, None, str(today + timedelta(days=4)), None, None, None, None, None),
        ("ORD-1011", "U1004", "2026-07-08", 27999.0, 0, 27999.0, "confirmed", "paid", "UPI", 0, "A006", None, None, str(today + timedelta(days=5)), None, None, None, None, None),
        ("ORD-1012", "U1005", "2026-07-01", 3999.0, 500, 3499.0, "delivered", "paid", "Debit Card", 0, "A007", "BlueDart", "BLD567890", str(today - timedelta(days=6)), str(today - timedelta(days=4)), None, None, None, None),
        ("ORD-1013", "U1005", "2026-07-07", 4499.0, 0, 4499.0, "shipped", "paid", "UPI", 0, "A007", "Delhivery", "DLV901234", str(today + timedelta(days=2)), None, None, None, None, None),
        ("ORD-1014", "U1006", "2026-06-30", 1999.0, 100, 1899.0, "delivered", "paid", "Wallet", 0, "A009", "EcomExpress", "ECM789012", str(today - timedelta(days=8)), str(today - timedelta(days=6)), None, None, None, None),
        ("ORD-1015", "U1006", "2026-07-05", 799.0, 0, 799.0, "shipped", "paid", "Credit Card", 40, "A009", "BlueDart", "BLD234567", str(today + timedelta(days=1)), None, None, None, None, None),
        ("ORD-1016", "U1007", "2026-07-03", 134999.0, 5000, 129999.0, "confirmed", "pending", "EMI", 0, "A010", None, None, str(today + timedelta(days=10)), None, None, None, None, None),
        ("ORD-1017", "U1007", "2026-06-20", 2499.0, 0, 2499.0, "cancelled", "refunded", "UPI", 0, "A010", None, None, None, None, "Out of stock", None, 2499.0, str(today - timedelta(days=12))),
        ("ORD-1018", "U1008", "2026-07-02", 3299.0, 200, 3099.0, "delivered", "paid", "Net Banking", 0, "A011", "Delhivery", "DLV567890", str(today - timedelta(days=5)), str(today - timedelta(days=3)), None, None, None, None),
        ("ORD-1019", "U1008", "2026-07-06", 2499.0, 0, 2499.0, "shipped", "paid", "Debit Card", 0, "A011", "BlueDart", "BLD345678", str(today + timedelta(days=4)), None, None, None, None, None),
        ("ORD-1020", "U1001", "2026-07-07", 399.0, 0, 399.0, "confirmed", "paid", "Wallet", 0, "A001", None, None, str(today + timedelta(days=3)), None, None, None, None, None),
    ]
    conn.executemany(
        """INSERT OR IGNORE INTO orders
           (order_id,user_id,order_date,total_amount,discount,final_amount,status,payment_status,payment_method,shipping_charge,delivery_address_id,courier,tracking_number,estimated_delivery,delivered_date,cancellation_reason,return_reason,refund_amount,refund_date)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", orders
    )

    items = [
        ("OI-001", "ORD-1001", "P100", 1, 79999, 79999.0),
        ("OI-002", "ORD-1002", "P103", 1, 29990, 29990.0),
        ("OI-003", "ORD-1003", "P102", 1, 114999, 114999.0),
        ("OI-004", "ORD-1004", "P107", 1, 24900, 24900.0),
        ("OI-005", "ORD-1005", "P104", 1, 2499, 2499.0),
        ("OI-006", "ORD-1006", "P110", 1, 999, 999.0),
        ("OI-007", "ORD-1007", "P108", 1, 41900, 41900.0),
        ("OI-008", "ORD-1008", "P104", 1, 2499, 2499.0),
        ("OI-009", "ORD-1009", "P101", 1, 74999, 74999.0),
        ("OI-010", "ORD-1010", "P113", 1, 299, 299.0),
        ("OI-011", "ORD-1011", "P105", 1, 27999, 27999.0),
        ("OI-012", "ORD-1012", "P125", 1, 3999, 3999.0),
        ("OI-013", "ORD-1013", "P123", 1, 4499, 4499.0),
        ("OI-014", "ORD-1014", "P124", 1, 1999, 1999.0),
        ("OI-015", "ORD-1015", "P121", 1, 799, 799.0),
        ("OI-016", "ORD-1016", "P114", 1, 134999, 134999.0),
        ("OI-017", "ORD-1017", "P116", 1, 2499, 2499.0),
        ("OI-018", "ORD-1018", "P117", 1, 3299, 3299.0),
        ("OI-019", "ORD-1019", "P116", 1, 2499, 2499.0),
        ("OI-020", "ORD-1020", "P119", 1, 399, 399.0),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO order_items VALUES (?,?,?,?,?,?)", items
    )

    cart = [
        ("C001", "U1001", "P101", 1),
        ("C002", "U1001", "P107", 2),
        ("C003", "U1002", "P111", 1),
        ("C004", "U1002", "P112", 1),
        ("C005", "U1003", "P114", 1),
        ("C006", "U1004", "P105", 1),
        ("C007", "U1005", "P125", 2),
        ("C008", "U1005", "P117", 1),
        ("C009", "U1006", "P119", 3),
        ("C010", "U1007", "P114", 1),
        ("C011", "U1008", "P117", 1),
        ("C012", "U1008", "P111", 1),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO cart VALUES (?,?,?,?,?)",
        [(c[0], c[1], c[2], c[3], "2026-07-09") for c in cart]
    )

    wishlist = [
        ("U1001", "P107"),
        ("U1001", "P109"),
        ("U1002", "P100"),
        ("U1002", "P114"),
        ("U1003", "P102"),
        ("U1004", "P111"),
        ("U1005", "P102"),
        ("U1005", "P108"),
        ("U1006", "P113"),
        ("U1006", "P119"),
        ("U1007", "P115"),
        ("U1008", "P117"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO wishlist VALUES (?,?,?)",
        [(w[0], w[1], "2026-07-09") for w in wishlist]
    )

    reviews = [
        ("R001", "U1001", "P100", 5, "Amazing phone! Camera is superb."),
        ("R002", "U1002", "P100", 4, "Great phone but battery could be better."),
        ("R003", "U1001", "P103", 5, "Best noise cancellation I've ever used."),
        ("R004", "U1002", "P107", 5, "AirPods are incredible. Worth every rupee."),
        ("R005", "U1003", "P104", 4, "Good speaker for the price. Decent bass."),
        ("R006", "U1004", "P108", 5, "Love my Apple Watch! Health features are great."),
        ("R007", "U1005", "P125", 5, "Super comfortable running shoes. Great for daily jogging."),
        ("R008", "U1005", "P123", 4, "Good earbuds for the price. Noise cancellation works well."),
        ("R009", "U1006", "P124", 4, "Nice denim jacket, fits well. True to size."),
        ("R010", "U1006", "P119", 5, "Life-changing book! Must read for everyone."),
        ("R011", "U1007", "P114", 5, "Beast of a laptop! Runs all games at ultra settings."),
        ("R012", "U1008", "P117", 4, "Beautiful handbag. Looks premium and lots of space."),
        ("R013", "U1001", "P110", 3, "Decent t-shirts for the price. Fabric could be softer."),
        ("R014", "U1002", "P111", 5, "Stunning saree! The border work is beautiful."),
        ("R015", "U1003", "P106", 4, "Great laptop but expensive. Display is gorgeous."),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO reviews VALUES (?,?,?,?,?,?)",
        [(r[0], r[1], r[2], r[3], r[4], str(today)) for r in reviews]
    )

    faqs = [
        ("How do I return a product?", "You can return any product within 30 days of delivery. Go to Your Orders, select the item and click Return. We'll arrange a free pickup.", "returns", "en", "return,refund,exchange,pickup"),
        ("What is your refund policy?", "Refunds are processed within 5-7 business days after the returned item is received at our warehouse. The amount is credited to your original payment method.", "returns", "en", "refund,money,back,payment"),
        ("How can I track my order?", "Go to Your Orders and click Track Package next to your order. You can also use the tracking number on the courier's website for real-time updates.", "shipping", "en", "track,shipment,courier,tracking"),
        ("What payment methods do you accept?", "We accept all major Credit/Debit Cards, UPI (Google Pay, PhonePe, Paytm), Net Banking, EMI options, and Wallet payments.", "payments", "en", "payment,upi,card,emi,wallet"),
        ("How do I cancel my order?", "Orders can be cancelled within 24 hours of placing. Go to Your Orders and click Cancel. Once shipped, cancellation is not possible.", "orders", "en", "cancel,order,shipped"),
        ("What is your delivery time?", "Standard delivery takes 3-5 business days. Express delivery is available in 1-2 business days for an additional charge.", "shipping", "en", "delivery,shipping,time,express"),
        ("How do I contact customer support?", "Call us at 1800-123-4567 or email support@ecommerce.com. We are available 24x7. Live chat is also available on our website.", "contact", "en", "contact,support,phone,email,chat"),
        ("What is your exchange policy?", "You can exchange size or color within 15 days of delivery. The product must be unused with original tags.", "returns", "en", "exchange,size,color,replace"),
        ("Do you offer international shipping?", "Currently we ship only within India. International shipping will be available soon.", "shipping", "en", "international,shipping,abroad,outside"),
        ("How do I apply a coupon?", "Enter the coupon code at checkout in the 'Apply Coupon' section. Only one coupon can be used per order.", "payments", "en", "coupon,discount,code,apply"),
        ("मैं अपना ऑर्डर कैसे ट्रैक करूं?", "अपने ऑर्डर पर जाएं और ट्रैक पैकेज पर क्लिक करें। आप कूरियर वेबसाइट पर ट्रैकिंग नंबर का उपयोग भी कर सकते हैं।", "shipping", "hi", "ट्रैक,ऑर्डर,कूरियर"),
        ("क्या आप कोड ऑन डिलीवरी प्रदान करते हैं?", "हां, हम चुनिंदा पिनकोड पर COD प्रदान करते हैं। अधिकतम ऑर्डर राशि ₹50,000 है।", "payments", "hi", "cod,डिलीवरी,भुगतान"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO faq (question,answer,category,lang,keywords) VALUES (?,?,?,?,?)", faqs
    )

    info = [
        ("company_name", "ShopEase Ecommerce Pvt Ltd"),
        ("about_us", "ShopEase is India's leading online shopping platform offering millions of products across electronics, fashion, home, books, and more. Founded in 2020, we serve 10M+ happy customers."),
        ("business_hours", "Customer Support: 24x7 | Store hours: Open 365 days | Delivery: 7 days a week"),
        ("privacy_policy", "We value your privacy. Your personal data is encrypted using AES-256 and never shared with third parties without your explicit consent."),
        ("terms", "By using our platform you agree to our terms and conditions. All sales are subject to our return and refund policy. Prices may vary without notice."),
        ("return_window", "30 days from delivery"),
        ("refund_timeline", "5-7 business days after return pickup"),
        ("customer_care_phone", "1800-123-4567"),
        ("customer_care_email", "support@ecommerce.com"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO company_info (key,value) VALUES (?,?)", info
    )

    coupons = [
        ("WELCOME10", "10% off for new users (max ₹500)", 10, 500, 999, "2025-01-01", "2026-12-31", 10000, 0),
        ("FREEDEL", "Free delivery on orders above ₹500", 0, 0, 500, "2025-01-01", "2026-12-31", 10000, 0),
        ("FESTIVE50", "Flat ₹500 off on orders above ₹2999", 0, 500, 2999, "2026-07-01", "2026-07-15", 5000, 0),
        ("SUMMER20", "20% off on electronics (max ₹2000)", 20, 2000, 4999, "2026-06-01", "2026-08-31", 3000, 0),
        ("BOOKLOVER", "15% off on books (max ₹100)", 15, 100, 500, "2026-01-01", "2026-12-31", 10000, 0),
        ("FLAT200", "Flat ₹200 off on orders above ₹1499", 0, 200, 1499, "2026-07-01", "2026-07-31", 2000, 0),
        ("WEEKEND50", "50% off on fashion (max ₹750)", 50, 750, 999, "2026-07-10", "2026-07-12", 500, 0),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO coupons VALUES (?,?,?,?,?,?,?,?,?)", coupons
    )

    loyalty = [
        ("U1001", 1250, "gold"),
        ("U1002", 850, "silver"),
        ("U1003", 200, "silver"),
        ("U1004", 450, "silver"),
        ("U1005", 600, "silver"),
        ("U1006", 310, "silver"),
        ("U1007", 100, "bronze"),
        ("U1008", 520, "silver"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO loyalty_points VALUES (?,?,?)", loyalty
    )

    conn.commit()
    conn.close()
