import pandas as pd
import json
import re
import numpy as np
from vector_search import embed_query, client

# -- Helper: cosine similarity between two vectors
def cosine_similarity(a: list, b: list) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# -- Hybrid search function combining keyword and semantic scores
def hybrid_search(
    query: str,
    df: pd.DataFrame,
    keyword_weight: float = 0.5,
    k: int = 5
) -> pd.DataFrame:
    """
    Perform hybrid semantic + keyword search over pre-embedded chunks.

    Args:
        query: The user's natural-language question.
        df: DataFrame with columns ['content','embedding_vectors',...].
        keyword_weight: Weight [0.0-1.0] for keyword vs. semantic.
        k: Number of top results to return.

    Returns:
        DataFrame of top-k rows sorted by hybrid_score.
    """
    # 1) Keyword overlap score
    keywords = set(re.findall(r"\w+", query.lower()))
    if keywords:
        df = df.copy()
        df['kw_score'] = df['content'].apply(
            lambda txt: len(keywords & set(re.findall(r"\w+", txt.lower()))) / len(keywords)
        )
    else:
        df = df.copy()
        df['kw_score'] = 0.0

    # 2) Pre-filter: keep chunks with any keyword match
    filtered = df[df['kw_score'] > 0].copy()
    if filtered.empty:
        filtered = df.copy()
        filtered['kw_score'] = 0.0

    # 3) Embed the query once
    q_emb = embed_query(query, client)

    # 4) Semantic similarity score
    filtered['sem_score'] = filtered['embedding_vectors'].apply(
        lambda vec: cosine_similarity(q_emb, vec)
    )

    # 5) Combined hybrid score
    alpha = 1 - keyword_weight
    filtered['hybrid_score'] = (
        alpha * filtered['sem_score'] + keyword_weight * filtered['kw_score']
    )

    # 6) Return top-k results
    return filtered.sort_values('hybrid_score', ascending=False).head(k)

def run_hybrid(
    query: str,
    csv_path: str = 'chunked_pages_with_embeddings.csv',
    keyword_weight: float = 0.5,
    k: int = 5
):
    """
    Load data, perform hybrid search, and print results for interactive sessions.
    """
    # Load pre-embedded chunks
    df = pd.read_csv(csv_path, encoding='utf-8')
    df['embedding_vectors'] = df['vectors'].apply(lambda s: json.loads(s))

    # Run the search
    results = hybrid_search(query, df, keyword_weight=keyword_weight, k=k)

    # Display
    for rank, row in results.reset_index(drop=True).iterrows():
        print(f"{rank+1}. score={row['hybrid_score']:.3f} | chunk_number={row['chunk_number']}")
        snippet = row['content'].replace('\n', ' ')[:200]
        print(f"   {snippet}...\n")

    return results

results = run_hybrid("What is the step 1 of autostep200 masking guidance", keyword_weight=0.3, k=3)

query= "What is the main idea of the document?"
# Inspect the returned answers
print(results[['content','hybrid_score']])

set(re.findall(r"\w+", query.lower()))
