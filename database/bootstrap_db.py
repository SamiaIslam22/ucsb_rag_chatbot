import os
from dotenv import load_dotenv
import psycopg
from pgvector.psycopg import register_vector
load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
DDL = """
CREATE EXTENSION IF NOT EXISTS vector;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'content_type') THEN
        CREATE TYPE content_type AS ENUM ('text', 'image', 'table');
    END IF;
END$$;
CREATE TABLE IF NOT EXISTS items (
    id              bigserial PRIMARY KEY,
    url             text,
    title           text,
    content         text,
    chunk_number    integer,
    total_chunks    integer,
    character_count integer,
    metadata        jsonb,
    content_type    content_type NOT NULL,
    embedding       vector(1536),
    created_at      timestamptz DEFAULT now(),
    UNIQUE (url, chunk_number)
);
CREATE INDEX IF NOT EXISTS items_embedding_ivf_cos
ON items USING ivfflat (embedding vector_cosine_ops) WITH (lists=100);
"""
with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
    with conn.cursor() as cur:
        cur.execute(DDL)               # 1) create extension + schema first
    register_vector(conn)              # 2) now the type exists; safe to register
print(":white_check_mark: DB bootstrapped: extension + schema + index ready") 