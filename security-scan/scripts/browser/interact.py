#!/usr/bin/env python3
"""
Page interaction: click, type, scroll, hover, press key.

Usage:
  python interact.py --url "https://target.com" --action click --coordinate "100,200"
  python interact.py --url "https://target.com" --action click --selector "#login-btn"
  python interact.py --url "https://target.com" --action type --selector "#username" --text "admin"
  python interact.py --url "https://target.com" --action scroll --direction down
  python interact.py --url "https://target.com" --action press --key Enter

Output: JSON with success, screenshot_base64, error (if any)
"""

import argparse
import asyncio
import base64
import json
import sys


async def interact(
    url: str,
    action: str,
    coordinate: str | None = None,
    selector: str | None = None,
    text: str | None = None,
    direction: str | None = None,
    key: str | None = None,
) -> dict:
    """Interact with page element."""
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

        # Navigate to URL first
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(1)

        result = {"action": action, "success": False}

        try:
            if action == "click":
                if coordinate:
                    x, y = map(int, coordinate.split(","))
                    await page.mouse.click(x, y)
                    result["clicked_at"] = {"x": x, "y": y}
                elif selector:
                    await page.click(selector)
                    result["clicked_selector"] = selector
                else:
                    raise ValueError("Either --coordinate or --selector required")
                result["success"] = True

            elif action == "type":
                if not text:
                    raise ValueError("--text required for type action")
                if selector:
                    await page.fill(selector, text)
                    result["typed_in"] = selector
                else:
                    await page.keyboard.type(text)
                    result["typed_text"] = text
                result["success"] = True

            elif action == "scroll":
                if direction == "down":
                    await page.keyboard.press("PageDown")
                elif direction == "up":
                    await page.keyboard.press("PageUp")
                else:
                    raise ValueError("--direction must be 'up' or 'down'")
                result["scrolled"] = direction
                result["success"] = True

            elif action == "press":
                if not key:
                    raise ValueError("--key required for press action")
                await page.keyboard.press(key)
                result["pressed"] = key
                result["success"] = True

            elif action == "hover":
                if coordinate:
                    x, y = map(int, coordinate.split(","))
                    await page.mouse.move(x, y)
                    result["hovered_at"] = {"x": x, "y": y}
                elif selector:
                    await page.hover(selector)
                    result["hovered_selector"] = selector
                else:
                    raise ValueError("Either --coordinate or --selector required")
                result["success"] = True

            elif action == "double_click":
                if coordinate:
                    x, y = map(int, coordinate.split(","))
                    await page.mouse.dblclick(x, y)
                    result["double_clicked_at"] = {"x": x, "y": y}
                elif selector:
                    await page.dblclick(selector)
                    result["double_clicked_selector"] = selector
                else:
                    raise ValueError("Either --coordinate or --selector required")
                result["success"] = True

            else:
                raise ValueError(f"Unknown action: {action}")

        except Exception as e:
            result["error"] = str(e)
            result["error_type"] = type(e).__name__

        # Wait for potential page changes
        await asyncio.sleep(0.5)

        # Capture final state
        screenshot_bytes = await page.screenshot(type="png", full_page=False)
        result["screenshot_base64"] = base64.b64encode(screenshot_bytes).decode("utf-8")
        result["current_url"] = page.url
        result["title"] = await page.title()

        await browser.close()

        return result


def main():
    parser = argparse.ArgumentParser(description="Page interaction")
    parser.add_argument("--url", required=True, help="URL to interact with")
    parser.add_argument(
        "--action",
        required=True,
        choices=["click", "type", "scroll", "press", "hover", "double_click"],
        help="Action to perform",
    )
    parser.add_argument("--coordinate", help="Coordinate for click/hover (x,y)")
    parser.add_argument("--selector", help="CSS selector for element")
    parser.add_argument("--text", help="Text to type")
    parser.add_argument(
        "--direction",
        choices=["up", "down"],
        help="Scroll direction",
    )
    parser.add_argument("--key", help="Key to press (e.g., Enter, Tab, Escape)")

    args = parser.parse_args()

    try:
        result = asyncio.run(
            interact(
                url=args.url,
                action=args.action,
                coordinate=args.coordinate,
                selector=args.selector,
                text=args.text,
                direction=args.direction,
                key=args.key,
            )
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "type": type(e).__name__}))
        sys.exit(1)


if __name__ == "__main__":
    main()
