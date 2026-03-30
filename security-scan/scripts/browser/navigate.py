#!/usr/bin/env python3
"""
Navigate to URL and capture page state.

Usage:
  python navigate.py --url "https://target.com" [--wait-for networkidle] [--timeout 30]

Output: JSON with url, title, screenshot_base64, page_source (truncated)
"""

import argparse
import asyncio
import base64
import json
import sys

MAX_PAGE_SOURCE_LENGTH = 20_000


async def navigate(
    url: str,
    wait_until: str = "domcontentloaded",
    timeout: int = 30,
) -> dict:
    """Navigate to URL and return page state."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until=wait_until, timeout=timeout * 1000)
        except Exception as e:
            await browser.close()
            return {"error": str(e), "type": type(e).__name__}

        # Wait a bit for dynamic content
        await asyncio.sleep(1)

        # Capture screenshot
        screenshot_bytes = await page.screenshot(type="png", full_page=False)
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        # Get page info
        current_url = page.url
        title = await page.title()
        source = await page.content()

        # Truncate source if too long
        if len(source) > MAX_PAGE_SOURCE_LENGTH:
            half = MAX_PAGE_SOURCE_LENGTH // 2
            source = (
                source[:half]
                + f"\n\n<!-- TRUNCATED {len(source) - MAX_PAGE_SOURCE_LENGTH} chars -->\n\n"
                + source[-half:]
            )

        # Extract links
        links = await page.evaluate(
            """() => {
            const links = [];
            document.querySelectorAll('a[href]').forEach(a => {
                links.push({href: a.href, text: a.textContent.trim().slice(0, 100)});
            });
            return links.slice(0, 50);
        }"""
        )

        # Extract forms
        forms = await page.evaluate(
            """() => {
            const forms = [];
            document.querySelectorAll('form').forEach(f => {
                const inputs = [];
                f.querySelectorAll('input, textarea, select').forEach(i => {
                    inputs.push({
                        name: i.name || i.id,
                        type: i.type || i.tagName.toLowerCase(),
                        value: i.value || ''
                    });
                });
                forms.push({
                    action: f.action,
                    method: f.method || 'GET',
                    inputs: inputs
                });
            });
            return forms;
        }"""
        )

        await browser.close()

        return {
            "url": current_url,
            "title": title,
            "screenshot_base64": screenshot_b64,
            "page_source": source,
            "links": links,
            "forms": forms,
            "viewport": {"width": 1280, "height": 720},
        }


def main():
    parser = argparse.ArgumentParser(description="Navigate to URL")
    parser.add_argument("--url", required=True, help="URL to navigate to")
    parser.add_argument(
        "--wait-for",
        default="domcontentloaded",
        choices=["domcontentloaded", "load", "networkidle"],
        help="Wait condition (default: domcontentloaded)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds (default: 30)",
    )

    args = parser.parse_args()

    try:
        result = asyncio.run(
            navigate(url=args.url, wait_until=args.wait_for, timeout=args.timeout)
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "type": type(e).__name__}))
        sys.exit(1)


if __name__ == "__main__":
    main()
