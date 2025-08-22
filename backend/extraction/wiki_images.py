import os
import base64
import asyncio
import httpx
import csv
import pandas as pd
from urllib.parse import urljoin, urlparse, urlunparse
from dotenv import load_dotenv
from openai import OpenAI
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

# Import the multi-page scraper to get page text
try:
    from wiki_texts import run_all_scrapes
except Exception:
    print("⚠️ Could not import wiki_texts module")

# Load URLs from CSV instead of hardcoded links
def load_wiki_urls_from_csv():
    """Load wiki URLs from the generated CSV file."""
    csv_path = "csv_dataframes/raw/wiki_all_page_links.csv"
    
    # Check if the CSV exists
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        print("📋 Run wiki_all_pages_links.py first to generate the URLs")
        
        # Fallback to manual links if CSV doesn't exist
        fallback_links = [
            "https://wiki.nanofab.ucsb.edu/wiki/E-Beam_1_-_4-inch,_4-wafer_Fixture_SOP",
            "https://wiki.nanofab.ucsb.edu/wiki/ICP_Etch_1_(Panasonic_E646V)",
            "https://wiki.nanofab.ucsb.edu/wiki/Oxford_ICP_Etcher_(PlasmaPro_100_Cobra)"
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

# Initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MULTI_LINKS = load_wiki_urls_from_csv()

MODEL_VISION = "gpt-4o-mini"

# Save to csv_dataframes/raw/ folder
OUT_PATH = "csv_dataframes/raw/wiki_images.csv"   # CSV output

# --- Helpers ---
def normalize_mediawiki_image_url(url: str) -> str:
    """Convert MediaWiki thumbnail to original image."""
    try:
        parsed = urlparse(url)
        path = parsed.path
        marker = "/w/images/thumb/"
        if marker in path:
            tail = path.split(marker, 1)[1]
            parts = tail.split("/")
            if len(parts) >= 3:
                a, ab, filename = parts[0], parts[1], parts[2]
                new_path = f"/w/images/{a}/{ab}/{filename}"
                return urlunparse(parsed._replace(path=new_path))
    except Exception:
        pass
    return url

def get_mime_from_url(url: str) -> str:
    low = url.lower()
    if low.endswith(".png"): return "image/png"
    if low.endswith(".jpg") or low.endswith(".jpeg"): return "image/jpeg"
    if low.endswith(".gif"): return "image/gif"
    if low.endswith(".webp"): return "image/webp"
    return "application/octet-stream"

async def download_image_as_data_url(url: str, client_http: httpx.AsyncClient) -> str | None:
    """Download image and return data URL (base64)."""
    mime = get_mime_from_url(url)
    try:
        r = await client_http.get(url, timeout=20.0, follow_redirects=True)
        if r.status_code == 200 and r.content:
            b64 = base64.b64encode(r.content).decode("ascii")
            return f"data:{mime};base64,{b64}"
    except Exception as e:
        print(f"Download failed for {url}: {e}")
    return None

def filename_key(u: str) -> str:
    """Stable key for deduping after thumb→orig normalization."""
    try:
        return urlparse(u).path.rsplit("/", 1)[-1].lower()
    except Exception:
        return u.lower()

def is_probably_ui(url: str) -> bool:
    """Drop obvious UI assets/logos if any slip in."""
    low = url.lower()
    bad_fragments = ["powered_by_mediawiki", "wikimedia-button", "logo", "sprite", "icon"]
    return any(b in low for b in bad_fragments)

def clip_context(text: str, max_chars: int = 1000) -> str:
    """Trim context so it doesn't drown the model."""
    if not text:
        return ""
    text = " ".join(text.split())  # collapse whitespace
    return text[:max_chars]

def summarize_image_with_context(data_url: str, context_text: str, alt=None, caption=None) -> str:
    """Call OpenAI vision model with page context."""
    context_bits = []
    if alt: context_bits.append(f"ALT: {alt}")
    if caption: context_bits.append(f"CAPTION: {caption}")
    if context_text: context_bits.append(f"PAGE CONTEXT: {context_text}")
    context = "\n".join(context_bits).strip()
    
    prompt = "Describe this image for lab documentation. Highlight its purpose and key technical details."
    if context:
        prompt += f"\n\nContext:\n{context}"
    
    try:
        resp = client.chat.completions.create(
            model=MODEL_VISION,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
            }]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[error] OpenAI API call failed: {e}"

