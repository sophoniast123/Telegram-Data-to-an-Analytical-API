import os
import json
import psycopg2
from pathlib import Path

# PostgreSQL connection
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 5432),
    dbname=os.getenv("DB_NAME", "medical_warehouse"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

data_dir = Path("data/raw/telegram_messages")

# Create raw table
cur.execute("""
CREATE TABLE IF NOT EXISTS raw.telegram_messages (
    message_id BIGINT PRIMARY KEY,
    channel_name TEXT,
    message_date TIMESTAMP,
    message_text TEXT,
    views INT,
    forwards INT,
    has_media BOOLEAN,
    image_path TEXT
)
""")
conn.commit()

# Load JSON files
for date_folder in data_dir.iterdir():
    if date_folder.is_dir():
        for file in date_folder.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                messages = json.load(f)
                for msg in messages:
                    cur.execute("""
                    INSERT INTO raw.telegram_messages (
                        message_id, channel_name, message_date,
                        message_text, views, forwards,
                        has_media, image_path
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (message_id) DO NOTHING
                    """, (
                        msg["message_id"], msg["channel_name"], msg["message_date"],
                        msg["message_text"], msg["views"], msg["forwards"],
                        msg["has_media"], msg["image_path"]
                    ))
conn.commit()
cur.close()
conn.close()
