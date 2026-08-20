#!/usr/bin/env bash
# serveOllama.sh - start Ollama for the labs and actually warm the model.
# Runs at postStart, every time the container starts.
#
# Two things matter here, and the old setup did neither:
#
#   1. OLLAMA_KEEP_ALIVE=-1 on the process that SERVES. Ollama's default is to
#      unload a model 5 minutes after its last use. Students spend well over
#      5 minutes on Lab 1 steps 1-10, so without this the model is cold again
#      by the time they run the agent in step 11.
#
#   2. A real inference call. `ollama pull` only copies weights to disk;
#      nothing is in RAM until something asks the model to generate. One tiny
#      request pays that cost during setup instead of during the lab.
set -uo pipefail

MODEL="llama3.2"   # must match MODEL in lab1/agent_helpers.py

pgrep -x ollama >/dev/null 2>&1 || {
  OLLAMA_KEEP_ALIVE=-1 nohup ollama serve >/tmp/ollama.log 2>&1 &
}

for _ in $(seq 1 30); do
  curl -sf http://localhost:11434/api/tags >/dev/null 2>&1 && break
  sleep 1
done

# Warm it: load the weights and keep them resident. Measured at ~5s on a
# 4-core codespace, so run it synchronously - backgrounding it does not
# survive postStart and the model stays cold.
curl -sf --max-time 180 http://localhost:11434/api/chat \
  -H 'Content-Type: application/json' \
  -d "{\"model\":\"${MODEL}\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"stream\":false,\"keep_alive\":-1}" \
  >/tmp/ollama-warm.log 2>&1 || echo 'warm-up failed' >&2

exit 0
