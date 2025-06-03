import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime

# Output file for streaming logs
output_file = "llm_prompts_log.ndjson"

# Append data to file safely
def append_to_file(data):
    with open(output_file, "a") as f:
        f.write(json.dumps(data) + "\n")

# Log POST request data if it looks like an LLM prompt
async def log_prompt_body(req, page_url):
    try:
        post_data = await req.post_data()
        if post_data:
            data = json.loads(post_data)
            if isinstance(data, dict) and any(k in data for k in ["messages", "prompt", "inputs"]):
                record = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "url": req.url,
                    "method": req.method,
                    "page": page_url,
                    "body": data
                }
                append_to_file(record)
                print(f"\n🔍 LLM Prompt Detected: {req.url}\n{json.dumps(data, indent=2)}\n")
    except Exception as e:
        pass

# Crawl and intercept POST requests
async def log_llm_requests(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        page.on("request", lambda req: asyncio.create_task(log_prompt_body(req, url)) if req.method == "POST" else None)

        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"Error loading {url}: {e}")

        await browser.close()

# Main driver
urls = [
    "https://chat.openai.com",           # OpenAI Chat
    "https://platform.openai.com/playground",  # OpenAI Playground
    "https://chatbotui.com",             # Chatbot UI (open-source)
    "https://bettergpt.chat",            # Better ChatGPT
    "https://chatboxai.app",             # Chatbox AI
    "https://typingmind.com",            # TypingMind
    "https://librechat.ai",              # LibreChat
    "https://chat.forefront.ai",         # Forefront Chat
    "https://poe.com",                   # Poe by Quora
    "https://nat.dev",                   # nat.dev Playground
    "https://agnai.chat",                # Agnai / Agnaistic
    # Optional: If ora.sh comes back online
    "https://ora.sh",
]

async def main():
    for url in urls:
        print(f"\n--- Crawling {url} ---")
        await log_llm_requests(url)

asyncio.run(main())
