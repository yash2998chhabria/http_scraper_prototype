import json
import asyncio
from urllib.parse import urlparse, urljoin
from datetime import datetime
from playwright.async_api import async_playwright

# CONFIG
seed_urls = [
    "https://typingmind.com/",
    "https://mygpt.ai/",
    "https://halist.ai/",
    "https://chatpad.ai/",
    "https://github.com/aws-samples/bedrock-claude-chat",
    "https://jan.ai/",
    "https://github.com/sindresorhus/awesome-chatgpt",
    "https://www.reddit.com/r/gptwrappers/"
]
keywords = ['converstations', 'o4', 'claude', 'gemini']
output_file = 'matched_api_calls_req_body.ndjson'
visited_urls = set()
max_depth = 2

def append_to_file(data):
    with open(output_file, 'a') as f:
        f.write(json.dumps(data) + '\n')

async def intercept_requests(page):
    async def handle_request(route, request):
        try:
            url = request.url.lower()
            method = request.method.upper()
            resource_type = request.resource_type
            headers = {k.lower(): v.lower() for k, v in request.headers.items()}
            timestamp = datetime.utcnow().isoformat()

            # Only check body (POST/PUT/PATCH)
            post_data = ''
            if method in ['POST', 'PUT', 'PATCH']:
                try:
                    post_data = (await request.post_data() or '').lower()
                except Exception:
                    post_data = ''

                if any(keyword in post_data for keyword in keywords):
                    metadata = {
                        'timestamp': timestamp,
                        'url': url,
                        'method': method,
                        'headers': headers,
                        'post_data': post_data,
                    }
                    print(f"[MATCH] {method} {url}")
                    append_to_file(metadata)

            await route.continue_()
        except Exception as e:
            print(f"Error in handle_request: {e}")
            await route.continue_()

    await page.route("**/*", handle_request)

async def extract_links(page, base_url):
    anchors = await page.eval_on_selector_all("a", "els => els.map(el => el.href)")
    text_content = await page.content()

    extracted = set()
    parsed_base = urlparse(base_url)

    # From <a href>
    for link in anchors:
        parsed_link = urlparse(link)
        clean_link = urljoin(base_url, parsed_link.path or '').rstrip('/')
        if parsed_link.scheme.startswith("http"):
            extracted.add(clean_link)

    return extracted

async def crawl_page(playwright, url, depth):
    if url in visited_urls or depth > max_depth:
        return
    visited_urls.add(url)

    print(f"[INFO] Visiting {url}")
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await intercept_requests(page)

    try:
        await page.goto(url, timeout=20000)
        await page.mouse.wheel(0, 500)
        await page.wait_for_timeout(3000)
        links = await extract_links(page, url)
    except Exception as e:
        print(f"Error visiting {url}: {e}")
        links = set()

    await browser.close()

    for link in links:
        await crawl_page(playwright, link, depth + 1)

async def main():
    async with async_playwright() as playwright:
        for url in seed_urls:
            await crawl_page(playwright, url, 0)

try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
        loop.create_task(main())
    else:
        loop.run_until_complete(main())
except RuntimeError:
    asyncio.run(main())
