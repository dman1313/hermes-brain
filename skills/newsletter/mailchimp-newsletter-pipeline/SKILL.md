---
name: mailchimp-newsletter-pipeline
description: Unified end to end pipeline for turning raw text or voice plus photos into a Mailchimp draft, embedded image, Dropbox archive, and test send.
tags: [mailchimp, newsletter, email-marketing, photos, dropbox]
version: 2.0.0
---

# Mailchimp Newsletter Pipeline

This is the single default pipeline for Dwayne's newsletter sends.

Use it when the user wants to go from rough source material to a Mailchimp-ready campaign with a real photo, a saved draft, and a test send.

It replaces the old split between "Mailchimp pipeline" and "Supabase photo workflow". Supabase is now optional, not the default path.

## When to Use

- Dwayne provides text, voice notes, ideas, or photos for a newsletter
- A newsletter needs to be drafted, humanized, packaged, and sent through Mailchimp
- A real image should appear inside the email
- The workflow should preserve a local and Dropbox archive in `photo.news`

## Default Principle

**Mailchimp hosts the image used in the actual campaign. Dropbox is for archive, staging, and review.**

That means the normal path is:

1. draft the article
2. humanize it
3. stage photo + draft in `photo.news`
4. sync `photo.news` to Dropbox
5. upload the final email image to Mailchimp File Manager
6. embed the returned `mcusercontent.com` image URL in the campaign HTML
7. send a test email
8. only send live after approval

## Known Environment Facts

- Mailchimp server prefix: `us13`
- Primary audience name: `School Claw`
- The live audience ID has been confirmed as `37494de84d`, but **always verify with `GET /lists` before campaign creation** because stale IDs fail with `Invalid list id`.
- `photo.news` local workspace: `/home/ubuntu/photo.news`
- Dropbox sync script for this workspace: `/home/ubuntu/.local/bin/photo-news-sync.sh`
- Current Dropbox app limitation: uploads work, but the app does not have `sharing.read` / `sharing.write`, so it cannot create permanent public shared links through the API.

## Inputs

Accepted inputs:
- raw text
- voice transcription
- one or more photos
- optional notes about audience, tone, subject line, or target email

## End to End Pipeline

### 1. Intake
Capture:
- topic
- audience
- goal
- tone
- key phrases to preserve
- target test email address

If the source is a voice note, transcribe first.
If the source is rough or robotic, plan to run a humanization pass before packaging.

### 2. Draft
Turn the raw material into:
- headline
- hook
- body copy
- closing
- subject line options
- preview text

Use `master-newsletter` for the editorial structure when helpful.

### 3. Humanize
Run a humanization pass before packaging.

Goals:
- preserve Dwayne's voice
- strip out AI phrasing
- keep the rhythm conversational
- avoid corporate language
- avoid unnecessary hyphenated compound adjectives

Use `humanizer` when the draft sounds too polished or synthetic.

Refer to the ## Humanization Gate section below for the formal checklist and rewrite triggers.

### 4. Stage Files in `photo.news`
Save working files locally before sending:
- markdown draft in `/home/ubuntu/photo.news/newsletters/drafts/`
- HTML draft in `/home/ubuntu/photo.news/newsletters/drafts/`
- source image in `/home/ubuntu/photo.news/photos/raw/`
- final image copy in `/home/ubuntu/photo.news/photos/edited/`
- metadata JSON if a campaign is created

Recommended naming:
- photos: `YYYYMMDD-topic-description.jpg`
- drafts: `YYYYMMDD-topic.md`
- HTML: `YYYYMMDD-topic.html`

### 5. Sync to Dropbox
Run:
```bash
/home/ubuntu/.local/bin/photo-news-sync.sh
```

Use Dropbox as:
- archive
- backup
- cross-device access
- short-lived review access if a temporary link is needed

Important limitation:
- because the current Dropbox app lacks `sharing.read` and `sharing.write`, do **not** rely on Dropbox for permanent public image URLs
- if needed, use `files_get_temporary_link` only as a short-lived review/prep URL

### 6. Upload the Image to Mailchimp File Manager
For the image that will appear inside the campaign, use Mailchimp File Manager.

API pattern:
```http
POST /file-manager/files
```

Payload fields:
- `name` — include the correct file extension
- `file_data` — base64 encoded file contents

Why this is the default:
- it returns a stable `mcusercontent.com` URL
- that URL works reliably inside Mailchimp campaign HTML
- it removes dependency on Supabase or Dropbox sharing scopes for the actual email image

