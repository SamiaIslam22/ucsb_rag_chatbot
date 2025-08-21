from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def format_chunk_for_display(chunk_row):
    """
    Format chunk content based on its type for user display
    """
    content_type = chunk_row.get('content_type', 'text')
    content = chunk_row.get('content', '')
    
    if content_type == 'table_row':
        # For table rows, parse the JSON content and format it nicely
        try:
            table_data = json.loads(content)
            formatted_content = "**Table Data:**\n"
            for key, value in table_data.items():
                if value and str(value).strip():  # Only show non-empty values
                    formatted_content += f"• **{key}**: {value}\n"
            return formatted_content
        except json.JSONDecodeError:
            return f"**Table Content:** {content}"
    
    elif content_type == 'table':
        # For complete tables, show as formatted markdown
        return f"**Complete Table:**\n```\n{content}\n```"
    
    elif content_type == 'text':
        # For text, show the actual content
        return f"**Text Content:**\n{content}"
    
    else:
        # Default case
        return content

def generate_response_with_context(user_prompt, retrieved_chunks, client):
    """
    Generate a response using OpenAI's Chat Completions API with retrieved context.
    Enhanced to handle different content types properly.

    Args:
        user_prompt: The user's question/prompt
        retrieved_chunks: List of (similarity_score, chunk_row) tuples from similarity search
        client: OpenAI client instance

    Returns:
        tuple: (response_text, enhanced_source_info_list)
    """
    if not retrieved_chunks:
        return "I couldn't find relevant information to answer your question.", []
    
    # Build context from retrieved chunks for AI
    context_parts = []
    enhanced_source_info = []
    
    for i, (score, chunk_row) in enumerate(retrieved_chunks, 1):
        # For AI context, use the raw content
        context_parts.append(f"Source {i}:\n{chunk_row['content']}\n")
        
        # For user display, create enhanced source info
        content_type = chunk_row.get('content_type', 'text')
        
        source_info = {
            'title': chunk_row['title'],
            'url': chunk_row['url'],
            'score': score,
            'chunk': chunk_row['chunk_number'],
            'content_type': content_type,
            'formatted_content': format_chunk_for_display(chunk_row),
            'raw_content': chunk_row['content']  # Keep raw content for reference
        }
        
        # Add specific handling based on content type
        if content_type == 'table_row':
            source_info['display_type'] = 'Table Row'
            source_info['icon'] = '📊'
        elif content_type == 'table':
            source_info['display_type'] = 'Complete Table'
            source_info['icon'] = '📋'
        elif content_type == 'text':
            source_info['display_type'] = 'Text Content'
            source_info['icon'] = '📄'
        else:
            source_info['display_type'] = 'Content'
            source_info['icon'] = '📝'
            
        enhanced_source_info.append(source_info)
    
    context = "\n".join(context_parts)
    
    # System prompt for RAG
    system_prompt = """You are a helpful AI assistant specializing in nanofabrication and laboratory processes. Use the provided context to answer the user's question accurately and comprehensively. 

Guidelines:
- Base your answer primarily on the provided context
- The context may include different types of information: text descriptions, table data, and technical specifications
- When referencing table data, mention specific values and parameters when relevant
- If the context doesn't contain enough information, say so
- Include relevant technical details from the context
- Be clear and concise
- When referencing information, you can mention it comes from the provided sources"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_prompt}"}
            ],
            temperature=0.1,
            max_tokens=4000
        )
        
        return response.choices[0].message.content, enhanced_source_info
        
    except Exception as e:
        return f"Error generating response: {e}", enhanced_source_info