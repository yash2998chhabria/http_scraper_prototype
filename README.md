# Async Crawler for API Keyword Detection

This is an asynchronous web crawler built with Python and Playwright. It visits a list of seed URLs, extracts additional links (up to a configurable depth), and intercepts network requests on the pages to identify API calls or content related to specific keywords. Matching requests are logged into an `.ndjson` file for further analysis.

## 🚀 Features

- Async crawling with Playwright
- Dynamic link extraction (from anchor tags and page content)
- Request interception and logging (XHR, Fetch requests)
- Keyword matching in URLs, headers, and post data
- Outputs results in newline-delimited JSON (`.ndjson`) format

## 🛠 Configuration

Modify these parameters in the script:

- `seed_urls`: Initial list of URLs to crawl.
- `keywords`: List of keywords to match in requests.
- `output_file`: Output file for matched API calls.
- `max_depth`: Maximum depth of crawling from seed URLs.

## 📦 Output Format

Each matched API call is logged as a JSON object in the `.ndjson` file, with fields:

- `timestamp`
- `url`
- `method`
- `resource_type`
- `headers`
- `post_data`

## 📋 Requirements

- Python 3.8+
- Playwright
- asyncio

Install dependencies:

```bash
pip install playwright
playwright install


## 🔍 Usage

Run the script:

```bash
python your_script_name.py

The crawler will start visiting the seed URLs, extract links, and log matching API calls into the specified .ndjson file.