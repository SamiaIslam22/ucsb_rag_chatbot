import os, csv, json
from dotenv import load_dotenv
import psycopg
from pgvector.psycopg import register_vector
from psycopg.types.json import Json  # <-- wrap dicts for jsonb
load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
# Set this to your actual CSV path if needed
CSV_PATH = "chunked_pages_with_embeddings.csv"
SQL = """
INSERT INTO items
(url, title, content, chunk_number, total_chunks, character_count, metadata, content_type, embedding)
VALUES (%(url)s, %(title)s, %(content)s, %(chunk_number)s, %(total_chunks)s, %(character_count)s, %(metadata)s, %(content_type)s, %(embedding)s)
ON CONFLICT (url, chunk_number) DO UPDATE
SET title = EXCLUDED.title,
    content = EXCLUDED.content,
    total_chunks = EXCLUDED.total_chunks,
    character_count = EXCLUDED.character_count,
    metadata = EXCLUDED.metadata,
    content_type = EXCLUDED.content_type,
    embedding = EXCLUDED.embedding;
"""
def to_int(x):
    try:
        return int(x)
    except Exception:
        return None
def norm_content_type(x: str | None) -> str:
    v = (x or "").strip().lower()
    return v if v in ("text", "image", "table") else "text"
with psycopg.connect(DATABASE_URL) as conn:
    register_vector(conn)  # enables python list -> vector
    with conn.cursor() as cur, open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        n = 0
        for row in reader:
            # vectors column is a JSON array in the CSV
            emb_str = row.get("vectors")
            embedding = json.loads(emb_str) if emb_str else None
            # metadata may be JSON string or empty
            meta_str = row.get("metadata")
            if meta_str:
                try:
                    meta_obj = json.loads(meta_str)
                except Exception:
                    # store raw string if it wasn't valid JSON
                    meta_obj = {"raw": meta_str}
                metadata = Json(meta_obj)   # <-- wrap for jsonb
            else:
                metadata = None
            rec = {
                "url": row.get("url"),
                "title": row.get("title"),
                "content": row.get("content"),
                "chunk_number": to_int(row.get("chunk_number")),
                "total_chunks": to_int(row.get("total_chunks")),
                "character_count": to_int(row.get("character_count")),
                "metadata": metadata,
                "content_type": norm_content_type(row.get("content_type")),
                "embedding": embedding,  # list[float] OK with register_vector
            }
            cur.execute(SQL, rec)
            n += 1
    conn.commit()
print(":white_check_mark: Ingest complete.")