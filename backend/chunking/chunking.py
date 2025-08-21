from langchain_text_splitters import CharacterTextSplitter
import pandas as pd
import json
import re
import os

# Initialize text splitter for regular text content
text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=1000,
    chunk_overlap=2,
    length_function=len,
    is_separator_regex=False,
)

def parse_table_to_rows(table_markdown):
    """
    Parse markdown table with [LINEBREAK] markers to extract headers and rows
    Handles both simple tables and multi-level header tables
    Returns: (headers, rows) where rows is list of dictionaries
    """
    if not table_markdown or table_markdown.strip() == "":
        return [], []
    
    # Replace [LINEBREAK] with actual newlines
    content = table_markdown.replace(' [LINEBREAK] ', '\n').replace('[LINEBREAK]', '\n')
    
    # Split into lines and clean
    lines = content.strip().split('\n')
    
    # Find lines that look like table rows
    table_lines = []
    for line in lines:
        line = line.strip()
        if '|' in line and line.count('|') >= 2:  # Must have at least 2 pipes
            # Skip separator lines (like |:---|:---|)
            if not re.match(r'^\|[\s\-\|:]+\|?$', line):
                table_lines.append(line)
    
    if len(table_lines) < 2:  # Need at least 2 rows
        return [], []
    
    # Strategy 1: Look for a row that contains common header indicators
    header_indicators = ['material', 'authors', 'title', 'name', 'type', 'item', 'description']
    header_row_index = None
    
    for i, line in enumerate(table_lines):
        line_lower = line.lower()
        if any(indicator in line_lower for indicator in header_indicators):
            header_row_index = i
            break
    
    # Strategy 2: If no clear header indicators, check for numeric headers (0, 1, 2)
    if header_row_index is None:
        first_line = table_lines[0]
        first_line_clean = first_line.strip().strip('|')
        first_cells = [col.strip() for col in first_line_clean.split('|')]
        first_cells = [cell for cell in first_cells if cell]  # Remove empty cells
        
        # Check if first row has numeric headers
        if len(first_cells) >= 2 and all(cell.isdigit() for cell in first_cells):
            # Use second row as headers (skip numeric row)
            header_row_index = 1
        else:
            # Use first row as headers
            header_row_index = 0
    
    # Extract headers from the identified row
    if header_row_index >= len(table_lines):
        return [], []
        
    header_line = table_lines[header_row_index]
    header_line = header_line.strip().strip('|')
    headers = [col.strip() for col in header_line.split('|')]
    headers = [h for h in headers if h]  # Remove empty headers
    
    if not headers:
        return [], []
    
    # For multi-level headers, combine with previous row if it exists and isn't numeric
    if header_row_index > 0:
        prev_line = table_lines[header_row_index - 1]
        prev_line_clean = prev_line.strip().strip('|')
        prev_cells = [col.strip() for col in prev_line_clean.split('|')]
        prev_cells = [cell for cell in prev_cells if cell]
        
        # Check if previous row could be category headers (not numeric and not separator)
        if (len(prev_cells) > 0 and 
            not all(cell.isdigit() for cell in prev_cells) and
            not re.match(r'^[\s\-\|:]+$', prev_line_clean)):
            
            # Try to combine category headers with sub-headers
            enhanced_headers = []
            prev_index = 0
            
            for i, header in enumerate(headers):
                if prev_index < len(prev_cells) and prev_cells[prev_index]:
                    # Combine category with sub-header if both exist
                    if header and header != prev_cells[prev_index]:
                        enhanced_header = f"{prev_cells[prev_index]} - {header}"
                    else:
                        enhanced_header = prev_cells[prev_index] or header
                else:
                    enhanced_header = header
                
                enhanced_headers.append(enhanced_header)
                
                # Move to next category header when we've processed its sub-headers
                # This is a simple heuristic - you might need to adjust based on your table structure
                if i < len(headers) - 1:
                    next_header = headers[i + 1]
                    if prev_index + 1 < len(prev_cells) and prev_cells[prev_index + 1]:
                        # Check if we should move to next category
                        if not next_header or len(next_header.strip()) == 0:
                            prev_index += 1
            
            headers = enhanced_headers
    
    # Process data rows (start after header row)
    data_start_index = header_row_index + 1
    rows = []
    
    for line in table_lines[data_start_index:]:
        line = line.strip().strip('|')
        cells = [col.strip() for col in line.split('|')]
        
        # Only process rows that have the same number of columns as headers
        if len(cells) == len(headers):
            # Create dictionary with proper header names as keys
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(cells):
                    row_dict[header] = cells[i]
                else:
                    row_dict[header] = ""  # Empty cell
            rows.append(row_dict)
        elif len(cells) > 0:  # Handle rows with different column counts
            # Pad with empty strings or truncate to match header count
            while len(cells) < len(headers):
                cells.append("")
            cells = cells[:len(headers)]
            
            row_dict = {}
            for i, header in enumerate(headers):
                row_dict[header] = cells[i] if i < len(cells) else ""
            rows.append(row_dict)
    
    return headers, rows

