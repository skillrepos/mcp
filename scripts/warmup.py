#!/usr/bin/env python3
"""
MCP Course Warmup Script
─────────────────────────
Pre-loads every expensive resource used by the MCP course labs so that
first-run latency is absorbed here instead of during a live demo.

What gets warmed up (in parallel where possible):
  1. Ollama  – verifies the server is reachable, then forces llama3.2
               into memory with a throwaway inference call and pins it
               there (keep_alive=-1). This is the one that matters: the
               Lab 1 and Lab 3 agents both call this model.
  2. SentenceTransformer – loads the all-MiniLM-L6-v2 embedding model.
               None of the five core labs use it; it is here for the
               optional/extended material that ships in `extra/`.
  3. Lab library imports – imports fastmcp, mcp and friends so the
               first `import` in lab code is a no-op.

Parallelism strategy:
  • Ollama inference and SentenceTransformer loading are the two
    slowest steps and are independent, so they run concurrently in
    separate threads.
  • Library imports are fast (<0.5 s) and run after the heavy work.

NOTE: scripts/serveOllama.sh already starts and warms Ollama at
container start, so this script is belt-and-braces for the LLM. It is
still useful after a long idle gap or on a local (non-Codespace) setup.
"""

from __future__ import annotations

import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

# ── ANSI helpers ─────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

OLLAMA_MODEL   = "llama3.2"
EMBED_MODEL    = "all-MiniLM-L6-v2"
OLLAMA_BASE    = "http://127.0.0.1:11434"

# ── Individual warmup functions ──────────────────────────────────────

def check_ollama() -> bool:
    """Verify that the Ollama daemon is reachable."""
    import requests
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        r.raise_for_status()
        models = [m["name"] for m in r.json().get("models", [])]
        if not any(OLLAMA_MODEL in m for m in models):
            print(f"  {YELLOW}⚠  Model '{OLLAMA_MODEL}' not found locally – "
                  f"pull it with:  ollama pull {OLLAMA_MODEL}{RESET}")
            return False
        return True
    except Exception as e:
        print(f"  {RED}✗ Ollama not reachable ({e}){RESET}")
        return False


def warmup_ollama_inference() -> bool:
    """
    Force Ollama to load llama3.2 into memory by running a tiny
    inference call.  This is the single most impactful warmup step
    because loading the model from disk into GPU/CPU takes 5-15 s on
    first call, but is instant on every subsequent call while the
    model stays resident.
    """
    try:
        print(f"  {CYAN}Loading {OLLAMA_MODEL} into Ollama memory …{RESET}")
        t0 = time.time()

        import requests
        resp = requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": "hi"}],
                "stream": False,
                "keep_alive": -1,                # stay resident, as serveOllama.sh does
                "options": {"num_predict": 1},   # generate exactly 1 token
            },
            timeout=120,
        )
        resp.raise_for_status()

        dt = time.time() - t0
        print(f"  {GREEN}✓ {OLLAMA_MODEL} loaded in Ollama ({dt:.1f}s){RESET}")
        return True
    except Exception as e:
        print(f"  {RED}✗ Ollama inference warmup failed: {e}{RESET}")
        return False


def warmup_embedding_model() -> bool:
    """
    Load the SentenceTransformer embedding model.

    No lab in labs.md uses embeddings - this is for the optional and
    retired material under `extra/`. The devcontainer image pre-downloads
    the model, so this is a ~1-3 s cache read there; on a local setup the
    first load downloads ~80 MB.
    """
    try:
        print(f"  {CYAN}Loading embedding model ({EMBED_MODEL})…{RESET}")
        t0 = time.time()

        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(EMBED_MODEL)

        # Run a tiny encode to fully initialize ONNX / torch backend
        _ = model.encode("warmup", show_progress_bar=False)

        dt = time.time() - t0
        print(f"  {GREEN}✓ Embedding model ready ({dt:.1f}s){RESET}")
        return True
    except Exception as e:
        print(f"  {RED}✗ Embedding model warmup failed: {e}{RESET}")
        return False


