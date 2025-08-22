import nest_asyncio
nest_asyncio.apply()
import asyncio
import pandas as pd
from urllib.parse import unquote
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
import os

def load_wiki_urls_from_csv():
    """Load wiki URLs from the generated CSV file."""
    csv_path = "csv_dataframes/raw/wiki_all_page_links.csv"
    
    # Check if the CSV exists
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        print("📋 Run wiki_all_pages_links.py first to generate the URLs")
        
        # Fallback to manual links if CSV doesn't exist
        fallback_links = [
            "https://wiki.nanofab.ucsb.edu/wiki/Wet_Benches#HF.2FTMAH_Processing_Bench",
            "https://wiki.nanofab.ucsb.edu/wiki/Autostep_200_Mask_Making_Guidance",
            "https://wiki.nanofab.ucsb.edu/wiki/Mask_Making_Guidelines_for_Contact_Aligners",
            "https://wiki.nanofab.ucsb.edu/wiki/ICP_Etch_1_(Panasonic_E646V)",
            "https://wiki.nanofab.ucsb.edu/wiki/Intellemetrics_Laser_Etch_Monitor_Procedure_for_Panasonic_ICP_Etchers",
            "https://wiki.nanofab.ucsb.edu/wiki/MLA150_-_Large_Image_GDS_Generation",
            "https://wiki.nanofab.ucsb.edu/wiki/MLA150_-_Design_Guidelines",
            "https://wiki.nanofab.ucsb.edu/wiki/GCA_6300_training_manual_-old_instructions",
            "https://wiki.nanofab.ucsb.edu/wiki/Oxford_ICP_Etcher_(PlasmaPro_100_Cobra)",
            "https://wiki.nanofab.ucsb.edu/wiki/S-Cubed_Flexi_-_Operating_Procedure"
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

# Load URLs from CSV instead of hardcoded links
wiki_links = load_wiki_urls_from_csv()

# :sparkles: Helper function: extract title from URL
def extract_title_from_url(url):
    return unquote(url.split("/wiki/")[-1].replace("_", " "))

# :two: Define scraping logic for one page
async def scrape(url):
    config = CrawlerRunConfig(
        css_selector="div#mw-content-text",
        word_count_threshold=0,
        excluded_tags=["nav", "footer", "aside"],
        exclude_external_links=True,
        exclude_social_media_links=True,
        exclude_external_images=True,
        cache_mode=CacheMode.BYPASS
    )
    async with AsyncWebCrawler() as crawler:
        try:
            result = await crawler.arun(url=url, config=config)
            # :arrows_counterclockwise: Instead of using metadata, extract title from URL
            title = extract_title_from_url(url)
            markdown = result.markdown.raw_markdown
            return {
                "title": title,
                "url": url,
                "markdown": markdown
            }
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None

# :three: Main runner: loop through all links
async def run_all_scrapes(urls=None):
    """Run scraping on provided URLs or default wiki_links"""
    if urls is None:
        urls = wiki_links
    
    if not urls:
        print("❌ No URLs to scrape!")
        return []
    
    results = []
    for i, url in enumerate(urls):
        print(f"🚀 Scraping ({i+1}/{len(urls)}): {url}")
        result = await scrape(url)
        if result:
            results.append(result)
    return results

# :four: Entry point
if __name__ == "__main__":
    print("🔍 Starting UCSB Wiki Text Extraction...")
    print(f"📋 Processing {len(wiki_links)} URLs from CSV")
    
    scraped_data = asyncio.run(run_all_scrapes(wiki_links))
    df = pd.DataFrame(scraped_data)
    
    # :file_folder: Save to csv_dataframes/raw/ folder
    output_path = "csv_dataframes/raw/wiki_texts.csv"
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the CSV
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ CSV saved as {output_path}")
    print(f"📊 Successfully extracted text from {len(df)} pages")
    print(df.head())