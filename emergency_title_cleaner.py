# emergency_title_cleaner.py
# Run this if you want to clean existing data without regenerating embeddings

import pandas as pd
import re
import json
import os

def ultra_aggressive_title_cleaning(title):
    """Ultra-aggressive title cleaning to remove all key artifacts"""
    if pd.isna(title) or title is None:
        return "Unknown Page"
    
    clean_title = str(title)
    
    # Remove ALL key-related artifacts (most aggressive patterns first)
    patterns_to_remove = [
        r'key[🔓🔒🔑].*?-',              # key + emoji + anything + dash
        r'key\w*[🔓🔒🔑].*?-',           # key + word + emoji + anything + dash
        r'key\w+-\w*-?',                 # key + word + dash + word + optional dash
        r'key\w*-.*?-',                  # key + anything + dash + anything + dash
        r'^[a-zA-Z]*[🔓🔒🔑].*?-',       # start + any letters + emoji + anything + dash
        r'^[🔓🔒🔑].*?-',                # start + emoji + anything + dash
        r'[🔓🔒🔑].*?-',                 # any emoji + anything + dash
        r'^key.*?-',                     # start + key + anything + dash
        r'key\w*',                       # any remaining "key" + letters
        r'^[a-zA-Z]{1,4}[🔓🔒🔑]',       # short letters + emoji at start
        r'^\w{1,6}_.*?_',                # short word + underscore + anything + underscore at start
    ]
    
    # Apply all removal patterns
    for pattern in patterns_to_remove:
        clean_title = re.sub(pattern, '', clean_title, flags=re.IGNORECASE)
    
    # Clean up formatting artifacts
    clean_title = clean_title.replace('_', ' ')
    clean_title = clean_title.replace('-', ' ')
    clean_title = clean_title.replace('  ', ' ')  # double spaces
    clean_title = re.sub(r'\s+', ' ', clean_title)  # multiple spaces to single
    clean_title = clean_title.strip()
    
    # Remove any remaining special characters at the start
    clean_title = re.sub(r'^[^a-zA-Z0-9]+', '', clean_title)
    
    # If title is still empty, too short, or contains artifacts
    if not clean_title or len(clean_title) < 3 or any(bad in clean_title.lower() for bad in ['key', '🔓', '🔒', '🔑']):
        return "Wiki Page Content"
    
    # Capitalize first letter of each word for better presentation
    clean_title = ' '.join(word.capitalize() for word in clean_title.split())
    
    # Limit length
    if len(clean_title) > 60:
        clean_title = clean_title[:60] + "..."
    
    return clean_title

def extract_title_from_url(url):
    """Extract a clean title from URL as fallback"""
    if not url:
        return "Unknown Source"
    
    try:
        # Get the last part of the URL
        url_parts = url.split('/')
        page_name = url_parts[-1]
        
        # Clean URL encoding
        page_name = page_name.replace('%20', ' ').replace('_', ' ')
        
        # Remove common URL artifacts
        page_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', page_name)
        page_name = re.sub(r'\s+', ' ', page_name).strip()
        
        # Capitalize words
        if page_name:
            page_name = ' '.join(word.capitalize() for word in page_name.split())
            return page_name
        else:
            return "Wiki Page"
    except:
        return "Wiki Content"

def clean_embeddings_file():
    """Clean the embeddings file in place"""
    
    embeddings_path = "csv_dataframes/embeddings/chunked_pages_with_embeddings.csv"
    
    print("Loading embeddings file...")
    
    try:
        df = pd.read_csv(embeddings_path)
        print(f"Found {len(df)} rows to clean")
        
        # Create backup
        backup_path = embeddings_path.replace('.csv', '_backup.csv')
        df.to_csv(backup_path, index=False)
        print(f"Backup created at: {backup_path}")
        
        # Clean titles
        print("Cleaning titles...")
        original_titles = df['title'].tolist()
        
        # Apply ultra-aggressive cleaning
        df['title'] = df['title'].apply(ultra_aggressive_title_cleaning)
        
        # For titles that are still problematic, use URL extraction
        for idx, row in df.iterrows():
            if (not row['title'] or 
                len(row['title']) < 3 or 
                row['title'] == "Wiki Page Content" or
                any(bad in str(row['title']).lower() for bad in ['key', 'unknown'])):
                
                # Try to extract from URL
                if 'url' in row and pd.notna(row['url']):
                    df.at[idx, 'title'] = extract_title_from_url(row['url'])
                else:
                    df.at[idx, 'title'] = f"Content Item {idx + 1}"
        
        # Also clean titles in metadata if it exists
        if 'metadata' in df.columns:
            print("Cleaning metadata titles...")
            for idx, row in df.iterrows():
                if pd.notna(row['metadata']):
                    try:
                        metadata = json.loads(row['metadata'])
                        if 'title' in metadata:
                            metadata['title'] = df.at[idx, 'title']  # Use the cleaned title
                            df.at[idx, 'metadata'] = json.dumps(metadata, separators=(',', ':'))
                    except json.JSONDecodeError:
                        continue
        
        # Save cleaned file
        df.to_csv(embeddings_path, index=False)
        
        # Show cleaning results
        print(f"\n=== Cleaning Results ===")
        cleaned_count = 0
        for i, (original, cleaned) in enumerate(zip(original_titles[:10], df['title'].tolist()[:10])):
            if original != cleaned:
                print(f"Row {i}: '{original}' -> '{cleaned}'")
                cleaned_count += 1
        
        print(f"\nCleaned {cleaned_count} out of first 10 titles")
        print(f"File saved to: {embeddings_path}")
        print(f"Your frontend should now show clean titles!")
        
        return True
        
    except FileNotFoundError:
        print(f"Error: File not found at {embeddings_path}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=== Emergency Title Cleaner ===")
    print("This script will clean corrupted titles in your embeddings file.")
    print("A backup will be created automatically.")
    print()
    
    # Confirm before proceeding
    response = input("Do you want to proceed? (y/N): ")
    if response.lower() != 'y':
        print("Operation cancelled.")
        exit()
    
    # Change to project root if needed
    if not os.path.exists("csv_dataframes"):
        print("Changing to parent directory to find csv_dataframes...")
        os.chdir("..")
        if not os.path.exists("csv_dataframes"):
            print("Error: Cannot find csv_dataframes directory")
            exit()
    
    success = clean_embeddings_file()
    
    if success:
        print("\n✅ Title cleaning completed successfully!")
        print("Try running your frontend now to see clean titles.")
    else:
        print("\n❌ Title cleaning failed!")
        print("You may need to regenerate your embeddings from scratch.")