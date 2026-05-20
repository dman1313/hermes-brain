---
name: school-bot-builder
title: SchoolBot Builder — AI Admissions Bot for Private Schools (Japan)
description: Build and deploy a bilingual (EN/JP) AI admissions chatbot for private English schools in Japan. Includes lead capture, tour scheduling, demo/sales page, and admin dashboard. One-day deploy. ¥50K-150K/month pricing.
---

# SchoolBot Builder

## When to Use
The user wants to build an AI admissions/FAQ bot for a private English school in Japan (or any bilingual school). Goal: generate leads, book tours, be sellable this week.

## Project Structure
```
~/human-good-ai/school-bot/
├── app.py                    # Flask app — routing, NLP, API
├── data/knowledge_base.json  # School info, FAQ, tour slots, tuition
├── templates/
│   ├── chat.html             # Chat widget UI (bilingual)
│   ├── demo.html             # Sales/demo page for school admins
│   └── admin.html            # Lead & tour booking dashboard
└── requirements.txt          # flask only (minimal deps)
```

## Step 1: Clone Template
```bash
mkdir -p ~/human-good-ai/school-bot/{static,templates,data}
```

## Step 2: Create Knowledge Base
Write `data/knowledge_base.json` with this structure:
```json
{
  "school": {"name": "...", "ages": "2-6", "location": "Shibuya-ku, Tokyo"},
  "faqs": [{"question": "...", "answer": "...", "intent": "tuition"}],
  "tour_slots": ["Mon 10:00", "Wed 14:00", "Fri 10:00"],
  "tuition": {"annual": "¥1,200,000 - ¥2,500,000", "enrollment": "¥150,000"}
}
```

## Step 3: Build app.py
- Flask server, port 8580
- `/` → chat widget
- `/demo` → sales page (for school to preview)
- `/admin` → lead dashboard (password: `schooladmin2026`)
- `POST /api/chat` → returns `{response, intent, language, suggestions}`
- `POST /api/lead-capture` → captures name, email, phone, intent
- `POST /api/book-tour` → books tour slot, returns confirmation
- `GET /api/leads` → returns all leads (JSON)

### Intent Classification (in order of priority)
Use `re.search()` with patterns. Do NOT use `\b` word boundaries for Japanese/CJK patterns — use plain `re.search()`:
1. greeting — loose match on short hello/greeting patterns
2. tour_booking — tour, visit, 見学, 見学したい
3. tuition — tuition, fee, cost, 学費, 料金, tuition, expensive
4. programs — program, class, course, クラス, プログラム
5. admissions — enroll, apply, admission, 入学, 申込
6. schedule — hours, schedule, open, 時間, 営業
7. english_support — english, bilingual, language, 英語
8. safety — safety, security, 安全
9. lunch — lunch, meal, 給食, ランチ
10. location — location, address, access, station, どこ
11. contact — contact, call, email, 連絡
12. after_kindergarten — after, elementary, primary, 卒園
13. general (fallback)

### Language Detection
```python
def detect_language(text):
    """Returns 'ja' or 'en' based on CJK character presence."""
    cjk_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u30ff' or '\u30a0' <= c <= '\u30ff')
    return "ja" if cjk_count > 2 else "en"
```

### Response Engine
- For each intent, provide both EN and JP response strings
- Use the detected language to pick the right response
- Include markdown formatting (bold, line breaks, lists)
- Append 3-5 contextual suggestion buttons per intent

## Step 4: Templates
- `chat.html`: embedded chat widget with quick reply buttons, tour booking modal, lead capture form
- `demo.html`: sales page with live bot preview, feature table, pricing tiers, CTA
- `admin.html`: simple password-protected lead dashboard (pass: `schooladmin2026`)

## Step 5: Deploy Options
### Option A: Render (fastest)
```bash
# Create render.yaml or deploy via Render Dashboard
# Set build command: pip install -r requirements.txt
# Set start command: gunicorn app:app --bind 0.0.0.0:$PORT
```

### Option B: VPS with Caddy/nginx
```bash
# Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy

# Caddyfile
schoolbot.humangood.ai {
    reverse_proxy localhost:8580
}

# Run with systemd
sudo systemctl enable caddy && sudo systemctl start caddy
```

## Step 6: Test
```bash
pip install flask
cd ~/human-good-ai/school-bot && python3 app.py
# Test endpoints:
curl http://localhost:8580/api/chat -X POST -H 'Content-Type: application/json' -d '{"message":"How much is tuition?"}'
curl http://localhost:8580/api/chat -X POST -H 'Content-Type: application/json' -d '{"message":"学費はいくらですか？"}'
```

## Pricing Tiers (for client sales)
| Tier | Price | Features |
|------|-------|----------|
| Starter | ¥50K/month | Website embed, email leads only, 5 leads/mo |
| Growth | ¥100K/month | SMS+email, 20 leads/mo, tour scheduling |
| Enterprise | ¥150K/month | Unlimited leads, custom branding, analytics dashboard |

## Sales Script (DMs)
> "Hi [name] — I built an AI admissions bot for international schools. It answers parent questions in English & Japanese 24/7, books tours automatically, and captures leads. Your website could be enrolling kids while you sleep. Free 1-week trial. Want to see a demo?"

## Pitfalls
- `\b` word boundary in Python `re` does NOT work with CJK characters (they're not `\w`). Always use plain `re.search()` without `\b` for Japanese patterns.
- Flask session `sid` is not a thing. Use `session.get("id", "anon")` instead.
- Make intent classifier **last to match, first to check** — put greeting FIRST, general as LAST fallback.
- Knowledge base must be editable by non-technical school staff — use simple JSON, not a database.
- For full test coverage, test: EN greeting, EN tuition, EN tour, EN location, EN programs, EN contact, JP tuition, JP tour, JP lunch, JP admissions, EN after-K.
