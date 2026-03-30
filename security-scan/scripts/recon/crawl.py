#!/usr/bin/env python3
"""
Web crawling and endpoint discovery.

Usage:
  python crawl.py --url "https://example.com" --depth 2
  python crawl.py --url "https://example.com" --depth 3 --include-external

Output: JSON with discovered URLs, endpoints, forms, parameters
"""

import argparse
import asyncio
import json
import re
import sys
from urllib.parse import urljoin, urlparse


async def crawl_website(
    url: str,
    max_depth: int = 2,
    include_external: bool = False,
    max_pages: int = 100,
) -> dict:
    """Crawl website and discover endpoints."""
    import httpx
    from bs4 import BeautifulSoup

    base_domain = urlparse(url).netloc
    visited = set()
    to_visit = [(url, 0)]
    discovered = {
        "pages": [],
        "forms": [],
        "api_endpoints": [],
        "js_files": [],
        "external_links": [],
        "parameters": set(),
        "emails": set(),
        "comments": [],
    }

    async with httpx.AsyncClient(
        timeout=15,
        follow_redirects=True,
        verify=False,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        },
    ) as client:
        while to_visit and len(visited) < max_pages:
            current_url, depth = to_visit.pop(0)

            if current_url in visited:
                continue

            # Check if same domain
            current_domain = urlparse(current_url).netloc
            if not include_external and current_domain != base_domain:
                discovered["external_links"].append(current_url)
                continue

            visited.add(current_url)

            try:
                response = await client.get(current_url)
            except Exception as e:
                continue

            content_type = response.headers.get("content-type", "")

            # Record page
            page_info = {
                "url": str(response.url),
                "status_code": response.status_code,
                "content_type": content_type,
                "content_length": len(response.content),
            }
            discovered["pages"].append(page_info)

            # Skip non-HTML content
            if "text/html" not in content_type:
                continue

            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # Extract links
            for a in soup.find_all("a", href=True):
                href = a["href"]
                full_url = urljoin(current_url, href)

                # Clean URL
                full_url = full_url.split("#")[0]
                if not full_url or full_url.startswith(("javascript:", "mailto:", "tel:")):
                    continue

                # Extract parameters
                parsed = urlparse(full_url)
                if parsed.query:
                    for param in parsed.query.split("&"):
                        if "=" in param:
                            discovered["parameters"].add(param.split("=")[0])

                # Add to crawl queue if within depth
                if depth < max_depth and full_url not in visited:
                    to_visit.append((full_url, depth + 1))

            # Extract forms
            for form in soup.find_all("form"):
                form_info = {
                    "action": urljoin(current_url, form.get("action", "")),
                    "method": (form.get("method", "GET")).upper(),
                    "page": current_url,
                    "inputs": [],
                }
                for inp in form.find_all(["input", "textarea", "select"]):
                    input_info = {
                        "name": inp.get("name", ""),
                        "type": inp.get("type", "text"),
                        "id": inp.get("id", ""),
                    }
                    if input_info["name"]:
                        form_info["inputs"].append(input_info)
                        discovered["parameters"].add(input_info["name"])
                discovered["forms"].append(form_info)

            # Extract JavaScript files
            for script in soup.find_all("script", src=True):
                js_url = urljoin(current_url, script["src"])
                if js_url not in [j["url"] for j in discovered["js_files"]]:
                    discovered["js_files"].append({"url": js_url, "page": current_url})

            # Look for API endpoints in JavaScript
            api_patterns = [
                r'["\']/(api|v\d|graphql)/[^"\']*["\']',
                r'fetch\s*\(\s*["\']([^"\']+)["\']',
                r'axios\.[a-z]+\s*\(\s*["\']([^"\']+)["\']',
                r'\.get\s*\(\s*["\']([^"\']+)["\']',
                r'\.post\s*\(\s*["\']([^"\']+)["\']',
            ]
            for pattern in api_patterns:
                for match in re.findall(pattern, html, re.IGNORECASE):
                    endpoint = match if isinstance(match, str) else match
                    if endpoint and not endpoint.startswith(("http://", "https://")):
                        full_endpoint = urljoin(current_url, endpoint)
                        if full_endpoint not in [e["url"] for e in discovered["api_endpoints"]]:
                            discovered["api_endpoints"].append({
                                "url": full_endpoint,
                                "found_in": current_url,
                            })

            # Extract emails
            email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
            for email in re.findall(email_pattern, html):
                discovered["emails"].add(email.lower())

            # Extract HTML comments
            for comment in soup.find_all(string=lambda t: isinstance(t, type(soup.new_string(""))) and t.parent.name is None):
                pass
            comment_pattern = r"<!--(.*?)-->"
            for comment in re.findall(comment_pattern, html, re.DOTALL):
                comment = comment.strip()[:200]
                if comment and comment not in discovered["comments"]:
                    discovered["comments"].append(comment)

    # Convert sets to lists for JSON
    discovered["parameters"] = sorted(discovered["parameters"])
    discovered["emails"] = sorted(discovered["emails"])

    return {
        "base_url": url,
        "pages_crawled": len(visited),
        "max_depth": max_depth,
        "discovered": discovered,
        "summary": {
            "total_pages": len(discovered["pages"]),
            "total_forms": len(discovered["forms"]),
            "total_api_endpoints": len(discovered["api_endpoints"]),
            "total_js_files": len(discovered["js_files"]),
            "total_parameters": len(discovered["parameters"]),
            "total_emails": len(discovered["emails"]),
            "total_external_links": len(discovered["external_links"]),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Web crawler")
    parser.add_argument("--url", required=True, help="Starting URL")
    parser.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Maximum crawl depth (default: 2)",
    )
    parser.add_argument(
        "--include-external",
        action="store_true",
        help="Include external links in crawl",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=100,
        help="Maximum pages to crawl (default: 100)",
    )

    args = parser.parse_args()

    try:
        result = asyncio.run(
            crawl_website(
                url=args.url,
                max_depth=args.depth,
                include_external=args.include_external,
                max_pages=args.max_pages,
            )
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "type": type(e).__name__}))
        sys.exit(1)


if __name__ == "__main__":
    main()
