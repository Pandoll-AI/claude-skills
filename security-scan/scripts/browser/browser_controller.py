#!/usr/bin/env python3
"""
Browser lifecycle management for Strix penetration testing skill.
Maintains persistent browser state in /tmp/strix_browser/

Usage:
  python browser_controller.py --action launch [--headless] [--url URL]
  python browser_controller.py --action close
  python browser_controller.py --action status

Output: JSON with status, url, title, screenshot_base64
"""

import argparse
import asyncio
import base64
import json
import os
import sys
from pathlib import Path

STATE_DIR = Path("/tmp/strix_browser")
STATE_FILE = STATE_DIR / "state.json"


def get_state() -> dict:
    """Load browser state from file."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"running": False, "url": None, "title": None}


def save_state(state: dict) -> None:
    """Save browser state to file."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


async def launch_browser(headless: bool = True, url: str | None = None) -> dict:
    """Launch browser and optionally navigate to URL."""
    from playwright.async_api import async_playwright

    state = get_state()
    if state.get("running"):
        return {"error": "Browser is already running. Use --action close first."}

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
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

        if url:
            await page.goto(url, wait_until="domcontentloaded")

        # Capture state
        screenshot_bytes = await page.screenshot(type="png", full_page=False)
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        current_url = page.url
        title = await page.title()

        # Note: For persistent state, we'd need a server process
        # This simplified version launches fresh each time
        await browser.close()

        state = {
            "running": True,
            "url": current_url,
            "title": title,
            "headless": headless,
        }
        save_state(state)

        return {
            "status": "launched",
            "url": current_url,
            "title": title,
            "screenshot_base64": screenshot_b64,
            "viewport": {"width": 1280, "height": 720},
        }


async def close_browser() -> dict:
    """Close browser and clear state."""
    state = get_state()

    # Clear state
    save_state({"running": False, "url": None, "title": None})

    if STATE_FILE.exists():
        STATE_FILE.unlink()

    return {"status": "closed", "message": "Browser session cleared"}


async def get_status() -> dict:
    """Get current browser status."""
    state = get_state()
    return {
        "running": state.get("running", False),
        "url": state.get("url"),
        "title": state.get("title"),
    }


def main():
    parser = argparse.ArgumentParser(description="Browser lifecycle management")
    parser.add_argument(
        "--action",
        required=True,
        choices=["launch", "close", "status"],
        help="Action to perform",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser with visible window",
    )
    parser.add_argument("--url", help="URL to navigate to after launch")

    args = parser.parse_args()

    headless = not args.no_headless

    try:
        if args.action == "launch":
            result = asyncio.run(launch_browser(headless=headless, url=args.url))
        elif args.action == "close":
            result = asyncio.run(close_browser())
        elif args.action == "status":
            result = asyncio.run(get_status())
        else:
            result = {"error": f"Unknown action: {args.action}"}

        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "type": type(e).__name__}))
        sys.exit(1)


if __name__ == "__main__":
    main()
