from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from pydantic import BaseModel
import os

app = FastAPI(title="Medical Telegram Analytics API")

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)

class TopProductResponse(BaseModel):
    product_name: str
    mention_count: int

@app.get("/api/reports/top-products", response_model=list[TopProductResponse])
def get_top_products(limit: int = 10):
    query = text("""
        SELECT product_name, COUNT(*) AS mention_count
        FROM fct_messages_products
        GROUP BY product_name
        ORDER BY mention_count DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"limit": limit}).fetchall()
    return [{"product_name": row[0], "mention_count": row[1]} for row in result]
