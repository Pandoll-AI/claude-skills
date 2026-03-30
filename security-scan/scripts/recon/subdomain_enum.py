#!/usr/bin/env python3
"""
Subdomain enumeration using DNS and certificate transparency.

Usage:
  python subdomain_enum.py --domain example.com
  python subdomain_enum.py --domain example.com --use-crtsh
  python subdomain_enum.py --domain example.com --wordlist common_subs.txt

Output: JSON with subdomains, resolved IPs, sources
"""

import argparse
import asyncio
import json
import sys


async def enumerate_subdomains(
    domain: str,
    use_crtsh: bool = True,
    wordlist_path: str | None = None,
    resolve_dns: bool = True,
) -> dict:
    """Enumerate subdomains for a domain."""
    import httpx

    subdomains = set()
    sources = {}

    # 1. Certificate Transparency via crt.sh
    if use_crtsh:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"https://crt.sh/?q=%.{domain}&output=json"
                )
                if response.status_code == 200:
                    certs = response.json()
                    for cert in certs:
                        name = cert.get("name_value", "")
                        for sub in name.split("\n"):
                            sub = sub.strip().lower()
                            if sub.endswith(domain) and "*" not in sub:
                                subdomains.add(sub)
                                sources[sub] = sources.get(sub, []) + ["crt.sh"]
        except Exception as e:
            sources["_crtsh_error"] = str(e)

    # 2. Common subdomain wordlist
    common_subs = [
        "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "ns2",
        "ns3", "ns4", "dns1", "dns2", "vpn", "admin", "api", "dev", "staging",
        "test", "beta", "demo", "app", "apps", "m", "mobile", "secure", "shop",
        "store", "blog", "portal", "gateway", "cdn", "static", "assets", "img",
        "images", "media", "video", "audio", "docs", "help", "support", "status",
        "monitor", "metrics", "grafana", "kibana", "jenkins", "gitlab", "git",
        "svn", "hg", "repo", "repository", "backup", "db", "database", "mysql",
        "postgres", "redis", "mongo", "elastic", "search", "solr", "queue",
        "mq", "rabbitmq", "kafka", "zookeeper", "consul", "vault", "auth",
        "login", "sso", "oauth", "iam", "identity", "accounts", "users",
        "customer", "client", "partner", "internal", "intranet", "extranet",
        "corp", "corporate", "office", "remote", "cloud", "aws", "gcp", "azure",
    ]

    # 3. Custom wordlist
    if wordlist_path:
        try:
            with open(wordlist_path) as f:
                for line in f:
                    word = line.strip().lower()
                    if word and not word.startswith("#"):
                        common_subs.append(word)
        except FileNotFoundError:
            sources["_wordlist_error"] = f"File not found: {wordlist_path}"

    # Add common subdomains
    for sub in common_subs:
        full_domain = f"{sub}.{domain}"
        subdomains.add(full_domain)
        sources[full_domain] = sources.get(full_domain, []) + ["wordlist"]

    # 4. DNS resolution
    resolved = {}
    if resolve_dns:
        import dns.resolver

        resolver = dns.resolver.Resolver()
        resolver.timeout = 2
        resolver.lifetime = 2

        async def resolve_domain(subdomain: str) -> tuple[str, list | None]:
            try:
                loop = asyncio.get_event_loop()
                answers = await loop.run_in_executor(
                    None, lambda: resolver.resolve(subdomain, "A")
                )
                return subdomain, [str(rdata) for rdata in answers]
            except Exception:
                return subdomain, None

        tasks = [resolve_domain(sub) for sub in subdomains]
        results = await asyncio.gather(*tasks)

        for subdomain, ips in results:
            if ips:
                resolved[subdomain] = ips

    # Filter to only resolved subdomains
    valid_subdomains = sorted(resolved.keys()) if resolve_dns else sorted(subdomains)

    return {
        "domain": domain,
        "total_found": len(subdomains),
        "resolved_count": len(resolved),
        "subdomains": valid_subdomains,
        "resolved_ips": resolved,
        "sources": {k: v for k, v in sources.items() if not k.startswith("_")},
        "errors": {k: v for k, v in sources.items() if k.startswith("_")},
    }


def main():
    parser = argparse.ArgumentParser(description="Subdomain enumeration")
    parser.add_argument("--domain", required=True, help="Target domain")
    parser.add_argument(
        "--use-crtsh",
        action="store_true",
        default=True,
        help="Use crt.sh certificate transparency (default: True)",
    )
    parser.add_argument(
        "--no-crtsh",
        action="store_true",
        help="Disable crt.sh lookup",
    )
    parser.add_argument("--wordlist", help="Custom wordlist file")
    parser.add_argument(
        "--no-resolve",
        action="store_true",
        help="Skip DNS resolution",
    )

    args = parser.parse_args()

    try:
        result = asyncio.run(
            enumerate_subdomains(
                domain=args.domain,
                use_crtsh=not args.no_crtsh,
                wordlist_path=args.wordlist,
                resolve_dns=not args.no_resolve,
            )
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "type": type(e).__name__}))
        sys.exit(1)


if __name__ == "__main__":
    main()
