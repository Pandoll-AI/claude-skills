#!/usr/bin/env python3
"""
Technology stack detection from HTTP headers, cookies, and HTML.

Usage:
  python tech_detect.py --url "https://example.com"

Output: JSON with detected technologies, headers, cookies, evidence
"""

import argparse
import json
import re
import sys


def detect_technologies(url: str) -> dict:
    """Detect technology stack from web response."""
    import httpx

    technologies = []
    evidence = []
    headers_analysis = {}
    cookies_analysis = []

    # Technology signatures
    signatures = {
        # Frameworks
        "Next.js": {
            "headers": ["x-nextjs-matched-path", "x-nextjs-page"],
            "html": [r"/_next/static", r"__NEXT_DATA__"],
        },
        "React": {
            "html": [r"react\.production\.min\.js", r"data-reactroot", r"__REACT_DEVTOOLS_GLOBAL_HOOK__"],
        },
        "Vue.js": {
            "html": [r"vue\.js", r"vue\.min\.js", r"data-v-", r"__VUE__"],
        },
        "Angular": {
            "html": [r"angular\.js", r"ng-version", r"ng-app", r"angular\.min\.js"],
        },
        "Django": {
            "headers": ["x-frame-options"],
            "cookies": ["csrftoken", "sessionid"],
            "html": [r"csrfmiddlewaretoken"],
        },
        "Flask": {
            "cookies": ["session"],
            "headers": ["server"],
        },
        "FastAPI": {
            "headers": ["server"],
            "html": [r"/docs", r"/redoc", r"openapi\.json"],
        },
        "Express.js": {
            "headers": ["x-powered-by"],
        },
        "Rails": {
            "headers": ["x-runtime", "x-request-id"],
            "cookies": ["_session_id"],
            "html": [r"csrf-token", r"rails-ujs"],
        },
        "Laravel": {
            "cookies": ["laravel_session", "XSRF-TOKEN"],
            "html": [r"laravel"],
        },
        "WordPress": {
            "html": [r"wp-content", r"wp-includes", r"wp-json"],
            "headers": ["link"],
        },
        "Drupal": {
            "headers": ["x-drupal-cache", "x-generator"],
            "html": [r"drupal\.js", r"/sites/default/"],
        },
        # Servers
        "Nginx": {
            "headers": ["server"],
        },
        "Apache": {
            "headers": ["server"],
        },
        "Cloudflare": {
            "headers": ["cf-ray", "cf-cache-status", "server"],
        },
        "AWS": {
            "headers": ["x-amz-", "x-amzn-"],
            "html": [r"\.amazonaws\.com", r"\.cloudfront\.net"],
        },
        "Vercel": {
            "headers": ["x-vercel-id", "x-vercel-cache"],
        },
        # JavaScript libraries
        "jQuery": {
            "html": [r"jquery[.-]?\d*\.?m?i?n?\.js"],
        },
        "Bootstrap": {
            "html": [r"bootstrap[.-]?\d*\.?m?i?n?\.css", r"bootstrap[.-]?\d*\.?m?i?n?\.js"],
        },
        # Analytics
        "Google Analytics": {
            "html": [r"google-analytics\.com", r"googletagmanager\.com", r"gtag\("],
        },
        "Firebase": {
            "html": [r"firebaseapp\.com", r"firebase\.js", r"firebase-app\.js"],
        },
        "Supabase": {
            "html": [r"supabase\.co", r"supabase\.js"],
        },
    }

    try:
        with httpx.Client(
            timeout=30,
            follow_redirects=True,
            verify=False,
        ) as client:
            response = client.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                },
            )

        html = response.text.lower()
        headers = {k.lower(): v.lower() for k, v in response.headers.items()}
        cookies = {c.name.lower(): c.value for c in response.cookies.jar}

        # Check each technology
        for tech, sigs in signatures.items():
            detected = False
            tech_evidence = []

            # Check headers
            if "headers" in sigs:
                for header_sig in sigs["headers"]:
                    for header_name, header_value in headers.items():
                        if header_sig.lower() in header_name or header_sig.lower() in header_value:
                            detected = True
                            tech_evidence.append(f"Header: {header_name}={header_value[:100]}")

            # Check cookies
            if "cookies" in sigs:
                for cookie_sig in sigs["cookies"]:
                    if cookie_sig.lower() in cookies:
                        detected = True
                        tech_evidence.append(f"Cookie: {cookie_sig}")

            # Check HTML
            if "html" in sigs:
                for html_sig in sigs["html"]:
                    if re.search(html_sig.lower(), html):
                        detected = True
                        tech_evidence.append(f"HTML pattern: {html_sig}")

            if detected:
                technologies.append(tech)
                evidence.append({"technology": tech, "evidence": tech_evidence})

        # Analyze headers for security
        for header_name, header_value in response.headers.items():
            headers_analysis[header_name] = header_value

        # Analyze cookies
        for cookie in response.cookies.jar:
            cookie_info = {
                "name": cookie.name,
                "secure": cookie.secure,
                "httponly": "httponly" in str(cookie).lower(),
                "samesite": "unknown",
            }
            cookies_analysis.append(cookie_info)

        # Extract version info from HTML
        versions = {}
        version_patterns = [
            (r'jquery[.-]?(\d+\.\d+\.\d+)', "jQuery"),
            (r'bootstrap[.-]?(\d+\.\d+\.\d+)', "Bootstrap"),
            (r'react[.-]?(\d+\.\d+\.\d+)', "React"),
            (r'vue[.-]?(\d+\.\d+\.\d+)', "Vue.js"),
            (r'angular[.-]?(\d+\.\d+\.\d+)', "Angular"),
        ]
        for pattern, tech in version_patterns:
            match = re.search(pattern, html)
            if match:
                versions[tech] = match.group(1)

        return {
            "url": str(response.url),
            "status_code": response.status_code,
            "technologies": sorted(set(technologies)),
            "versions": versions,
            "evidence": evidence,
            "headers": headers_analysis,
            "cookies": cookies_analysis,
            "server": response.headers.get("server", "Unknown"),
            "content_type": response.headers.get("content-type", "Unknown"),
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "url": url}


def main():
    parser = argparse.ArgumentParser(description="Technology detection")
    parser.add_argument("--url", required=True, help="Target URL")

    args = parser.parse_args()

    try:
        result = detect_technologies(url=args.url)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "type": type(e).__name__}))
        sys.exit(1)


if __name__ == "__main__":
    main()
