#!/usr/bin/env python3
"""
MCP Course Warmup Script
─────────────────────────
Pre-loads every expensive resource used by the MCP course labs so that
first-run latency is absorbed here instead of during a live demo.

What gets warmed up (in parallel where possible):
  1. Ollama  – verifies the server is reachable, then forces llama3.2
               into GPU/CPU memory with a throwaway inference call.
  2. SentenceTransformer – downloads / loads the all-MiniLM-L6-v2
               embedding model (heaviest Python-side cold start).
  3. ChromaDB – creates an ephemeral client so the native lib is loaded.
  4. FastMCP + LangChain imports – imports the libraries so first
               `import` in lab code is a no-op.

Parallelism strategy:
  • Ollama inference and SentenceTransformer loading are the two
    slowest steps and are independent, so they run concurrently in
    separate threads.
  • ChromaDB and library imports are fast (<0.5 s each) and run
    sequentially after the heavy work finishes.
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
    Load the SentenceTransformer embedding model used by the MCP
    servers (mcp_server_solution, mcp_server_support_solution,
    mcp_server_classification, index_pdfs).

    First load downloads ~80 MB; subsequent loads read from the
    HuggingFace cache in ~1-3 s.
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


def warmup_chromadb() -> bool:
    """Import and initialize an ephemeral ChromaDB client."""
    try:
        t0 = time.time()
        import chromadb
        _ = chromadb.EphemeralClient()
        dt = time.time() - t0
        print(f"  {GREEN}✓ ChromaDB ready ({dt:.1f}s){RESET}")
        return True
    except Exception as e:
        print(f"  {RED}✗ ChromaDB warmup failed: {e}{RESET}")
        return False


def warmup_library_imports() -> bool:
    """
    Import the key libraries used across the labs so that Python's
    import cache is primed.  This covers:
      • fastmcp  (FastMCP server + Client)
      • langchain_ollama (ChatOllama for agents)
      • langchain_mcp_adapters (MultiServerMCPClient)
      • langgraph (agent graph runtime)
    """
    try:
        t0 = time.time()
        failures = []

        for mod_name in (
            "fastmcp",
            "langchain_ollama",
            "langchain_mcp_adapters",
            "langgraph",
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
        print(f"{RED}  Ollama is required. Start it with:  ollama serve &{RESET}")
        print(f"{RED}  Then pull the model with:           ollama pull {OLLAMA_MODEL}{RESET}\n")

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
    results["ChromaDB"]  = warmup_chromadb()
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
