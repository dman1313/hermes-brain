---
name: mailchimp-supabase-newsletter
description: Legacy specialization for Supabase-hosted newsletter images. Default to mailchimp-newsletter-pipeline unless the user explicitly wants Supabase storage.
category: productivity
tags: [mailchimp, supabase, newsletter, email]
version: 2.0.0
---

# Mailchimp + Supabase Newsletter Workflow

This skill is now a **special case**, not the main pipeline.

## Default Rule

If the user simply wants a newsletter with photos, use **`mailchimp-newsletter-pipeline`**.
That unified pipeline already covers:
- drafting
- humanizing
- saving to `photo.news`
- Dropbox sync
- Mailchimp image upload
- campaign creation
- test send

## Use This Skill Only When

- Dwayne explicitly asks for **Supabase Storage**
- a stable public media layer outside Mailchimp is required
- there is a working Supabase service role key available for bucket creation and uploads

## Current Environment Notes

- Supabase anon/public key is read-only and cannot perform storage writes
- Supabase service role key is still required for bucket creation and file uploads
- Mailchimp image uploads already work through `POST /file-manager/files`
- Current confirmed Mailchimp audience for `School Claw` is `37494de84d`, but it should still be verified live with `GET /lists`

## Recommended Decision Rule

- **No service role key available** -> use `mailchimp-newsletter-pipeline`
- **Service role key available and user wants Supabase-hosted assets** -> use this skill

## Fallback

If the Supabase path fails or is blocked, immediately fall back to:
1. save assets in `photo.news`
2. sync to Dropbox
3. upload the email image to Mailchimp File Manager
4. continue with the Mailchimp test-send flow

## Important Reminder

Do not block newsletter delivery just because Supabase is unavailable. Supabase is optional in this environment, not required.
