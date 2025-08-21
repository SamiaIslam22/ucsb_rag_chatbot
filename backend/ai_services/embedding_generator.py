# embedding_generator.py
import pandas as pd
import json
import time
import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def embed_chunks_with_openai(chunks_df, client):
    """Generate embeddings for existing chunks"""
    
    embedded_chunks = []
    
    for index, row in chunks_df.iterrows():
        print(f"Processing chunk {index + 1}/{len(chunks_df)}")
        
        try:
            response = client.embeddings.create(
                input=row['content'],
                model="text-embedding-3-small"
            )
            
            # Get the embedding vector
            embedding_vector = response.data[0].embedding
            
            # Create metadata dictionary
            metadata = {
                'url': row['url'],
                'title': row['title'],
                'chunk_number': row['chunk_number'],
                'total_chunks': row['total_chunks'],
                'character_count': row['character_count']
            }
            
            # Add content_type to metadata if it exists
            if 'content_type' in row:
                metadata['content_type'] = row['content_type']
            
            # Add data with metadata structure
            chunk_data = {
                'url': row['url'],
                'title': row['title'],
                'content': row['content'],
                'chunk_number': row['chunk_number'],
                'total_chunks': row['total_chunks'],
                'character_count': row['character_count'],
                'metadata': json.dumps(metadata, separators=(',', ':')),
                'vectors': json.dumps(embedding_vector, separators=(',', ':'))
            }
            
            # Add content_type if it exists
            if 'content_type' in row:
                chunk_data['content_type'] = row['content_type']
                
            embedded_chunks.append(chunk_data)
            
            # Small delay to respect rate limits
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error processing chunk {index + 1}: {e}")
            chunk_data = {
                'url': row['url'],
                'title': row['title'], 
                'content': row['content'],
                'chunk_number': row['chunk_number'],
                'character_count': row['character_count'],
                'metadata': json.dumps({'url': row['url'], 'title': row['title']}),
                'vectors': None
            }
            
            # Add content_type and total_chunks if they exist
            if 'content_type' in row:
                chunk_data['content_type'] = row['content_type']
            if 'total_chunks' in row:
                chunk_data['total_chunks'] = row['total_chunks']
                
            embedded_chunks.append(chunk_data)
    
    return pd.DataFrame(embedded_chunks)

print("Loading chunks from processed/chunked_pages.csv...")
input_path = "csv_dataframes/processed/chunked_pages.csv"

try:
    chunks_df = pd.read_csv(input_path)
    print(f"Found {len(chunks_df)} chunks to embed")
    
    # Show breakdown by content type if available
    if 'content_type' in chunks_df.columns:
        content_type_counts = chunks_df['content_type'].value_counts()
        print("Content type breakdown:")
        for content_type, count in content_type_counts.items():
            print(f"  - {content_type}: {count} chunks")
    
    # Generate embeddings
    embedded_df = embed_chunks_with_openai(chunks_df, client)
    
    # Save to embeddings folder
    output_path = "csv_dataframes/embeddings/chunked_pages_with_embeddings.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    embedded_df.to_csv(output_path, index=False)
    
    print(f"✅ Embeddings generated and saved to '{output_path}'!")
    print(f"Generated embeddings for {len(embedded_df)} chunks")
    
    # Show summary
    print(f"\nSummary:")
    print(f"- Total chunks: {len(embedded_df)}")
    print(f"- Average content length: {embedded_df['character_count'].mean():.0f} characters")
    
    # Show breakdown by content type if available
    if 'content_type' in embedded_df.columns:
        content_type_counts = embedded_df['content_type'].value_counts()
        print("Final content type breakdown:")
        for content_type, count in content_type_counts.items():
            print(f"  - {content_type}: {count} chunks")

except FileNotFoundError:
    print(f"Error: Could not find {input_path}")
    print("Make sure you've run the chunking script first to create the chunked_pages.csv file")
except Exception as e:
    print(f"Error: {e}")