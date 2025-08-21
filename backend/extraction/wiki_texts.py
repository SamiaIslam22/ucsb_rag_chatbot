import nest_asyncio
nest_asyncio.apply()
import asyncio
import pandas as pd
from urllib.parse import unquote
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
import os

# :one: Paste your links here
wiki_links = [
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

# :sparkles: New helper function: extract title from URL
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
            print(f":x: Error scraping {url}: {e}")
            return None

# :three: Main runner: loop through all links
async def run_all_scrapes(urls):
    results = []
    for i, url in enumerate(urls):
        print(f":rocket: Scraping ({i+1}/{len(urls)}): {url}")
        result = await scrape(url)
        if result:
            results.append(result)
    return results

# :four: Entry point
if __name__ == "__main__":
    scraped_data = asyncio.run(run_all_scrapes(wiki_links))
    df = pd.DataFrame(scraped_data)
    
    # :file_folder: Save to csv_dataframes/raw/ folder
    output_path = "csv_dataframes/raw/wiki_texts.csv"
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the CSV
    df.to_csv(output_path, index=False)
    
    print(f"\n:white_check_mark: CSV saved as {output_path}")
    print(df.head())