def create_row_chunks(rows, table_metadata):
    """
    Convert table rows to individual chunks with meaningful column names
    Returns: list of chunk dictionaries
    """
    row_chunks = []
    
    for row_idx, row_dict in enumerate(rows, 1):
        # Ensure we have meaningful keys, not just numbers
        if not row_dict or all(isinstance(k, (int, str)) and str(k).isdigit() for k in row_dict.keys()):
            print(f"Warning: Row {row_idx} has numeric keys, skipping")
            continue
            
        # Convert row dictionary to JSON string with proper column names
        row_json = json.dumps(row_dict, separators=(',', ':'), ensure_ascii=False)
        
        # Create chunk for this row
        chunk_data = {
            "url": table_metadata['url'],
            "title": f"{table_metadata['title']} - Row {row_idx}",
            "content": row_json,
            "chunk_number": row_idx,
            "total_chunks": len(rows),
            "character_count": len(row_json),
            "content_type": "table_row"
        }
        row_chunks.append(chunk_data)
    
    return row_chunks

# List to store all chunk data (text, tables, and images)
all_chunks = []

print("=== Processing Text Content ===")
# Read the text CSV file from raw folder
print("Loading text CSV...")
try:
    text_df = pd.read_csv("csv_dataframes/raw/wiki_texts.csv", encoding='utf-8')
    print(f"Found {len(text_df)} pages to process")
    
    # Process each row in the text CSV
    for index, row in text_df.iterrows():
        print(f"Processing page {index + 1}/{len(text_df)}: {row['title'][:50]}..." )
        
        url = row["url"]
        title = row["title"]
        content = row["markdown"]
        
        # Split content into chunks
        texts = text_splitter.create_documents([content])
        print(f"  Created {len(texts)} text chunks")
        
        # Collect chunk data
        for chunk_num, text in enumerate(texts, 1):
            chunk_data = {
                "url": url,
                "title": title,
                "content": text.page_content,
                "chunk_number": chunk_num,
                "total_chunks": len(texts),
                "character_count": len(text.page_content),
                "content_type": "text"
            }
            all_chunks.append(chunk_data)
            
except FileNotFoundError:
    print("Text CSV file not found, skipping text processing...")
except Exception as e:
    print(f"Error processing text: {e}")

