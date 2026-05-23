# Installing Go via Snap (Ubuntu 24.04)

## Problem
Ubuntu 24.04 apt repos ship Go 1.22. Many modern Go tools require 1.24+ (cli-printing-press needs 1.26.3+). The `go install` command fails with compile errors if the compiler is too old.

## Solution: Snap

```bash
# Check available channels
snap info go

# Install latest in the 1.26 track (classic confinement required)
sudo snap install go --channel=1.26/stable --classic

# Verify
go version  # go1.26.3 linux/amd64
```

Snap automatically adds Go to PATH. No manual GOPATH setup needed.

## GOPATH Binary Path

`go install` places binaries in `~/go/bin/`. Add to PATH permanently:

```bash
echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
```

## Snap Channel Pinning

The `1.26/stable` channel ensures you stay on the 1.26.x line. Other channels available:

| Channel | Version | Notes |
|---------|---------|-------|
| `latest/stable` | 1.26.2 | Slightly behind 1.26 track |
| `1.26/stable` | 1.26.3 | Recommended — latest patch |
| `1.26/edge` | 1.26.0 | Avoid for production |
