import os
from dotenv import load_dotenv
import psycopg
from pgvector.psycopg import register_vector
from openai import OpenAI
load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY_DEV"))
EMBED_MODEL = "text-embedding-3-small"  # 1536-dim
def embed(text: str):
    e = client.embeddings.create(model=EMBED_MODEL, input=text)
    return e.data[0].embedding
def search(query: str, k: int = 5, content_type: str | None = None):
    qvec = embed(query)
    sql = """
    SELECT id, url, title, content_type, left(content, 240) AS snippet,
           1 - (embedding <=> %s::vector) AS score
    FROM items
    {where}
    ORDER BY embedding <-> %s::vector
    LIMIT %s;
    """.format(where="WHERE content_type = %s" if content_type else "")
    with psycopg.connect(DATABASE_URL) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            params = ([qvec] + ([content_type] if content_type else []) + [qvec, k]) \
                     if content_type else ([qvec, qvec, k])
            cur.execute(sql, params)
            return cur.fetchall()
if __name__ == "__main__":
    rows = search("vernier alignment mark", k=5, content_type="text")
    for r in rows:
        _id, url, title, ctype, snip, score = r
        print(f"{score:.3f} | {ctype:5} | {title or ''}")
        print(f"  {url}")
        print(f"  {snip}…\n")