print("\n=== Processing Tables ===")
# Read the tables CSV file from raw folder
print("Loading tables CSV...")
try:
    tables_df = pd.read_csv("csv_dataframes/raw/wiki_tables.csv", encoding='utf-8')
    print(f"Found {len(tables_df)} table entries to process")
    
    # Process each table entry
    for index, row in tables_df.iterrows():
        print(f"Processing table entry {index + 1}/{len(tables_df)}: {row['page_name']}")
        
        # Skip entries that don't have tables
        if row['has_tables'] == 'no' or row['has_tables'] == 'error':
            print(f"  Skipping - no tables or error")
            continue
            
        url = row["page_url"]
        page_name = row["page_name"]
        table_number = row["table_number"]
        table_content = row["tables_markdown"]
        
        # Create title for the table chunk
        title = f"{page_name} - {table_number}"
        
        # APPROACH 1: Complete table chunk 
        complete_table_chunk = {
            "url": url,
            "title": title,
            "content": table_content,
            "chunk_number": 1,
            "total_chunks": 1,
            "character_count": len(table_content),
            "content_type": "table"
        }
        all_chunks.append(complete_table_chunk)
        print(f"  Created 1 complete table chunk")
        
        # APPROACH 2: Individual row chunks 
        try:
            headers, rows = parse_table_to_rows(table_content)
            
            if len(rows) > 0:
                print(f"  Detected headers: {headers[:3]}{'...' if len(headers) > 3 else ''}")
                table_metadata = {
                    'url': url,
                    'title': title
                }
                row_chunks = create_row_chunks(rows, table_metadata)
                all_chunks.extend(row_chunks)
                print(f"  Created {len(row_chunks)} individual row chunks")
            else:
                print(f"  No parseable rows found in table")
                
        except Exception as e:
            print(f"  Error parsing table rows: {e}")
            
except FileNotFoundError:
    print("Tables CSV file not found, skipping table processing...")
except Exception as e:
    print(f"Error processing tables: {e}")

print("\n=== Processing Images ===")
# Read the images CSV file from raw folder
print("Loading images CSV...")
try:
    images_df = pd.read_csv("csv_dataframes/raw/wiki_images.csv", encoding='utf-8')
    print(f"Found {len(images_df)} images to process")
    
    # Process each image entry
    for index, row in images_df.iterrows():
        print(f"Processing image {index + 1}/{len(images_df)}: {row['url']}")
        
        # Create image chunk
        image_chunk = {
            "url": row["url"],
            "title": f"Image {row['index']}: {row.get('alt', 'No alt text')}",
            "content": f"Image: {row.get('alt', '')} | Caption: {row.get('caption', '')} | Summary: {row.get('summary', '')}",
            "chunk_number": 1,
            "total_chunks": 1,
            "character_count": len(row.get('summary', '')),
            "content_type": "image"
        }
        all_chunks.append(image_chunk)
        print(f"  Created 1 image chunk")
        
except FileNotFoundError:
    print("Images CSV file not found, skipping image processing...")
except Exception as e:
    print(f"Error processing images: {e}")

# Create DataFrame and save to processed folder
print("\n=== Combining and Saving ===")
print("Creating DataFrame...")
chunks_df = pd.DataFrame(all_chunks)

# Count different types of chunks
text_chunks = len(chunks_df[chunks_df['content_type'] == 'text']) if 'content_type' in chunks_df.columns else 0
table_chunks = len(chunks_df[chunks_df['content_type'] == 'table']) if 'content_type' in chunks_df.columns else 0
table_row_chunks = len(chunks_df[chunks_df['content_type'] == 'table_row']) if 'content_type' in chunks_df.columns else 0
image_chunks = len(chunks_df[chunks_df['content_type'] == 'image']) if 'content_type' in chunks_df.columns else 0

print(f"Total chunks created: {len(chunks_df)}")
print(f"  - Text chunks: {text_chunks}")
print(f"  - Complete table chunks: {table_chunks}")
print(f"  - Table row chunks: {table_row_chunks}")
print(f"  - Image chunks: {image_chunks}")

# Save to processed folder
output_path = "csv_dataframes/processed/chunked_pages.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

print("Saving to CSV...")
chunks_df.to_csv(output_path, index=False)

# Display sample
print("\nSample of chunk types:")
if not chunks_df.empty and 'content_type' in chunks_df.columns:
    # Show one of each type
    for content_type in ['text', 'table', 'table_row', 'image']:
        sample_chunks = chunks_df[chunks_df['content_type'] == content_type]
        if not sample_chunks.empty:
            sample = sample_chunks.iloc[0]
            print(f"\n{content_type.upper()} chunk example:")
            print(f"  Title: {sample['title'][:50]}...")
            print(f"  Content length: {sample['character_count']} characters")
            print(f"  Content preview: {sample['content'][:100]}...")

print(f"\n✅ Processing complete! All chunks saved to '{output_path}'")