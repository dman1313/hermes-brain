# Agent Reach Channel States (2026-04-30, VPS server)

## Final State After Install

8/16 channels fully active. All software dependencies installed.

### ✅ Working (no auth needed)
| Channel | Tool | Status |
|---------|------|--------|
| YouTube | yt-dlp | ✅ |
| RSS/Atom | feedparser | ✅ |
| V2EX | API | ✅ |
| WeChat Articles | Exa + Camoufox | ✅ |
| Exa Search | mcporter | ✅ |
| Web Pages | Jina Reader | ✅ |
| Bilibili | yt-dlp + bili-cli | ✅ |
| Weibo | mcp-server-weibo | ✅ |

### ⚠️ Needs Auth
| Channel | Tool | What's Needed |
|---------|------|---------------|
| GitHub | gh CLI (v2.76.0) | `gh auth login` |
| Reddit | rdt-cli (v0.4.1) | Cookie or `rdt login` |

### 🔒 Needs User Credentials
| Channel | Tool | What's Needed |
|---------|------|---------------|
| Twitter/X | twitter-cli | Browser cookie (Cookie-Editor export) |
| XiaoHongShu | xhs-cli | `xhs login` or cookie |
| Xiaoyuzhou | transcribe.sh | Groq API key (free: console.groq.com) |
| Xueqiu | CLI | Browser cookie |
| Douyin | douyin-mcp-server (v1.2.1) | MCP service start |
| LinkedIn | linkedin-scraper-mcp | Install + browser login |

## Install Commands Used

```bash
# Core
pip install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto

# Fixes
curl -fsSL https://github.com/cli/cli/releases/download/v2.76.0/gh_2.76.0_linux_amd64.tar.gz -o /tmp/gh.tar.gz
tar -xzf /tmp/gh.tar.gz -C /tmp && cp /tmp/gh_*/bin/gh ~/.local/bin/
pip install 'rdt-cli>=0.4.0'
sudo apt install -y ffmpeg

# All channels
pip install douyin-mcp-server
agent-reach install --env=auto --channels=all
```

## RDT-CLI Version Note
As of 2026-04-30, PyPI has rdt-cli up to v0.4.1. The Agent Reach guide says `>=0.4.2` but that version isn't published yet.
Use `pip install 'rdt-cli>=0.4.0'` instead.