### 7. Create Campaign Draft
Before campaign creation:
- verify the audience/list ID with `GET /lists`
- use the current `School Claw` list ID returned by the API

Then create the campaign draft with:
- subject line
- preview text
- from name
- reply-to email
- recipients list ID

If Mailchimp returns `Invalid list id`, refresh the audience ID from `GET /lists` and retry.

### 8. Set Campaign Content
Set both:
- HTML content
- plain-text fallback

HTML requirements:
- mobile friendly
- one clear hero image if a photo is provided
- descriptive alt text
- short paragraphs
- simple layout that renders well in Mailchimp

Plain-text requirements:
- include the full article
- keep structure readable
- do not omit important content just because the HTML version has styling

### 9. Send Test Email
Always send a test first.

API pattern:
```http
POST /campaigns/{campaign_id}/actions/test
```

Test payload:
- `test_emails`: array of target addresses
- `send_type`: usually `html`

Expected behavior:
- the test email sends
- the campaign often remains in `save` status afterward
- this is normal and does not mean the test failed

### 10. Optional Live Send
Only after user approval:
```http
POST /campaigns/{campaign_id}/actions/send
```

Never assume a draft or successful test means approval to send live.

## Fallback Rules

### If Supabase is unavailable
Do not block the send.
Use Mailchimp File Manager as the image host.

### If Dropbox shared links cannot be created
Do not block the send.
Use Dropbox only for archive/sync and Mailchimp for the live image.

### If the audience ID in notes or code is stale
Do not trust the cached value.
Call `GET /lists` and use the live result.

## Verification Checklist

Before finishing:
- [ ] copy sounds like Dwayne, not like AI
- [ ] image appears in the HTML draft
- [ ] image was uploaded to Mailchimp File Manager
- [ ] audience/list ID was verified live
- [ ] campaign content was set successfully
- [ ] test email was sent to the requested address
- [ ] live send was not triggered unless explicitly approved

## Delivery Follow-Up

After the test email is sent, track the campaign.

### Immediate (within test send)
- [ ] Test email received
- [ ] Image renders correctly
- [ ] Links work
- [ ] Mobile preview looks good
- [ ] Plain-text version is complete

### Post-send tracking (add to campaign JSON)
After live send (if approved), add to the campaign metadata JSON:
```json
{
  "live_sent_at": "ISO timestamp",
  "live_sent_to_count": N,
  "campaign_status": "sent",
  "archive_url": "https://..."
}
```

### Engagement check (manual or cron)
- 24h after send: check open rate and click rate via Mailchimp API
- Add engagement data to the campaign JSON
- If open rate < 15%, flag for subject line review
- If click rate < 2%, flag for CTA review

API endpoint: GET /campaigns/{campaign_id}
Fields to track: emails_sent, open_rate, click_rate, unsubscribed

Save updated JSON to: /home/ubuntu/photo.news/newsletters/drafts/YYYYMMDD-topic-mailchimp.json

## Practical Example

Recent proven run:
- humanized a graffiti reflection newsletter
- staged files in `photo.news`
- synced files to Dropbox with `photo-news-sync.sh`
- uploaded the truck image to Mailchimp File Manager
- created campaign `3948174018`
- embedded the Mailchimp-hosted image URL
- sent a test email to `dwayneprimeau@gmail.com`

## Pitfalls to Avoid

- using a stale audience ID from notes instead of checking `GET /lists`
- treating Dropbox as the live newsletter image host
- blocking on Supabase when Mailchimp image hosting already solves the problem
- skipping the plain-text fallback
- sending live before Dwayne approves

## Humanization Gate

Before packaging, run the draft through this checklist. If any answer is "no," revise before proceeding.

### Voice check
- [ ] Does the opening sound like a real person talking, not a press release?
- [ ] Are there at least 2 sentences that could only come from this specific author?
- [ ] Is the rhythm varied (short + medium sentences, not all the same length)?
- [ ] Would the author actually say these words out loud?

### AI smell check
- [ ] Zero instances of: leverage, delve, in today's world, it's important to note, game-changing, unlock, harness, navigate, landscape, tapestry
- [ ] No sentence starts with "In the realm of" or "When it comes to"
- [ ] No triple-adjective stacks ("incredible, transformative, and groundbreaking")
- [ ] Concluding thought is specific, not generic motivation