def warmup_library_imports() -> bool:
    """
    Import the key libraries used across the labs so that Python's
    import cache is primed.  This covers:
      • fastmcp   (FastMCP server + Client - every lab)
      • mcp       (the MCP Python SDK underneath it)
      • httpx     (the agents' HTTP client)
      • fastapi / uvicorn (lab5 auth server, the Explorer)
      • jose      (JWT handling in lab5)

    The langchain packages are deliberately absent: langchain_mcp_adapters
    imports mcp.server.fastmcp, a module deleted in MCP Python SDK v2, so
    it cannot be installed alongside this stack. See requirements.txt.
    """
    try:
        t0 = time.time()
        failures = []

        for mod_name in (
            "fastmcp",
            "mcp",
            "httpx",
            "fastapi",
            "uvicorn",
            "jose",
        ):
            try:
                __import__(mod_name)
            except ImportError:
                failures.append(mod_name)

        dt = time.time() - t0

        if failures:
            print(f"  {YELLOW}⚠  Missing optional packages: {', '.join(failures)} ({dt:.1f}s){RESET}")
        else:
            print(f"  {GREEN}✓ Library imports cached ({dt:.1f}s){RESET}")
        # Treat missing optional libs as non-fatal
        return True
    except Exception as e:
        print(f"  {RED}✗ Library import warmup failed: {e}{RESET}")
        return False


# ── Orchestrator ─────────────────────────────────────────────────────

def _run_timed(label: str, fn: Callable[[], bool]) -> tuple[str, bool, float]:
    """Run *fn*, return (label, success, elapsed)."""
    t0 = time.time()
    ok = fn()
    return label, ok, time.time() - t0


def main() -> None:
    print(f"\n{BOLD}{CYAN}═══  MCP Course Warmup  ═══{RESET}")
    print(f"{DIM}Pre-loading models and libraries for all labs{RESET}\n")

    total_t0 = time.time()

    # ── Phase 1: Ollama health check (fast, must pass before inference) ──
    print(f"{YELLOW}Phase 1 ▸ Checking Ollama server …{RESET}")
    ollama_ok = check_ollama()
    if not ollama_ok:
        print(f"{RED}  Ollama is required. Start and warm it with:  bash scripts/serveOllama.sh{RESET}")
        print(f"{RED}  If the model is missing, pull it first with:  bash scripts/startOllama.sh{RESET}\n")

    # ── Phase 2: Heavy loads in parallel ─────────────────────────────
    print(f"\n{YELLOW}Phase 2 ▸ Loading models (parallel) …{RESET}")
    results: dict[str, bool] = {}

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = []
        if ollama_ok:
            futures.append(pool.submit(_run_timed, "Ollama LLM", warmup_ollama_inference))
        futures.append(pool.submit(_run_timed, "Embeddings", warmup_embedding_model))

        for fut in as_completed(futures):
            label, ok, elapsed = fut.result()
            results[label] = ok

    # ── Phase 3: Fast follow-ups (sequential is fine) ────────────────
    print(f"\n{YELLOW}Phase 3 ▸ Loading supporting libraries …{RESET}")
    results["Libraries"] = warmup_library_imports()

    # ── Summary ──────────────────────────────────────────────────────
    total_dt = time.time() - total_t0
    passed = sum(1 for v in results.values() if v)
    total  = len(results)

    print(f"\n{'═' * 44}")
    print(f"{BOLD}Warmup Summary{RESET}")
    for label, ok in results.items():
        icon = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
        print(f"  {icon}  {label}")
    print(f"\n  {passed}/{total} components ready  •  {total_dt:.1f}s total")

    if passed >= total - 1:
        print(f"\n{GREEN}{BOLD}✓ MCP course environment is warmed up!{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{YELLOW}Some components failed — labs may still work "
              f"but expect slower first runs.{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
