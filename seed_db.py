"""
Seed initial SQLite database with admin user and sample transactions.
Uses only standard library (sqlite3, hashlib, base64, os, uuid, datetime).
"""
import sqlite3
import hashlib
import base64
import os
import uuid
from datetime import datetime, timezone

DB_PATH = "fraudshield_dev.db"

def get_hash(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000)
    return f"pbkdf2_sha256$600000${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"

def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(36) PRIMARY KEY,
        email VARCHAR(254) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role VARCHAR(20) DEFAULT 'analyst',
        created_at TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id VARCHAR(100) PRIMARY KEY,
        amount_minor BIGINT NOT NULL,
        currency VARCHAR(3) NOT NULL,
        occurred_at TIMESTAMP NOT NULL,
        merchant_category VARCHAR(100),
        features_json TEXT DEFAULT '{}',
        created_at TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id VARCHAR(36) PRIMARY KEY,
        transaction_id VARCHAR(100) UNIQUE NOT NULL,
        risk_index FLOAT NOT NULL,
        risk_tier VARCHAR(10) NOT NULL,
        reasons_json TEXT NOT NULL,
        model_version VARCHAR(80) DEFAULT 'demo-rules-v0',
        requires_review BOOLEAN DEFAULT 0,
        created_at TIMESTAMP,
        FOREIGN KEY(transaction_id) REFERENCES transactions(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id VARCHAR(36) PRIMARY KEY,
        transaction_id VARCHAR(100) NOT NULL,
        status VARCHAR(20) DEFAULT 'open',
        priority VARCHAR(20) DEFAULT 'medium',
        assigned_user_id VARCHAR(36),
        notes TEXT,
        created_at TIMESTAMP,
        FOREIGN KEY(transaction_id) REFERENCES transactions(id)
    )
    """)

    now = datetime.now(timezone.utc).isoformat()

    # Insert Admin user
    cur.execute("SELECT id FROM users WHERE email = 'admin@fraudshield.ai'")
    admin_row = cur.fetchone()
    admin_id = str(uuid.uuid4())
    if not admin_row:
        pw_hash = get_hash("AdminSecret2026!")
        cur.execute(
            "INSERT INTO users (id, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (admin_id, "admin@fraudshield.ai", pw_hash, "admin", now)
        )
        print("Created default admin: admin@fraudshield.ai / AdminSecret2026!")
    else:
        admin_id = admin_row[0]

    # Seed sample transactions & predictions
    samples = [
        ("TX_9941_US", 1250000, "USD", "crypto_exchange", 98.5, "HIGH",
         '["Unusually large transaction amount exceeding account baseline", "Unrecognized device hardware fingerprint", "Cross-border IP"]', 1),
        ("TX_9940_UK", 432000, "USD", "luxury_retail", 84.0, "HIGH",
         '["Rapid velocity jump", "Foreign proxy connection"]', 1),
        ("TX_9939_EU", 15400, "EUR", "online_electronics", 62.0, "MEDIUM",
         '["Multiple failed card verification attempts"]', 1),
        ("TX_9938_SG", 8500, "USD", "groceries", 12.0, "LOW",
         '["Familiar domestic merchant", "Recognized biometric device"]', 0),
        ("TX_9937_IN", 24000, "USD", "travel_airlines", 18.5, "LOW",
         '["Normal transaction velocity"]', 0)
    ]

    for tx_id, amt, curr, cat, score, tier, reasons, req_rev in samples:
        cur.execute("SELECT id FROM transactions WHERE id = ?", (tx_id,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO transactions (id, amount_minor, currency, occurred_at, merchant_category, features_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (tx_id, amt, curr, now, cat, "{}", now)
            )
            pred_id = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO predictions (id, transaction_id, risk_index, risk_tier, reasons_json, model_version, requires_review, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (pred_id, tx_id, score, tier, reasons, "v0.1.0-rules", req_rev, now)
            )
            if req_rev:
                alert_id = "ALT_" + tx_id.split("_")[1]
                cur.execute(
                    "INSERT INTO alerts (id, transaction_id, status, priority, assigned_user_id, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (alert_id, tx_id, "open", tier.lower(), admin_id, f"High risk anomalous activity on {cat}", now)
                )

    conn.commit()
    conn.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed()
