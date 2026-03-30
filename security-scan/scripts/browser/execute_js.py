#!/usr/bin/env python3
"""
Execute JavaScript code in the browser context.

Usage:
  python execute_js.py --url "https://target.com" --code "document.cookie"
  python execute_js.py --url "https://target.com" --code "localStorage.getItem('token')"
  python execute_js.py --url "https://target.com" --code "JSON.stringify(window.config)"

Output: JSON with js_result, screenshot_base64
"""

import argparse
import asyncio
import base64
import json
import sys

MAX_JS_RESULT_LENGTH = 10_000


async def execute_js(url: str, code: str) -> dict:
    """Execute JavaScript and return result."""
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

        # Navigate first
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(1)

        result = {"code": code, "success": False}

        try:
            js_result = await page.evaluate(code)
            result["js_result"] = js_result
            result["success"] = True

            # Truncate if too long
            result_str = str(js_result)
            if len(result_str) > MAX_JS_RESULT_LENGTH:
                result["js_result_truncated"] = True
                result["js_result"] = result_str[:MAX_JS_RESULT_LENGTH] + "... [TRUNCATED]"

        except Exception as e:
            result["error"] = str(e)
            result["error_type"] = type(e).__name__

        # Capture screenshot
        screenshot_bytes = await page.screenshot(type="png", full_page=False)
        result["screenshot_base64"] = base64.b64encode(screenshot_bytes).decode("utf-8")
        result["current_url"] = page.url
        result["title"] = await page.title()

        await browser.close()

        return result


def main():
    parser = argparse.ArgumentParser(description="Execute JavaScript")
    parser.add_argument("--url", required=True, help="URL to execute JS on")
    parser.add_argument("--code", required=True, help="JavaScript code to execute")

    args = parser.parse_args()

    try:
        result = asyncio.run(execute_js(url=args.url, code=args.code))
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "type": type(e).__name__}))
        sys.exit(1)


if __name__ == "__main__":
    main()
