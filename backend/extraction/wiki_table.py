import logging
import time
from pathlib import Path
import pandas as pd
import re
import csv
import os
from docling.document_converter import DocumentConverter

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

def load_wiki_urls_from_csv():
    """Load wiki URLs from the generated CSV file."""
    csv_path = "csv_dataframes/raw/wiki_all_page_links.csv"
    
    # Check if the CSV exists
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        print("📋 Run wiki_all_pages_links.py first to generate the URLs")
        
        # Fallback to manual links if CSV doesn't exist
        fallback_links = [
            "https://wiki.nanofab.ucsb.edu/wiki/ADT_UV-Tape_Table_1042R",
            "https://wiki.nanofab.ucsb.edu/wiki/LegacyTable",
            "https://wiki.nanofab.ucsb.edu/wiki/Stepper_2_(Autostep_200)_-_Table_of_Chucks,_Shims,_Target_Thicknesses",
            "https://wiki.nanofab.ucsb.edu/wiki/Ovens_-_Overview_of_All_Lab_Ovens",
            "https://wiki.nanofab.ucsb.edu/wiki/Lift-Off_with_DUV_Imaging_%2B_PMGI_Underlayer",
            "https://wiki.nanofab.ucsb.edu/wiki/Lithography_Recipes",
            "https://wiki.nanofab.ucsb.edu/wiki/PubList2018",
            "https://wiki.nanofab.ucsb.edu/wiki/Stocked_Chemical_List",
            "https://wiki.nanofab.ucsb.edu/wiki/Staff_List",
            "https://wiki.nanofab.ucsb.edu/wiki/Dry_Etching_Recipes"
        ]
        print(f"🔄 Using fallback links: {len(fallback_links)} URLs")
        return fallback_links
    
    try:
        # Load the CSV
        df = pd.read_csv(csv_path)
        urls = df['url'].tolist()
        print(f"✅ Loaded {len(urls)} URLs from {csv_path}")
        return urls
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []

def clean_for_ai_csv(df):
    df_clean = df.copy()
    df_clean = df_clean.fillna('')
    
    cleaned_columns = []
    for col in df_clean.columns:
        clean_col = re.sub(r'[^\w\s]', '_', str(col)).strip().replace(' ', '_').lower()
        if 'dry_etching' in clean_col or 'dry_etch' in clean_col:
            clean_col = 'dry_etching'
        cleaned_columns.append(clean_col)
    
    df_clean.columns = cleaned_columns
    
    cols = pd.Series(df_clean.columns)
    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
    df_clean.columns = cols
    
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].astype(str)
            df_clean[col] = df_clean[col].str.replace('\r', '', regex=False)
            df_clean[col] = df_clean[col].str.replace('\t', ' ', regex=False)
            df_clean[col] = df_clean[col].str.strip()
            df_clean[col] = df_clean[col].str.replace(r'\s+', ' ', regex=True)
    
    return df_clean

def table_to_markdown(table):
    table_df_clean = clean_for_ai_csv(table.export_to_dataframe())
    table_markdown = table_df_clean.to_markdown(index=False)
    return table_markdown

def ultra_clean_text_for_csv(text_content):
    if not text_content:
        return ""
    
    cleaned = str(text_content)
    
    cleaned = cleaned.replace('\r\n', '\n')
    cleaned = cleaned.replace('\r', '\n')
    cleaned = cleaned.replace('\n', ' [LINEBREAK] ')
    
    cleaned = cleaned.replace('"', '""')
    cleaned = cleaned.replace("'", "''")
    
    if '|' not in cleaned:
        cleaned = cleaned.replace(',', ';')
    else:
        parts = cleaned.split('|')
        for i, part in enumerate(parts):
            if not any(keyword in part.lower() for keyword in ['table', 'header', '---', '--']):
                parts[i] = part.replace(',', ';')
        cleaned = '|'.join(parts)
    
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', ' ', cleaned)
    cleaned = cleaned.replace('\t', ' [TAB] ')
    cleaned = re.sub(r' +', ' ', cleaned)
    cleaned = cleaned.strip()
    
    max_length = 32000
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length] + ' [TRUNCATED]'
    
    return cleaned

def get_page_name_from_url(url):
    page_name = url.split('/')[-1]
    page_name = re.sub(r'[^\w\s-]', '_', page_name)
    return page_name