# --- Main ---
async def main():
    print("🔍 Starting UCSB Wiki Image Extraction...")
    
    # Get pages to process from CSV
    pages = MULTI_LINKS
    if not pages:
        print("❌ No pages to process!")
        print("🔧 Please run wiki_all_pages_links.py first")
        return
        
    print(f"📋 Processing {len(pages)} pages for image extraction")
    
    # 1) Use wiki_texts.py to extract page text (markdown) per URL for context
    print("📝 Getting page text for context...")
    try:
        scraped = await run_all_scrapes(pages)
        print(f"✅ Got text context for {len(scraped)} pages")
    except Exception as e:
        print(f"⚠️ Could not get page text context: {e}")
        scraped = []
    
    # Build quick lookup: url -> context (title + markdown)
    page_ctx = {}
    for item in scraped:
        ctx_text = ""
        # Prefer markdown (already somewhat cleaned)
        if item.get("markdown"):
            ctx_text = item["markdown"]
        page_ctx[item["url"]] = {
            "title": item.get("title") or "",
            "context_text": clip_context(ctx_text, max_chars=1000),
        }
    
    # 2) Crawl each page for images
    config = CrawlerRunConfig(
        word_count_threshold=0,
        exclude_external_images=False,
        cache_mode=CacheMode.BYPASS
    )
    
    entries = []
    async with AsyncWebCrawler() as crawler:
        for page_index, page_url in enumerate(pages, 1):
            print(f"🖼️ Crawling images from page {page_index}/{len(pages)}: {page_url[-50:]}")
            
            try:
                result = await crawler.arun(url=page_url, config=config)
                images = result.media.get("images", [])
                
                raw_entries = []
                for img in images:
                    src = img.get("src")
                    if not src:
                        continue
                    
                    # absolutize
                    if src.startswith("//"):
                        src = "https:" + src
                    elif not src.startswith("http"):
                        src = urljoin(page_url, src)
                    
                    # normalize any MediaWiki thumbnail to original
                    src = normalize_mediawiki_image_url(src)
                    
                    raw_entries.append({
                        "page_url": page_url,
                        "url": src,
                        "alt": img.get("alt"),
                        "caption": img.get("caption") or img.get("desc") or img.get("figcaption")
                    })
                
                # Optional: drop obvious UI images (just in case)
                filtered = [e for e in raw_entries if not is_probably_ui(e["url"])]
                
                # Dedupe per page by normalized filename
                seen = set()
                for e in filtered:
                    k = filename_key(e["url"])
                    if k in seen:
                        continue
                    seen.add(k)
                    entries.append(e)
                    
                print(f"   ✅ Found {len(filtered)} unique images on this page")
                
            except Exception as e:
                print(f"   ❌ Error crawling {page_url}: {e}")
    
    print(f"🎯 Total unique content images found: {len(entries)}")
    
    # 3) Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    
    # 4) Download, summarize with CONTEXT, write CSV
    print(f"🤖 Starting AI-powered image analysis...")
    
    # Create CSV even if no images found
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "page_url", "image_url", "title", "alt", "caption", "summary"])
        
        if not entries:
            print("⚠️ No images found to process")
        else:
            async with httpx.AsyncClient() as http_client:
                for idx, e in enumerate(entries, 1):
                    img_url = e["url"]
                    page_url = e["page_url"]
                    print(f"\n🔄 Processing image {idx}/{len(entries)}: {img_url[-50:]}")
                    
                    data_url = await download_image_as_data_url(img_url, http_client)
                    if not data_url:
                        print("   ❌ Failed to fetch image")
                        writer.writerow([
                            idx, 
                            page_url,
                            img_url, 
                            "", 
                            e.get("alt") or "", 
                            e.get("caption") or "", 
                            "[error] fetch failed"
                        ])
                        continue
                    
                    # Pull context text for this image's page
                    ctx_info = page_ctx.get(page_url, {})
                    context_text = ctx_info.get("context_text", "")
                    page_title = ctx_info.get("title", "")
                    
                    print(f"   🤖 Analyzing image with AI...")
                    try:
                        summary = summarize_image_with_context(
                            data_url,
                            context_text=context_text,
                            alt=e.get("alt"),
                            caption=e.get("caption")
                        )
                        print(f"   ✅ AI analysis complete")
                    except Exception as ex:
                        summary = f"[error] {ex}"
                        print(f"   ❌ AI analysis failed: {ex}")
                    
                    # Write row with data
                    writer.writerow([
                        idx,
                        page_url,
                        img_url,
                        page_title,
                        e.get("alt") or "",
                        e.get("caption") or "",
                        summary
                    ])
    
    print(f"\n✅ Image extraction complete!")
    print(f"📄 CSV saved to: {OUT_PATH}")
    print(f"🖼️ Processed {len(entries)} images from {len(pages)} pages")
    
    # Verify output file
    if os.path.exists(OUT_PATH):
        try:
            verify_df = pd.read_csv(OUT_PATH)
            print(f"✅ Output file verified: {len(verify_df)} rows")
        except Exception as e:
            print(f"⚠️ Output file verification failed: {e}")
    else:
        print(f"❌ Output file not created: {OUT_PATH}")

if __name__ == "__main__":
    asyncio.run(main())