### Rewrite triggers
If the draft fails any check above, rewrite ONLY the failing sections. Do not rewrite the entire piece. Preserve what works, fix what doesn't.

Common fixes:
- Corporate opener → start with the specific observation or detail
- Generic conclusion → end with the most interesting thought, even if incomplete
- Flat rhythm → break one long paragraph into fragments
- AI phrases → replace with the simpler word the author would actually use

## Research Gate

Research is conditional. Before running the research stage, answer these questions:

### When to research
- The piece makes a factual claim that could be wrong (dates, statistics, names)
- The piece references something the audience might verify
- The piece would be stronger with one concrete data point or source
- The piece is about a topic where misinformation is common

### When to skip research
- The piece is a personal reflection or observation (like the graffiti newsletter)
- The piece is an opinion piece with no factual claims
- The piece is a quick update or announcement
- Adding research would dilute the personal voice

### How to research (when triggered)
- Find 1-3 supporting facts maximum
- Prefer recent, authoritative sources
- Integrate naturally — don't add a "Sources:" section unless the piece is academic
- If a fact contradicts the author's point, flag it for human review
- Never invent statistics or sources

If research is skipped, add a note to the intake brief: "No research needed — personal reflection piece" or similar.

## Output Contract

Every newsletter run MUST produce all of the following. No exceptions unless the user explicitly says "skip [item]."

### Required outputs
1. **3 subject line options** — one direct, one curiosity, one emotional
2. **Preview text** — 40-90 characters, complements (not repeats) the subject line
3. **Article draft** — markdown, following voice profile
4. **HTML email** — 600px, inline styles, inline images, mobile-friendly
5. **Plain-text version** — full article, no HTML, readable in any email client
6. **Image strategy** — for each image: role (hero/supporting/proof/behind-the-scenes), placement reasoning, alt text
7. **CTA check** — if no CTA is present, explicitly note why ("Personal reflection — no CTA needed") or add one
8. **3 quality gate results** — voice check, audience check, platform check (pass/fail per item)

### Subject line rules
- Direct: states what the newsletter is about plainly
- Curiosity: creates interest without being clickbait
- Emotional: connects to the reader's feeling or aspiration
- All three must be true to the content — no bait-and-switch

### CTA decision matrix
| Newsletter type | CTA approach |
|---|---|
| Personal reflection | Optional — "Reply with your thoughts" or omit |
| Product update | Required — specific action (try it, read docs) |
| School announcement | Required — date/deadline/link |
| Event invite | Required — RSVP/registration link |
| Thought leadership | Soft — "Share if this resonated" |

## Notes

Supabase can still be used later if Dwayne specifically wants a Supabase-hosted media layer, but it is no longer part of the default pipeline.

## Voice Profile

Dwayne's newsletters are written in a specific voice. All drafts must match these characteristics before proceeding downstream.

### Core characteristics
- Practical, direct, conversational
- First person, present tense when describing observations
- Short paragraphs (1-3 sentences)
- Questions used as rhetorical devices, not engagement bait
- Honest uncertainty — "My gut says," "I don't think," "Maybe"
- No corporate filler, no hype, no exaggerated adjectives
- Clean grammar without flattening personality
- Concrete over abstract — show through specific details, not generalizations
- Lets distinctive phrases survive — "running argument between the city and the people living in it"

### Words to avoid
- leverage, delve, in today's world, game-changing, navigate (metaphorical), unlock, harness, synergy, landscape, tapestry, transformative, groundbreaking

### Sentence patterns
- Opens with observation, not thesis statement
- Builds paragraphs: observation → reflection → conclusion
- Varied rhythm — mix short declarative sentences with longer ones
- Comfortable with fragments for emphasis: "Right out in the open. Sitting in the middle of daily life."
- Lists use parallel structure: "Sometimes it's art. Sometimes it's damage. Sometimes it's protest."

### Anti-patterns
- If it reads like LinkedIn, rewrite it
- If it sounds like every other newsletter, inject specificity
- If every sentence is the same length, vary the rhythm
- If the conclusion is generic inspiration, cut it or replace with a real thought

### Sample voice (from published newsletter)
> Walking through parts of Europe, graffiti doesn't feel occasional. It feels constant.
>
> My gut says a lot of it comes down to rebellion. In France especially, there still seems to be this strong urge to push back against power.
>
> A way of saying: I'm here, and I don't care what the system thinks.
>
> If you spend enough time walking around, the walls start to feel like a running argument between the city and the people living in it.
