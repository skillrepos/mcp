# Dev Container Image Maintenance

The Codespaces dev container uses a pre-built Docker image hosted on GitHub Container Registry (GHCR) to avoid large downloads at startup. When certain files change, the image must be rebuilt and pushed.

## Image location

```
ghcr.io/skillrepos/mcp-devcontainer:latest
```

## What's baked into the image

| Component | How it got there |
|-----------|-----------------|
| Python 3 + venv | `apt-get install` |
| `/opt/py_env/` (full virtualenv) | CPU-only PyTorch installed first, then `pip install -r requirements.txt` |
| sentence-transformers embedding model | Pre-downloaded at build time |
| Ollama binary | Installed via `ollama.com/install.sh` (no model pulled) |
| zstd, curl, ca-certificates | `apt-get install` |

At codespace startup, `scripts/pysetup.sh` copies `/opt/py_env` to the workspace and fixes paths. No network downloads are needed.

## When to rebuild the image

Rebuild whenever you change any of these files:

| File changed | Why rebuild is needed |
|---|---|
| `.devcontainer/Dockerfile` | Image build instructions changed |
| `requirements.txt` | Python packages are pre-installed in `/opt/py_env` |
| Embedding model (in Dockerfile) | Model is pre-cached in the image |

Changes to these files do **not** require a rebuild:

- `.devcontainer/devcontainer.json` (VS Code settings, extensions, postCreateCommand)
- `scripts/pysetup.sh` (runs at startup, not at image build)
- Any Python source files (`.py`), data files, or docs

## How to rebuild and push

### Preferred: the GitHub Actions workflow

`.github/workflows/build-devcontainer.yml` builds and pushes the image on
GitHub's own amd64 runners. Use this unless you have a reason not to.

- **Manually:** Actions tab -> *Build devcontainer image* -> **Run workflow**.
- **Automatically:** it also fires on any push to `main` that touches
  `requirements.txt` or `.devcontainer/Dockerfile` - the two triggers listed
  above - so the image stops drifting from the repo on its own.

It authenticates with the automatic `GITHUB_TOKEN`, so there is no PAT to
manage and no `docker login`. Because the runner is amd64, the arm64 trap below
cannot happen. Every run publishes **two** tags: `:latest` and a dated
`:YYYY-MM-DD`, so a bad image can be rolled back by pointing
`devcontainer.json` at the previous date.

After building, the workflow pulls the image it just pushed and asserts the
baked venv matches `requirements.txt` (the `fastmcp` pin), that `ollama` is on
PATH, and that the embedding model is cached - so a green run means the image
is actually correct, not merely that the build exited 0.

**One-time setup:** the workflow needs the `skillrepos/mcp` repo to have write
access to the package. If the first run fails with `denied` or
`installation not allowed`, go to
`github.com/orgs/skillrepos/packages/container/mcp-devcontainer/settings` ->
**Manage Actions access** and add the repository with **Write** (the section
below covers the Read grants Codespaces needs to *pull*; publishing needs
Write).

### Fallback: build it by hand

Run from the repo root (the `COPY requirements.txt` in the Dockerfile needs the repo root as build context).

**You must specify `--platform linux/amd64`** — Codespaces runs on amd64. If you build on Apple Silicon (ARM) without this flag, the image will be arm64 and Codespaces will fail with "No manifest found."

```bash
# 1. Log in to GHCR (one-time, or when token expires)
docker login ghcr.io -u YOUR_GITHUB_USERNAME

# 2. Build the image (always specify platform)
docker build --platform linux/amd64 -f .devcontainer/Dockerfile -t ghcr.io/skillrepos/mcp-devcontainer:latest .

# 3. Push to GHCR
docker push ghcr.io/skillrepos/mcp-devcontainer:latest
```

Then commit and push your code changes (e.g. updated `requirements.txt`) so the repo and image stay in sync.

## Image size constraints

Free Codespaces have a 32GB storage limit. The image must fit within this along with the Codespaces system overhead (agent, VS Code server, mounts). To keep the image small:

