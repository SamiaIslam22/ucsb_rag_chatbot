import pandas as pd
import numpy as np
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def cosine_similarity_openai(query_vector, chunk_vectors):
    """Calculate cosine similarity - OpenAI embeddings are pre-normalized"""
    return np.dot(chunk_vectors, query_vector)

def vector_similarity_search(query_text, df, client, k=5):
    """Find most similar chunks to the query with enhanced content type info"""
    
    # Embed the query
    query_embedding = embed_query(query_text, client)
    if query_embedding is None:
        return []
    
    # Calculate similarities with all chunks
    similarities = []
    for idx, row in df.iterrows():
        chunk_embedding = row['embedding_vectors']
        if chunk_embedding:
            similarity = cosine_similarity_openai(query_embedding, chunk_embedding)
            
            # Create enhanced row data with content type information
            enhanced_row = row.to_dict()
            
            # Ensure content_type exists
            if 'content_type' not in enhanced_row or pd.isna(enhanced_row['content_type']):
                # Try to infer content type from other fields
                if 'table' in str(enhanced_row.get('title', '')).lower():
                    enhanced_row['content_type'] = 'table'
                elif any(keyword in str(enhanced_row.get('content', '')) for keyword in ['{', '}', ':', '"']):
                    # Looks like JSON - probably a table row
                    enhanced_row['content_type'] = 'table_row'
                else:
                    enhanced_row['content_type'] = 'text'
            
            similarities.append((similarity, enhanced_row))
    
    # Sort by similarity (highest first) and return top k
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    print(f"Found {len(similarities)} chunks, returning top {k}")
    for i, (score, chunk) in enumerate(similarities[:k], 1):
        content_type = chunk.get('content_type', 'unknown')
        print(f"  {i}. Score: {score:.3f} | Type: {content_type} | {chunk['title'][:50]}...")
    
    return similarities[:k]

def embed_query(query_text, client):
    """Generate embedding for user query"""
    try:
        response = client.embeddings.create(
            input=query_text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        return None

def load_chunked_data_from_csv(csv_path="csv_dataframes/embeddings/chunked_pages_with_embeddings.csv"):
    """Load chunked data with embeddings from CSV and ensure content_type is available"""
    print(f"Loading chunked data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Convert JSON string embeddings back to lists
    print("Converting embeddings from JSON...")
    df['embedding_vectors'] = df['vectors'].apply(
        lambda x: json.loads(x) if pd.notna(x) and x != 'None' else None
    )
    
    # Filter out rows without embeddings
    df_with_embeddings = df[df['embedding_vectors'].notna()].copy()
    
    # Ensure content_type column exists
    if 'content_type' not in df_with_embeddings.columns:
        print("Adding content_type column...")
        df_with_embeddings['content_type'] = 'text'  # Default to text
        
        # Try to infer content types
        for idx, row in df_with_embeddings.iterrows():
            title = str(row.get('title', '')).lower()
            content = str(row.get('content', ''))
            
            if 'table' in title and 'row' in title:
                df_with_embeddings.at[idx, 'content_type'] = 'table_row'
            elif 'table' in title:
                df_with_embeddings.at[idx, 'content_type'] = 'table'
            elif content.startswith('{') and content.endswith('}'):
                df_with_embeddings.at[idx, 'content_type'] = 'table_row'
    
    print(f"Loaded {len(df_with_embeddings)} chunks with embeddings")
    
    # Show content type distribution
    if 'content_type' in df_with_embeddings.columns:
        type_counts = df_with_embeddings['content_type'].value_counts()
        print("Content type distribution:")
        for content_type, count in type_counts.items():
            print(f"  - {content_type}: {count}")
    
    return df_with_embeddings