def main():
    """Main function to extract tables from all wiki URLs"""
    print("🔍 Starting UCSB Wiki Table Extraction...")
    
    # Load URLs from CSV
    input_urls = load_wiki_urls_from_csv()
    
    if not input_urls:
        print("❌ No URLs found to process!")
        return
    
    # Create output directories
    output_dir = Path("csv_dataframes/raw/scratch")
    output_dir.mkdir(parents=True, exist_ok=True)

    doc_converter = DocumentConverter()
    start_time = time.time()
    all_table_rows = []

    print(f"📊 Processing {len(input_urls)} URLs for table extraction...")

    for url_index, input_doc_path in enumerate(input_urls):
        print(f"\n🔄 Processing URL {url_index + 1}/{len(input_urls)}: {input_doc_path}")
        
        try:
            conv_res = doc_converter.convert(input_doc_path)
            tables_count = len(conv_res.document.tables)
            has_tables = "yes" if tables_count > 0 else "no"
            page_name = get_page_name_from_url(input_doc_path)
            
            if tables_count > 0:
                print(f"📋 Found {tables_count} table(s) on {page_name}")
                for table_idx, table in enumerate(conv_res.document.tables):
                    try:
                        raw_markdown = table_to_markdown(table)
                    except Exception as e:
                        raw_markdown = f"Error converting table: {str(e)}"
                        print(f"⚠️ Error converting table {table_idx + 1}: {e}")
                    
                    md_filename = output_dir / f"{page_name}_table_{table_idx + 1}.md"
                    try:
                        with open(md_filename, 'w', encoding='utf-8') as f:
                            f.write(f"# {page_name} - Table {table_idx + 1}\n\n")
                            f.write(f"Source: {input_doc_path}\n\n")
                            f.write(raw_markdown)
                        print(f"💾 Saved table to: {md_filename}")
                    except Exception as e:
                        print(f"⚠️ Error saving table file: {e}")
                    
                    cleaned_markdown = ultra_clean_text_for_csv(raw_markdown)
                    
                    table_row = {
                        'page_url': input_doc_path,
                        'page_name': page_name,
                        'has_tables': has_tables,
                        'table_number': f"table_{table_idx + 1}",
                        'tables_markdown': cleaned_markdown
                    }
                    all_table_rows.append(table_row)
            else:
                print(f"📋 No tables found on {page_name}")
                table_row = {
                    'page_url': input_doc_path,
                    'page_name': page_name,
                    'has_tables': has_tables,
                    'table_number': "no_tables",
                    'tables_markdown': ""
                }
                all_table_rows.append(table_row)

        except Exception as e:
            print(f"❌ Error processing {input_doc_path}: {e}")
            page_name = get_page_name_from_url(input_doc_path)
            error_row = {
                'page_url': input_doc_path,
                'page_name': page_name,
                'has_tables': 'error',
                'table_number': 'error',
                'tables_markdown': f"Error: {str(e)}"
            }
            all_table_rows.append(error_row)

    # Save to csv_dataframes/raw/ folder
    output_filename = "csv_dataframes/raw/wiki_tables.csv"

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    if not all_table_rows:
        print("⚠️ No table data to save, creating empty CSV...")
        df_final = pd.DataFrame(columns=['page_url', 'page_name', 'has_tables', 'table_number', 'tables_markdown'])
    else:
        df_final = pd.DataFrame(all_table_rows)

        for col in df_final.columns:
            if df_final[col].dtype == 'object':
                df_final[col] = df_final[col].astype(str)
                df_final[col] = df_final[col].str.replace(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', ' ', regex=True)
                df_final[col] = df_final[col].str.strip()

    try:
        df_final.to_csv(
            output_filename,
            index=False,
            encoding='utf-8',
            quoting=csv.QUOTE_ALL,
            escapechar='\\',
            doublequote=True,
            lineterminator='\n'
        )
        print("✅ CSV created successfully")
    except Exception as e:
        print(f"Primary method failed: {e}")
        try:
            with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['page_url', 'page_name', 'has_tables', 'table_number', 'tables_markdown']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                for row in all_table_rows:
                    clean_row = {key: ultra_clean_text_for_csv(str(value)) for key, value in row.items()}
                    writer.writerow(clean_row)
            print("✅ CSV created with fallback method")
        except Exception as e2:
            print(f"❌ Both CSV methods failed: {e2}")
            # Create minimal CSV so pipeline doesn't fail
            with open(output_filename, 'w') as f:
                f.write("page_url,page_name,has_tables,table_number,tables_markdown\n")
            print("🔄 Created minimal CSV to continue pipeline")

    end_time = time.time() - start_time
    
    # Count successful table extractions
    successful_tables = len([row for row in all_table_rows if row.get('table_number', '') not in ['no_tables', 'error', '']])
    
    print(f"\n✅ Table extraction completed!")
    print(f"⏱️ Processing time: {end_time:.2f} seconds")
    print(f"📊 URLs processed: {len(input_urls)}")
    print(f"📋 Tables extracted: {successful_tables}")
    print(f"📁 Individual table files: {output_dir}")
    print(f"📄 Main CSV: {output_filename}")

    # Verify the output file exists and has content
    if os.path.exists(output_filename):
        try:
            verify_df = pd.read_csv(output_filename)
            print(f"✅ Output file verified: {len(verify_df)} rows")
        except Exception as e:
            print(f"⚠️ Output file verification failed: {e}")
    else:
        print(f"❌ Output file not created: {output_filename}")

    _log.info("Table extraction complete")

if __name__ == "__main__":
    main()