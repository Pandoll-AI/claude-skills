#!/usr/bin/env python3
"""
Extract page source and analyze HTML structure.

Usage:
  python view_source.py --url "https://target.com"
  python view_source.py --url "https://target.com" --extract forms
  python view_source.py --url "https://target.com" --extract links
  python view_source.py --url "https://target.com" --extract scripts
  python view_source.py --url "https://target.com" --extract comments

Output: JSON with page_source, extracted data
"""

import argparse
import asyncio
import base64
import json
import re
import sys

MAX_PAGE_SOURCE_LENGTH = 30_000


async def view_source(url: str, extract: str | None = None) -> dict:
    """Get page source and optionally extract specific elements."""
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

        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(1)

        source = await page.content()
        original_length = len(source)

        result = {
            "url": page.url,
            "title": await page.title(),
            "original_length": original_length,
        }

        # Truncate source if too long
        if original_length > MAX_PAGE_SOURCE_LENGTH:
            half = MAX_PAGE_SOURCE_LENGTH // 2
            source = (
                source[:half]
                + f"\n\n<!-- TRUNCATED {original_length - MAX_PAGE_SOURCE_LENGTH} chars -->\n\n"
                + source[-half:]
            )
            result["truncated"] = True

        result["page_source"] = source

        # Extract specific elements
        if extract == "forms":
            forms = await page.evaluate(
                """() => {
                const forms = [];
                document.querySelectorAll('form').forEach(f => {
                    const inputs = [];
                    f.querySelectorAll('input, textarea, select').forEach(i => {
                        inputs.push({
                            tag: i.tagName.toLowerCase(),
                            name: i.name || '',
                            id: i.id || '',
                            type: i.type || '',
                            value: i.value || '',
                            placeholder: i.placeholder || ''
                        });
                    });
                    forms.push({
                        action: f.action,
                        method: (f.method || 'GET').toUpperCase(),
                        id: f.id || '',
                        name: f.name || '',
                        inputs: inputs
                    });
                });
                return forms;
            }"""
            )
            result["forms"] = forms

        elif extract == "links":
            links = await page.evaluate(
                """() => {
                const links = [];
                const seen = new Set();
                document.querySelectorAll('a[href]').forEach(a => {
                    if (!seen.has(a.href)) {
                        seen.add(a.href);
                        links.push({
                            href: a.href,
                            text: a.textContent.trim().slice(0, 100),
                            rel: a.rel || '',
                            target: a.target || ''
                        });
                    }
                });
                return links;
            }"""
            )
            result["links"] = links

        elif extract == "scripts":
            scripts = await page.evaluate(
                """() => {
                const scripts = [];
                document.querySelectorAll('script').forEach(s => {
                    scripts.push({
                        src: s.src || '[inline]',
                        type: s.type || 'text/javascript',
                        async: s.async,
                        defer: s.defer,
                        content_preview: s.src ? '' : s.textContent.slice(0, 500)
                    });
                });
                return scripts;
            }"""
            )
            result["scripts"] = scripts

        elif extract == "comments":
            # Extract HTML comments
            comments = re.findall(r"<!--(.*?)-->", source, re.DOTALL)
            result["comments"] = [c.strip()[:500] for c in comments[:50]]

        elif extract == "meta":
            meta = await page.evaluate(
                """() => {
                const meta = [];
                document.querySelectorAll('meta').forEach(m => {
                    meta.push({
                        name: m.name || '',
                        property: m.getAttribute('property') || '',
                        content: m.content || '',
                        httpEquiv: m.httpEquiv || ''
                    });
                });
                return meta;
            }"""
            )
            result["meta"] = meta

        elif extract == "headers":
            # Get response headers (via JS isn't possible, use performance API)
            headers = await page.evaluate(
                """() => {
                const entries = performance.getEntriesByType('navigation');
                if (entries.length > 0) {
                    const timing = entries[0];
                    return {
                        transferSize: timing.transferSize,
                        encodedBodySize: timing.encodedBodySize,
                        decodedBodySize: timing.decodedBodySize,
                        duration: timing.duration
                    };
                }
                return {};
            }"""
            )
            result["performance"] = headers

        # Capture screenshot
        screenshot_bytes = await page.screenshot(type="png", full_page=False)
        result["screenshot_base64"] = base64.b64encode(screenshot_bytes).decode("utf-8")

        await browser.close()

        return result


def main():
    parser = argparse.ArgumentParser(description="View page source")
    parser.add_argument("--url", required=True, help="URL to get source from")
    parser.add_argument(
        "--extract",
        choices=["forms", "links", "scripts", "comments", "meta", "headers"],
        help="Extract specific elements",
    )

    args = parser.parse_args()

    try:
        result = asyncio.run(view_source(url=args.url, extract=args.extract))
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "type": type(e).__name__}))
        sys.exit(1)


if __name__ == "__main__":
    main()
