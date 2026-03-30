#!/usr/bin/env python3
"""
Batch HTTP request sending for fuzzing and parameter testing.

Usage:
  python intercept.py --url "https://target.com/api" --params '{"id": ["1", "2", "3"]}'
  python intercept.py --url "https://target.com/search" --params '{"q": ["<script>", "' OR 1=1--", "${7*7}"]}'
  python intercept.py --url "https://target.com/user/FUZZ" --wordlist ids.txt

Output: JSON with all responses and analysis
"""

import argparse
import asyncio
import json
import sys
import time


async def send_batch_requests(
    url: str,
    method: str = "GET",
    params: dict | None = None,
    wordlist_path: str | None = None,
    headers: dict | None = None,
    body_template: str | None = None,
    concurrency: int = 5,
    delay: float = 0.1,
) -> dict:
    """Send multiple requests with parameter variations."""
    import httpx

    results = []
    payloads = []

    # Build payload list from params
    if params:
        for param_name, values in params.items():
            for value in values:
                payloads.append({"param": param_name, "value": value})

    # Or from wordlist for FUZZ replacement
    if wordlist_path and "FUZZ" in url:
        try:
            with open(wordlist_path) as f:
                for line in f:
                    word = line.strip()
                    if word:
                        payloads.append({"fuzz": word})
        except FileNotFoundError:
            return {"error": f"Wordlist not found: {wordlist_path}"}

    if not payloads:
        return {"error": "No payloads provided. Use --params or --wordlist"}

    default_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    if headers:
        default_headers.update(headers)

    semaphore = asyncio.Semaphore(concurrency)

    async def make_request(payload: dict, client: httpx.AsyncClient) -> dict:
        async with semaphore:
            target_url = url
            request_params = {}
            request_body = body_template

            if "fuzz" in payload:
                target_url = url.replace("FUZZ", payload["fuzz"])
            elif "param" in payload:
                request_params[payload["param"]] = payload["value"]

            start_time = time.time()

            try:
                if method.upper() == "GET":
                    response = await client.get(
                        target_url,
                        params=request_params,
                        headers=default_headers,
                    )
                else:
                    body = None
                    if request_body:
                        body = request_body
                        for key, val in payload.items():
                            body = body.replace(f"{{{key}}}", str(val))

                    response = await client.request(
                        method.upper(),
                        target_url,
                        params=request_params,
                        headers=default_headers,
                        content=body,
                    )

                elapsed_ms = (time.time() - start_time) * 1000

                # Truncate response body
                body_preview = response.text[:1000] if response.text else ""

                result = {
                    "payload": payload,
                    "url": str(response.url),
                    "status_code": response.status_code,
                    "response_time_ms": round(elapsed_ms, 2),
                    "content_length": len(response.content),
                    "body_preview": body_preview,
                }

                # Check for interesting responses
                result["interesting"] = False
                result["flags"] = []

                # Flag different status codes
                if response.status_code not in [200, 301, 302, 404]:
                    result["interesting"] = True
                    result["flags"].append(f"Unusual status: {response.status_code}")

                # Flag reflections of payload
                if "value" in payload and payload["value"] in response.text:
                    result["interesting"] = True
                    result["flags"].append("Payload reflected in response")

                # Flag SQL errors
                sql_errors = ["mysql", "syntax error", "sql", "oracle", "postgresql"]
                for err in sql_errors:
                    if err.lower() in response.text.lower():
                        result["interesting"] = True
                        result["flags"].append(f"Possible SQL error: {err}")
                        break

                # Flag template injection
                if "${" in str(payload.get("value", "")) and "49" in response.text:
                    result["interesting"] = True
                    result["flags"].append("Possible template injection (7*7=49)")

                return result

            except Exception as e:
                return {
                    "payload": payload,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }

            finally:
                await asyncio.sleep(delay)

    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        tasks = [make_request(p, client) for p in payloads]
        results = await asyncio.gather(*tasks)

    # Analyze results
    interesting = [r for r in results if r.get("interesting")]
    errors = [r for r in results if "error" in r]
    successful = [r for r in results if "status_code" in r]

    # Group by status code
    status_distribution = {}
    for r in successful:
        code = r["status_code"]
        status_distribution[code] = status_distribution.get(code, 0) + 1

    return {
        "total_requests": len(results),
        "successful": len(successful),
        "errors": len(errors),
        "interesting_count": len(interesting),
        "status_distribution": status_distribution,
        "interesting_responses": interesting[:20],  # Limit output
        "all_results": results[:100],  # Limit output
    }


def main():
    parser = argparse.ArgumentParser(description="Batch HTTP requests")
    parser.add_argument("--url", required=True, help="Target URL (use FUZZ for wordlist replacement)")
    parser.add_argument(
        "--method",
        default="GET",
        choices=["GET", "POST", "PUT", "DELETE", "PATCH"],
        help="HTTP method (default: GET)",
    )
    parser.add_argument(
        "--params",
        help='Parameters as JSON: {"param": ["val1", "val2"]}',
    )
    parser.add_argument("--wordlist", help="Wordlist file for FUZZ replacement")
    parser.add_argument("--body", help="Request body template (use {param} for substitution)")
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Concurrent requests (default: 5)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Delay between requests in seconds (default: 0.1)",
    )

    args = parser.parse_args()

    params = None
    if args.params:
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON params: {e}"}))
            sys.exit(1)

    try:
        result = asyncio.run(
            send_batch_requests(
                url=args.url,
                method=args.method,
                params=params,
                wordlist_path=args.wordlist,
                body_template=args.body,
                concurrency=args.concurrency,
                delay=args.delay,
            )
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "type": type(e).__name__}))
        sys.exit(1)


if __name__ == "__main__":
    main()
