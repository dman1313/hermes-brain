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

## Output Contract

A successful run should produce:
- humanized article draft
- HTML draft file
- local saved assets in `photo.news`
- Dropbox sync confirmation
- Mailchimp-hosted image URL
- campaign ID
- archive URL
- confirmation that the test email was sent

## Verification Checklist

Before finishing:
- [ ] copy sounds like Dwayne, not like AI
- [ ] image appears in the HTML draft
- [ ] image was uploaded to Mailchimp File Manager
- [ ] audience/list ID was verified live
- [ ] campaign content was set successfully
- [ ] test email was sent to the requested address
- [ ] live send was not triggered unless explicitly approved

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

## Notes

Supabase can still be used later if Dwayne specifically wants a Supabase-hosted media layer, but it is no longer part of the default pipeline.
