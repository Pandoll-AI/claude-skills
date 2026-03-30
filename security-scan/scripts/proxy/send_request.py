#!/usr/bin/env python3
"""
Send HTTP requests for security testing.

Usage:
  python send_request.py --method GET --url "https://api.example.com/users"
  python send_request.py --method POST --url "https://api.example.com/login" --body '{"user":"admin"}'
  python send_request.py --method GET --url "https://example.com" --header "Authorization: Bearer token"
  python send_request.py --method GET --url "https://example.com" --cookie "session=abc123"

Output: JSON with status_code, headers, body, response_time_ms
"""

import argparse
import json
import sys
import time


def send_request(
    method: str,
    url: str,
    headers: list[str] | None = None,
    body: str | None = None,
    cookies: list[str] | None = None,
    timeout: int = 30,
    follow_redirects: bool = True,
    verify_ssl: bool = True,
) -> dict:
    """Send HTTP request and return response details."""
    import httpx

    # Parse headers
    header_dict = {}
    if headers:
        for h in headers:
            if ":" in h:
                key, value = h.split(":", 1)
                header_dict[key.strip()] = value.strip()

    # Parse cookies
    cookie_dict = {}
    if cookies:
        for c in cookies:
            if "=" in c:
                key, value = c.split("=", 1)
                cookie_dict[key.strip()] = value.strip()

    # Parse body
    content = None
    json_body = None
    if body:
        try:
            json_body = json.loads(body)
        except json.JSONDecodeError:
            content = body

    # Set default user-agent if not provided
    if "User-Agent" not in header_dict and "user-agent" not in header_dict:
        header_dict["User-Agent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    start_time = time.time()

    try:
        with httpx.Client(
            timeout=timeout,
            follow_redirects=follow_redirects,
            verify=verify_ssl,
        ) as client:
            response = client.request(
                method=method.upper(),
                url=url,
                headers=header_dict,
                cookies=cookie_dict,
                json=json_body,
                content=content,
            )

        elapsed_ms = (time.time() - start_time) * 1000

        # Get response body
        try:
            response_body = response.text
            # Truncate if too long
            if len(response_body) > 50000:
                response_body = response_body[:50000] + "\n\n[TRUNCATED]"
        except Exception:
            response_body = "[Binary content]"

        # Check if response is JSON
        response_json = None
        try:
            response_json = response.json()
        except Exception:
            pass

        result = {
            "success": True,
            "method": method.upper(),
            "url": str(response.url),
            "status_code": response.status_code,
            "status_text": response.reason_phrase,
            "response_time_ms": round(elapsed_ms, 2),
            "response_headers": dict(response.headers),
            "response_body": response_body,
            "response_json": response_json,
            "content_length": len(response.content),
            "redirected": len(response.history) > 0,
            "redirect_history": [str(r.url) for r in response.history],
        }

        # Security-relevant header analysis
        security_headers = {}
        for header in [
            "Content-Security-Policy",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "Strict-Transport-Security",
            "X-XSS-Protection",
            "Access-Control-Allow-Origin",
            "Set-Cookie",
        ]:
            value = response.headers.get(header)
            if value:
                security_headers[header] = value

        result["security_headers"] = security_headers

        # Analyze cookies
        cookies_received = []
        for cookie in response.cookies.jar:
            cookies_received.append(
                {
                    "name": cookie.name,
                    "value": cookie.value[:50] + "..." if len(cookie.value) > 50 else cookie.value,
                    "domain": cookie.domain,
                    "path": cookie.path,
                    "secure": cookie.secure,
                    "httponly": "httponly" in str(cookie).lower(),
                }
            )
        result["cookies_received"] = cookies_received

        return result

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Request timed out",
            "error_type": "TimeoutException",
            "url": url,
            "method": method.upper(),
        }
    except httpx.ConnectError as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "ConnectError",
            "url": url,
            "method": method.upper(),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "url": url,
            "method": method.upper(),
        }


def main():
    parser = argparse.ArgumentParser(description="Send HTTP request")
    parser.add_argument(
        "--method",
        required=True,
        choices=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
        help="HTTP method",
    )
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument(
        "--header",
        action="append",
        dest="headers",
        help="Request header (can be used multiple times)",
    )
    parser.add_argument("--body", help="Request body (JSON or raw)")
    parser.add_argument(
        "--cookie",
        action="append",
        dest="cookies",
        help="Cookie (name=value, can be used multiple times)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--no-follow-redirects",
        action="store_true",
        help="Don't follow redirects",
    )
    parser.add_argument(
        "--no-verify-ssl",
        action="store_true",
        help="Don't verify SSL certificates",
    )

    args = parser.parse_args()

    try:
        result = send_request(
            method=args.method,
            url=args.url,
            headers=args.headers,
            body=args.body,
            cookies=args.cookies,
            timeout=args.timeout,
            follow_redirects=not args.no_follow_redirects,
            verify_ssl=not args.no_verify_ssl,
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "type": type(e).__name__}))
        sys.exit(1)


if __name__ == "__main__":
    main()
