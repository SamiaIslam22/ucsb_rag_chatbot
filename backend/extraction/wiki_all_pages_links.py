import nest_asyncio
nest_asyncio.apply()
import asyncio
import pandas as pd
import re
from urllib.parse import urljoin, unquote
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import os

# The two main AllPages URLs we want to scrape
ALLPAGES_URLS = [
    "https://wiki.nanofab.ucsb.edu/wiki/Special:AllPages",
    "https://wiki.nanofab.ucsb.edu/w/index.php?title=Special:AllPages&from=Surface+Analysis+%28KLA%2FTencor+Surfscan%29"
]

def extract_title_from_url(url):
    """Extract clean page title from wiki URL."""
    try:
        title_part = url.split("/wiki/")[-1]
        title = unquote(title_part)
        title = title.replace("_", " ")
        title = title.split('#')[0].split('?')[0]
        return title.strip()
    except Exception:
        return url

def extract_wiki_links_from_content(content, base_url):
    """Extract wiki page links from the content."""
    links = []
    
    # Look for wiki links - simple and effective patterns
    patterns = [
        r'<a[^>]+href="(/wiki/[^"]+)"[^>]*>([^<]+)</a>',
        r'href="(/wiki/[^"#\?]+)"'
    ]
    
    all_matches = []
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        all_matches.extend(matches)
    
    # Process matches
    seen_urls = set()
    for match in all_matches:
        if isinstance(match, tuple):
            url_path = match[0]
        else:
            url_path = match
            
        # Skip special pages, files, categories, and other non-content pages
        if any(skip in url_path.lower() for skip in [
            'special:', 'file:', 'category:', 'talk:', 'user:', 'help:', 
            'mediawiki:', 'template:', 'user_talk:', 'nanofab_talk:',
            'main_page', 'recent_changes', 'random_page', 'printable',
            'action=', 'oldid=', 'diff=', 'redirect='
        ]):
            continue
        
        # Skip duplicates
        if url_path in seen_urls:
            continue
        seen_urls.add(url_path)
        
        full_url = urljoin(base_url, url_path)
        title = extract_title_from_url(full_url)
        
        # Skip very short titles
        if len(title) < 2:
            continue
        
        # Skip if title is mostly numbers or special characters
        if len(re.sub(r'[^a-zA-Z]', '', title)) < 2:
            continue
        
        links.append({
            'title': title,
            'url': full_url
        })
    
    return links

async def scrape_single_allpages_url(url):
    """Scrape links from one AllPages URL."""
    print(f"🔍 Scraping: {url}")
    
    # Simple browser config
    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
        browser_type="chromium"
    )
    
    # Simple crawler config
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=0,
        excluded_tags=["script", "style"],
        exclude_external_links=False,
        wait_for="css:body",
        page_timeout=60000,  # 60 seconds
        delay_before_return_html=3.0,
        remove_overlay_elements=True
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        try:
            result = await crawler.arun(url=url, config=crawler_config)
            
            if not result.success:
                print(f"❌ Failed to scrape {url}")
                print(f"   Error: {result.error_message}")
                return []
            
            if not result.html:
                print(f"❌ No HTML content from {url}")
                return []
                
            print(f"✅ Retrieved HTML ({len(result.html):,} characters)")
            
            # Extract links
            links = extract_wiki_links_from_content(result.html, url)
            
            print(f"✅ Found {len(links)} wiki page links")
            
            # Show sample links
            if links:
                print("📋 Sample links:")
                for i, link in enumerate(links[:5], 1):
                    print(f"   {i}. {link['title']}")
                if len(links) > 5:
                    print(f"   ... and {len(links) - 5} more")
            
            return links
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return []

async def get_all_wiki_page_links():
    """Get all wiki page links from the two main AllPages URLs."""
    print("🚀 Starting UCSB Wiki page discovery...")
    print(f"📋 Will scrape {len(ALLPAGES_URLS)} AllPages URLs")
    
    all_links = []
    
    # Scrape each URL
    for i, url in enumerate(ALLPAGES_URLS, 1):
        print(f"\n📄 Processing URL {i}/{len(ALLPAGES_URLS)}")
        links = await scrape_single_allpages_url(url)
        all_links.extend(links)
        
        # Small delay between requests
        if i < len(ALLPAGES_URLS):
            print("⏸️ Waiting 2 seconds...")
            await asyncio.sleep(2)
    
    # Remove duplicates
    print(f"\n🔄 Removing duplicates...")
    print(f"   Raw links found: {len(all_links)}")
    
    seen_urls = set()
    unique_links = []
    
    for link in all_links:
        if link['url'] not in seen_urls:
            seen_urls.add(link['url'])
            unique_links.append(link)
    
    print(f"   Unique links: {len(unique_links)}")
    
    # Sort by title
    if unique_links:
        unique_links.sort(key=lambda x: x['title'].lower())
    
    return unique_links

async def main():
    """Main function to extract all wiki page links and save to CSV."""
    
    try:
        # Get all links from the two URLs
        links = await get_all_wiki_page_links()
        
        if not links:
            print("❌ No links found!")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(links)
        
        # Create output directory
        output_path = "csv_dataframes/raw/wiki_all_page_links.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        
        print(f"\n✅ SUCCESS!")
        print(f"📄 Saved {len(df)} wiki pages to: {output_path}")
        print(f"\n📊 Summary:")
        print(f"   Total pages discovered: {len(df)}")
        print(f"   Output file: {output_path}")
        
        print(f"\n📋 Sample of discovered pages:")
        for i, row in df.head(10).iterrows():
            print(f"   {i+1:2d}. {row['title']}")
        
        if len(df) > 10:
            print(f"   ... and {len(df) - 10} more pages")
        
        print(f"\n🚀 Next step: Run the main pipeline")
        print(f"   cd backend/")
        print(f"   python main.py")
        
        return df
        
    except Exception as e:
        print(f"❌ Error in main(): {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(main())
    if result is not None:
        print(f"\n🏁 Discovery completed successfully!")
    else:
        print(f"\n💥 Discovery failed!")