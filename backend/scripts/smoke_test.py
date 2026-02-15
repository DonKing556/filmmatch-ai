#!/usr/bin/env python3
"""Pre-launch smoke test.

Verifies that all critical services and endpoints are operational.
Run this after deployment to validate the system before opening to traffic.

Usage:
    python scripts/smoke_test.py [--base-url http://localhost:8000]
"""

import argparse
import sys
import time

import httpx

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def check(name: str, passed: bool, detail: str = "") -> bool:
    icon = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
    suffix = f" — {detail}" if detail else ""
    print(f"  [{icon}] {name}{suffix}")
    return passed


def main():
    parser = argparse.ArgumentParser(description="FilmMatch AI Smoke Test")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the backend API",
    )
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    print(f"\n{'='*60}")
    print(f"  FilmMatch AI — Pre-Launch Smoke Test")
    print(f"  Target: {base}")
    print(f"{'='*60}\n")

    client = httpx.Client(timeout=15.0)
    results: list[bool] = []

    # 1. Health endpoint
    print("1. Core Health")
    try:
        r = client.get(f"{base}/api/v1/health")
        data = r.json()
        results.append(check("Health endpoint", r.status_code == 200))
        results.append(check("Environment set", bool(data.get("environment")), data.get("environment", "")))
    except Exception as e:
        results.append(check("Health endpoint", False, str(e)))

    # 2. Readiness (dependency checks)
    print("\n2. Dependencies")
    try:
        r = client.get(f"{base}/api/v1/ops/readiness")
        data = r.json()
        checks = data.get("checks", {})
        for dep, status in checks.items():
            results.append(check(f"{dep} connection", status == "ok", status))
        results.append(check("Overall readiness", data.get("ready", False)))
    except Exception as e:
        results.append(check("Readiness endpoint", False, str(e)))

    # 3. TMDB connectivity (via trending)
    print("\n3. External Services")
    try:
        r = client.get(f"{base}/api/v1/movies/trending")
        if r.status_code == 200:
            movies = r.json()
            results.append(check("TMDB trending", len(movies) > 0, f"{len(movies)} movies"))
        else:
            results.append(check("TMDB trending", False, f"HTTP {r.status_code}"))
    except Exception as e:
        results.append(check("TMDB trending", False, str(e)))

    # 4. Metrics endpoint
    print("\n4. Monitoring")
    try:
        r = client.get(f"{base}/metrics")
        results.append(check("Prometheus /metrics", r.status_code == 200))
    except Exception as e:
        results.append(check("Prometheus /metrics", False, str(e)))

    # 5. Rate limiting headers
    print("\n5. Security")
    try:
        r = client.get(f"{base}/api/v1/movies/trending")
        has_rl = "x-ratelimit-limit" in r.headers
        results.append(check("Rate limit headers", has_rl, r.headers.get("x-ratelimit-limit", "missing")))
    except Exception as e:
        results.append(check("Rate limit headers", False, str(e)))

    try:
        r = client.get(f"{base}/api/v1/health")
        has_rid = "x-request-id" in r.headers
        results.append(check("Request ID header", has_rid))
    except Exception as e:
        results.append(check("Request ID header", False, str(e)))

    # 6. Cache warmup
    print("\n6. Cache Warmup")
    try:
        r = client.post(f"{base}/api/v1/ops/warmup")
        if r.status_code == 200:
            data = r.json()
            results.append(check(
                "Warmup executed",
                data.get("trending", 0) > 0,
                f"{data.get('trending', 0)} trending, {data.get('enriched', 0)} enriched",
            ))
        else:
            results.append(check("Warmup executed", False, f"HTTP {r.status_code}"))
    except Exception as e:
        results.append(check("Warmup executed", False, str(e)))

    # Summary
    passed = sum(results)
    total = len(results)
    failed = total - passed

    print(f"\n{'='*60}")
    if failed == 0:
        print(f"  {GREEN}ALL {total} CHECKS PASSED{RESET}")
        print(f"  System is ready for launch!")
    else:
        print(f"  {YELLOW}{passed}/{total} checks passed, {RED}{failed} failed{RESET}")
        print(f"  Fix failures before launching.")
    print(f"{'='*60}\n")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
