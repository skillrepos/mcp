#!/usr/bin/env python3
"""
warmup.py – Pre-warm all Ollama models used in the MCP course labs.

Sends a short prompt to each model so that Ollama loads the weights into
memory before students start the labs.  This avoids long cold-start delays
during interactive exercises.

Usage:
    python scripts/warmup.py               # warm up all models
    python scripts/warmup.py --list        # just list models, don't warm up
    python scripts/warmup.py --timeout 600 # custom read timeout (seconds)

Models are discovered from a single registry list below.  When new models
are added to any lab, add them here too.
"""

import argparse
import sys
import time

try:
    import httpx
except ImportError:
    sys.exit(
        "httpx is required but not installed.\n"
        "Install it with:  pip install httpx"
    )

# ── Ollama endpoint ──────────────────────────────────────────────────────
OLLAMA_URL = "http://127.0.0.1:11434"
CHAT_URL   = f"{OLLAMA_URL}/api/chat"

# ── Model registry ───────────────────────────────────────────────────────
# Every model used across all labs should appear here.
# Format:  (model_tag, description_of_where_its_used)
MODELS = [
    ("llama3.2:latest", "Lab 1 agent (ChatOllama), Lab 4 client-agent, MCP server resource"),
]


# ── ANSI colors ──────────────────────────────────────────────────────────
BLUE   = "\033[94m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
RESET  = "\033[0m"


def check_ollama_running(timeout: float = 5.0) -> bool:
    """Return True if the Ollama server is reachable."""
    try:
        resp = httpx.get(OLLAMA_URL, timeout=timeout)
        return resp.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


def list_local_models(timeout: float = 10.0) -> list[str]:
    """Return tags of models already pulled locally."""
    try:
        resp = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=timeout)
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        return []


def warm_up_model(model: str, read_timeout: float = 300.0) -> tuple[bool, float, str]:
    """
    Send a tiny chat request to force Ollama to load the model.

    Returns (success, elapsed_seconds, detail_message).
    """
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Reply with the single word 'ready'."},
        ],
        "stream": False,
    }

    timeout = httpx.Timeout(connect=30.0, read=read_timeout, write=30.0, pool=30.0)
    start = time.time()

    try:
        resp = httpx.post(CHAT_URL, json=payload, timeout=timeout)
        elapsed = time.time() - start
        resp.raise_for_status()

        data = resp.json()
        content = ""
        if isinstance(data, dict) and "message" in data:
            content = data["message"].get("content", "")

        return True, elapsed, content.strip()

    except httpx.TimeoutException:
        return False, time.time() - start, "Timed out waiting for model response"
    except httpx.ConnectError:
        return False, time.time() - start, "Could not connect to Ollama"
    except httpx.HTTPStatusError as exc:
        return False, time.time() - start, f"HTTP {exc.response.status_code}: {exc.response.text[:200]}"
    except Exception as exc:
        return False, time.time() - start, f"{type(exc).__name__}: {exc}"


def main():
    parser = argparse.ArgumentParser(
        description="Warm up Ollama models used in the MCP training course."
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List the models that would be warmed up, then exit.",
    )
    parser.add_argument(
        "--timeout", type=float, default=300.0,
        help="Read timeout in seconds per model (default: 300).",
    )
    args = parser.parse_args()

    # ── List mode ────────────────────────────────────────────────────────
    if args.list:
        print(f"\n{BLUE}Models used in MCP course labs:{RESET}\n")
        for tag, where in MODELS:
            print(f"  • {tag:25s}  ({where})")
        print()
        return

    # ── Pre-flight checks ────────────────────────────────────────────────
    print(f"\n{BLUE}{'='*60}")
    print(f"  Ollama Model Warm-Up for MCP Course Labs")
    print(f"{'='*60}{RESET}\n")

    if not check_ollama_running():
        print(f"{RED}✗ Ollama does not appear to be running at {OLLAMA_URL}")
        print(f"  Start it with:  ollama serve &{RESET}\n")
        sys.exit(1)

    print(f"{GREEN}✓ Ollama is running at {OLLAMA_URL}{RESET}\n")

    # Check which models are already pulled
    local_models = list_local_models()
    if local_models:
        print(f"{BLUE}Locally available models:{RESET}")
        for m in local_models:
            print(f"  • {m}")
        print()

    # ── Warm up each model ───────────────────────────────────────────────
    results = []
    for i, (tag, where) in enumerate(MODELS, 1):
        print(f"{BLUE}[{i}/{len(MODELS)}] Warming up {tag}...{RESET}")
        print(f"       Used in: {where}")

        # Check if model is pulled
        # Normalize tags for comparison (ollama may add :latest)
        tag_variants = {tag, tag.split(":")[0], tag.split(":")[0] + ":latest"}
        if local_models and not tag_variants & set(local_models):
            print(f"{YELLOW}  ⚠ Model '{tag}' not found locally. "
                  f"Pull it with: ollama pull {tag}{RESET}")
            results.append((tag, False, 0.0, "Not pulled locally"))
            continue

        ok, elapsed, detail = warm_up_model(tag, read_timeout=args.timeout)

        if ok:
            print(f"{GREEN}  ✓ Ready in {elapsed:.1f}s — response: {detail!r}{RESET}\n")
        else:
            print(f"{RED}  ✗ Failed after {elapsed:.1f}s — {detail}{RESET}\n")

        results.append((tag, ok, elapsed, detail))

    # ── Summary ──────────────────────────────────────────────────────────
    passed = sum(1 for _, ok, _, _ in results if ok)
    total  = len(results)

    print(f"{BLUE}{'='*60}")
    print(f"  Warm-Up Summary: {passed}/{total} models ready")
    print(f"{'='*60}{RESET}\n")

    for tag, ok, elapsed, detail in results:
        status = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
        print(f"  {status} {tag:25s}  {elapsed:6.1f}s  {detail[:50]}")

    print()

    if passed < total:
        print(f"{YELLOW}Some models failed to warm up. Students may experience "
              f"cold-start delays.{RESET}\n")
        sys.exit(1)
    else:
        print(f"{GREEN}All models are warm and ready for the labs!{RESET}\n")


if __name__ == "__main__":
    main()
