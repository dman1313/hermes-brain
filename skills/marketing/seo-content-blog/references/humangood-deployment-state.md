# humangood.ai Deployment State (as of 2026-05-24)

## Live Site State
- **Sitemap:** 3 URLs only (/, /agent-ready.html, /agent-ready.md) — lastmod dates from May 3
- **Blog:** Returns 404 — no blog content is live
- **Deploy target:** Zeabur (confirmed by `x-zeabur-request-id` header)
- **CDN:** Cloudflare (confirmed by `cf-ray` header)

## Local Repo State (dman1313/goodhuman, main branch)
- **Sitemap:** 9 URLs (including blog index + 5 blog posts)
- **Blog:** 5 posts + index, all committed and pushed
- **Latest commit:** ede9887 (May 24) — empty commit to trigger redeploy

## The Gap
Commits from May 14–24 are all on `main` but Zeabur hasn't deployed any of them.
The auto-deploy webhook appears disconnected or broken.

## Blog Posts (local only, not live)
1. `ai-in-education-guide-school-leaders.html` — May 19
2. `nonprofits-ai-reduce-admin-work.html` — May 14
3. `schools-ai-admin-automation-guide.html` — May 14
4. `agent-ready-standard-guide.html` — May 14
5. `ai-workflows-save-small-teams-10-hours.html` — May 24

## Action Needed
User needs to check Zeabur dashboard:
1. Verify the project is connected to `dman1313/goodhuman` on `main`
2. Manually trigger a redeploy
3. If webhook is broken, reconnect it
