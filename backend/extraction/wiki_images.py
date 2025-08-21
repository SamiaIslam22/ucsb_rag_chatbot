import os
import base64
import asyncio
import httpx
import csv
from urllib.parse import urljoin, urlparse, urlunparse
from dotenv import load_dotenv
from openai import OpenAI
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

# Import the multi-page scraper to get page text
try:
    from wiki_texts import run_all_scrapes, wiki_links as MULTI_LINKS
except Exception:
    # still allow running with just PAGE_URL if wiki_links isn't defined
    from wiki_texts import run_all_scrapes
    MULTI_LINKS = []

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# You can keep this as a single page seed, or just manage links in multi_page.wiki_links
PAGE_URL = "https://wiki.nanofab.ucsb.edu/wiki/E-Beam_1_-_4-inch,_4-wafer_Fixture_SOP"
MODEL_VISION = "gpt-4o-mini"

# :file_folder: Save to csv_dataframes/raw/ folder
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

# --- Main ---
async def main():
    # 0) Decide which pages to process
    pages = list({*(MULTI_LINKS or []), PAGE_URL})  # ensure PAGE_URL included
    print(f"Pages to process: {len(pages)}")
    
    # 1) Use multi_page.py to extract page text (markdown) per URL
    scraped = await run_all_scrapes(pages)
    
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
        for page_url in pages:
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
    
    print(f"Keeping {len(entries)} unique content images after dedupe across all pages")
    
    # 3) Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    
    # 4) Download, summarize with CONTEXT, write CSV (NO EMBEDDINGS)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Simplified CSV header - just the core data
        writer.writerow(["index", "page_url", "image_url", "title", "alt", "caption", "summary"])
        
        async with httpx.AsyncClient() as http_client:
            for idx, e in enumerate(entries, 1):
                img_url = e["url"]
                page_url = e["page_url"]
                print(f"\nImage {idx}/{len(entries)}: {img_url}")
                
                data_url = await download_image_as_data_url(img_url, http_client)
                if not data_url:
                    print("  :x: Failed to fetch image")
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
                
                try:
                    summary = summarize_image_with_context(
                        data_url,
                        context_text=context_text,
                        alt=e.get("alt"),
                        caption=e.get("caption")
                    )
                except Exception as ex:
                    summary = f"[error] {ex}"
                
                # Write row with simplified data
                writer.writerow([
                    idx,
                    page_url,
                    img_url,
                    page_title,
                    e.get("alt") or "",
                    e.get("caption") or "",
                    summary
                ])
    
    print(f"\n✅ Saved CSV to {OUT_PATH}")

if __name__ == "__main__":
    asyncio.run(main())