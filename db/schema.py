def create_tables(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        user_id        TEXT PRIMARY KEY,
        name           TEXT NOT NULL,
        email          TEXT UNIQUE NOT NULL,
        phone          TEXT,
        password_hash  TEXT NOT NULL,
        is_guest       INTEGER DEFAULT 0,
        preferred_lang TEXT DEFAULT 'en',
        created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS addresses (
        address_id  TEXT PRIMARY KEY,
        user_id     TEXT REFERENCES users(user_id),
        label       TEXT,
        street      TEXT,
        city        TEXT,
        state       TEXT,
        pincode     TEXT,
        is_default  INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS categories (
        category_id   TEXT PRIMARY KEY,
        name          TEXT NOT NULL,
        parent_id     TEXT REFERENCES categories(category_id)
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id    TEXT PRIMARY KEY,
        name          TEXT NOT NULL,
        description   TEXT,
        category_id   TEXT REFERENCES categories(category_id),
        price         REAL NOT NULL,
        mrp           REAL,
        stock         INTEGER DEFAULT 0,
        rating        REAL DEFAULT 0,
        review_count  INTEGER DEFAULT 0,
        brand         TEXT,
        specs         TEXT,
        images        TEXT,
        is_active     INTEGER DEFAULT 1,
        created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS orders (
        order_id        TEXT PRIMARY KEY,
        user_id         TEXT REFERENCES users(user_id),
        order_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount    REAL NOT NULL,
        discount        REAL DEFAULT 0,
        final_amount    REAL NOT NULL,
        status          TEXT DEFAULT 'confirmed',
        payment_status  TEXT DEFAULT 'pending',
        payment_method  TEXT,
        shipping_charge REAL DEFAULT 0,
        delivery_address_id TEXT REFERENCES addresses(address_id),
        courier         TEXT,
        tracking_number TEXT,
        estimated_delivery DATE,
        delivered_date  DATE,
        cancellation_reason TEXT,
        return_reason   TEXT,
        refund_amount   REAL,
        refund_date     DATE
    );

    CREATE TABLE IF NOT EXISTS order_items (
        item_id     TEXT PRIMARY KEY,
        order_id    TEXT REFERENCES orders(order_id),
        product_id  TEXT REFERENCES products(product_id),
        quantity    INTEGER DEFAULT 1,
        unit_price  REAL NOT NULL,
        subtotal    REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS cart (
        cart_id    TEXT PRIMARY KEY,
        user_id    TEXT REFERENCES users(user_id),
        product_id TEXT REFERENCES products(product_id),
        quantity   INTEGER DEFAULT 1,
        added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS wishlist (
        user_id    TEXT REFERENCES users(user_id),
        product_id TEXT REFERENCES products(product_id),
        added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, product_id)
    );

    CREATE TABLE IF NOT EXISTS reviews (
        review_id   TEXT PRIMARY KEY,
        user_id     TEXT REFERENCES users(user_id),
        product_id  TEXT REFERENCES products(product_id),
        rating      INTEGER CHECK(rating BETWEEN 1 AND 5),
        comment     TEXT,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS coupons (
        coupon_code  TEXT PRIMARY KEY,
        description  TEXT,
        discount_pct REAL,
        max_discount REAL,
        min_cart     REAL,
        valid_from   DATE,
        valid_to     DATE,
        usage_limit  INTEGER DEFAULT 1,
        used_count   INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS loyalty_points (
        user_id    TEXT PRIMARY KEY REFERENCES users(user_id),
        points     INTEGER DEFAULT 0,
        tier       TEXT DEFAULT 'silver'
    );

    CREATE TABLE IF NOT EXISTS chat_history (
        session_id  TEXT NOT NULL,
        role        TEXT NOT NULL,
        message     TEXT NOT NULL,
        intent      TEXT,
        confidence  REAL,
        timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS faq (
        faq_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        question    TEXT NOT NULL,
        answer      TEXT NOT NULL,
        category    TEXT,
        lang        TEXT DEFAULT 'en',
        keywords    TEXT
    );

    CREATE TABLE IF NOT EXISTS company_info (
        key   TEXT PRIMARY KEY,
        value TEXT
    );
    """)
    conn.commit()
