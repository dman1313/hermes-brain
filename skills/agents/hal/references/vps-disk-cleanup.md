# VPS Disk Cleanup Playbook

When `df -h /` shows >80% usage, run this sequence. Tested 2026-06-14: freed 25GB (87% → 54%).

## Quick Wins (always safe)

```bash
# 1. UV package cache (often 5GB+)
uv cache prune
rm -rf ~/.cache/uv/archive-v0  # aggressive — uv re-downloads as needed

# 2. APT cache
sudo apt-get clean && sudo apt-get autoremove -y

# 3. Journal logs
sudo journalctl --vacuum-size=50M

# 4. Temp files
rm -rf /tmp/hermes-results /tmp/node-compile-cache /tmp/tsx-*

# 5. Stale caches (safe to remove, recreated on demand)
rm -rf ~/.cache/electron ~/.cache/ort.pyke.io ~/.cache/node-gyp
```

## Docker Cleanup

```bash
# Check what's running vs dead
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

# Remove stopped containers
docker container prune -f

# Remove unused images (not tied to running containers)
docker image prune -f

# Remove unused volumes
docker volume prune -f

# Nuclear: remove specific images by name
docker rmi <image-name>
```

## Project Cleanup

```bash
# Find disk hogs
du -sh ~/[a-z]*/ 2>/dev/null | sort -rh | head -20

# Before removing, check if MCP servers or services depend on the directory
grep -r "dirname" ~/.hermes/config.yaml

# Remove with rm -rf (use sudo for go/pkg/mod permission issues)
sudo rm -rf ~/project-name
```

## What to Keep vs Remove

**Keep:** Active trading projects, newsletter pipeline, hermes-office, agent-memory vault, hermes-brain (NotebookLM), codegraph

**Remove:** Dead projects, unused Docker stacks, stale experiment directories, cached models no longer needed, old Go module caches

## HuggingFace Cache

```bash
# Check what's cached
du -sh ~/.cache/huggingface/hub/*

# Remove specific models
rm -rf ~/.cache/huggingface/hub/models--<org>--<model-name>
```

## Results from 2026-06-14 Cleanup

| Item | Size Freed |
|------|-----------|
| Docker (WeKnora app + images + volumes) | ~10GB |
| Go installation | 657MB |
| UV cache archives | 5.3GB |
| Headroom project | 6.2GB |
| Ruflo source (MCP runs from npx) | 3.2GB |
| Open-design, symphony, misc projects | ~4GB |
| HuggingFace whisper model | 1.6GB |
| Apt cache, journals, misc | ~400MB |
| **Total** | **~25GB** |