- **Install CPU-only PyTorch first** (before `requirements.txt`) using `--index-url https://download.pytorch.org/whl/cpu`. This prevents pip from ever downloading the GPU variant.
- **Remove `triton`** — a ~1GB PyTorch dependency not needed for CPU inference. Include it in the `pip uninstall` list in the Dockerfile.
- **Remove all `nvidia-*` packages** — CUDA libraries are not usable in Codespaces.

- **Clean up test directories and .pyc files** to recover additional space.
- **Keep all installs and removals in the same `RUN` layer** — otherwise Docker preserves deleted files in earlier layers and the image stays large.

If a new dependency causes the image to exceed 32GB, check for unnecessary transitive dependencies (`pip show <package>`) and uninstall them in the Dockerfile.

## GHCR package visibility

Codespaces must be able to pull the image. There are two options:

### Option A: Make the package public

Go to: `github.com/orgs/skillrepos/packages/container/mcp-devcontainer/settings`

Under "Danger Zone", set visibility to **Public**. This may require org admin permissions.

### Option B: Grant repository access (for private packages)

If org restrictions prevent making the package public:

1. Go to the package settings page (same URL as above)
2. Under **"Manage Actions access"**, add the repository with **Read** access
3. Under **"Manage repository access"**, also add the repository with **Read** access

Both access grants are needed for Codespaces to authenticate the pull.

## Forked repos and prebuilds

Forked repos **cannot pull GHCR images** from the original org's private packages. Even if the image is public, forks should use the Dockerfile build approach for reliability.

### devcontainer.json for forks

Forks must use `"build"` instead of `"image"`, and **must include `"context": ".."`** because Codespaces uses `.devcontainer/` as the default build context, but the Dockerfile needs to `COPY` files (e.g. `requirements.txt`) from the repo root:

```jsonc
// For the original repo (pulls pre-built image — fast):
"image": "ghcr.io/ORG/IMAGE:latest",

// For forks or when GHCR image is unavailable (builds from Dockerfile):
"build": {
    "dockerfile": "Dockerfile",
    "context": ".."
},
```

Without `"context": ".."`, the build will fail with:
```
"/requirements.txt": not found
```

### Setting up prebuilds on a fork

1. In the forked repo, change `devcontainer.json` to use the `"build"` config shown above
2. Go to the fork's **Settings > Codespaces > Prebuilds > Set up prebuild**
3. Configure for the `main` branch and your preferred region
4. The prebuild will build the Dockerfile on GitHub's infra and cache the result
5. Subsequent codespace creations from the fork will use the cached prebuild

This is slower than pulling a pre-built image (~5-10 min for the initial prebuild) but only happens once. After the prebuild completes, users get fast startup.

### Keeping forks in sync

When the upstream repo updates dependency files or the Dockerfile:

1. Sync the fork with upstream
2. The prebuild will automatically re-trigger (if configured for "on push")
3. No need to rebuild or push any GHCR image — the fork builds its own

## Startup script considerations

If your `postCreateCommand` runs scripts that install packages (e.g., `pip install`), those commands must be **conditional** — they should only run when the pre-built venv is NOT available. Otherwise the script will re-download packages that are already baked into the image, defeating the purpose of pre-building.

Example pattern for a setup script:

```bash
if [ -d "/opt/py_env" ]; then
    # Fast path: copy pre-built venv from image
    cp -a /opt/py_env ./py_env
    # Fix hardcoded paths
    sed -i "s|/opt/py_env|$(pwd)/py_env|g" ./py_env/bin/activate
    sed -i "s|/opt/py_env|$(pwd)/py_env|g" ./py_env/bin/pip*
    sed -i "s|/opt/py_env|$(pwd)/py_env|g" ./py_env/pyvenv.cfg 2>/dev/null || true
else
    # Fallback: create venv and install from scratch
    python3 -m venv ./py_env
    pip install -r requirements.txt
fi
```

Any `pip install`, `pip install --upgrade`, or NVIDIA/CUDA cleanup commands must be inside the `else` block. If they run unconditionally after the copy, they will download new versions over the network on every codespace creation.

## Testing after a rebuild

1. Create a new codespace from the main branch
2. Confirm `py_env/` is populated and no `pip install` runs
3. Confirm `which ollama` returns `/usr/local/bin/ollama`
4. Confirm `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"` loads instantly (no download)
5. Check disk usage with `df -h` — ensure adequate free space remains
