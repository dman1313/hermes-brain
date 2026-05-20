---
name: seo-content-blog
description: |
  SEO audit, keyword research, content strategy, and blog post creation
  for static websites deployed via GitHub/Zeabur. Covers the full workflow:
  audit current SEO state, identify content gaps, write blog posts targeting
  real search keywords, build pages matching the site's existing design system,
  update sitemap/robots.txt/nav, and deploy via git push.
  Trigger when user says "scan my website for SEO", "build blog pages",
  "create content that ranks", "/goal for blog", or "what content does my
  site need to rank?"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    category: marketing
    tags: [seo, blog, content-strategy, zeabur, static-site, keyword-research]
---

# SEO Content & Blog — Audit, Build, Deploy

## 1. Overview

**What this skill does:**  
A complete workflow for adding SEO-optimized content to a static website. It starts with an audit of the site's current SEO posture, identifies content gaps, targets keywords the audience actually searches, creates blog posts matching the site's existing design system, updates SEO infrastructure (sitemap, robots.txt, nav), and deploys via git push to GitHub (which triggers Zeabur auto-deploy).

**When to use it:**  
- User says "scan my website for SEO" or "audit my site"
- User says "build blog pages so it can rank" or "create content"
- User says "I need service pages for my site"
- User provides a `/goal` asking for SEO/content strategy

**Limits / Boundaries:**  
- This skill assumes the site is a **static HTML site deployed via GitHub → Zeabur** (or similar git-based deploy). For CMS-based sites (WordPress, Ghost, etc.), use a different approach.
- This skill does NOT handle image generation, design system creation from scratch, or full marketing funnels — see `marketing-pipeline` for those.
- Does NOT configure Cloudflare HSTS or DNS settings — that's a dashboard action.

---

## 2. Phase 1: SEO Audit

### 2.1 What to check

| Check | How | Severity |
|-------|-----|----------|
| Page count | curl + sitemap.xml | Critical |
| Meta descriptions | grep for `<meta name="description"` on each page | High |
| Title tags | grep for `<title>` on each page | High |
| Canonical tags | grep for `rel="canonical"` | High |
| OG / Twitter cards | grep for `og:title`, `twitter:card` | Medium |
| Schema.org JSON-LD | grep for `application/ld+json` | Medium |
| Sitemap.xml | Curl it, check it covers all pages | Critical |
| Robots.txt | Curl it, check it allows all + points to sitemap | Medium |
| Favicon | Check for 404 on /favicon.ico | Low |
| HSTS header | `curl -sI` and check `strict-transport-security` | Low |
| Image alt text | grep for `<img` and check `alt` attributes | Medium |
| Content depth | Strip tags and count words per page | Medium |
| Internal linking | grep for `<a href` — are there non-nav links between pages? | Medium |
| llms.txt / ai.txt | Check if present for agent-readiness | Low (bonus) |
| Blog | Check if `/blog/` or `/blog` exists | Critical |

### 2.2 Audit output format

Present as a bullet list with ✅/❌ markers. Group by Critical / High / Medium / Low severity. Include the actual values found (e.g., "Only 2 pages in sitemap", "894 words on homepage").

End with a brief summary paragraph identifying the top 3 gaps to fix.

---

## 3. Phase 2: Keyword & Content Gap Analysis

### 3.1 Identify keyword targets

From the site's content and services, derive target keywords. Use these categories:

| Category | Example Keywords |
|----------|-----------------|
| **Core audience** | "AI for nonprofits", "AI for schools", "AI for mission-driven organizations" |
| **Problem/pain point** | "reduce administrative burden AI", "automate nonprofit admin work" |
| **Product terms** | "agent ready website", "AI agent certification" |
| **Value terms** | "ethical AI implementation", "responsible AI framework" |
| **Format terms** | "AI readiness checklist", "AI for nonprofits guide" |

### 3.2 Map content to keywords

For each keyword target, define:
- **Post type** — Guide, Checklist, Case Study, Explainer, How-to
- **Target audience** — Nonprofits, Schools, Founders, etc.
- **Internal link targets** — Which service pages or product pages this post links to
- **Post's main H2 structure** — 4-6 headings

---

## 4. Phase 3: Build Blog Posts

**Templates available:** `references/blog-page-template.html` and `references/blog-index-template.html` — copy these and replace `{PLACEHOLDERS}` for each new post. Both match the premium green/cream design system used on humangood.ai.

### 4.1 Design matching

Before writing, **inspect the site's existing CSS**:
```bash
curl -sL https://sitename.com/styles.css | head -80
# Extract CSS custom properties (:root vars), font stacks, border radii, colors
```

Build inline CSS that uses the site's actual design tokens. For blog posts specifically:

- **Match the header/nav exactly** — copy the `<header>` block from the existing site's HTML
- **Use the site's existing CSS file** via `<link rel="stylesheet" href="...">`
- **Add page-specific styles** in a `<style>` block scoped to blog/article classes
- **Match spacing, font sizes, and link colors** to the main site's feel

### 4.2 Blog page SEO template

Every blog post MUST include in its `<head>`:
```html
<meta name="description" content="...">
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:image" content="https://sitename.com/assets/hero-wide.png">
<meta property="og:url" content="https://sitename.com/blog/post-slug.html">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://sitename.com/blog/post-slug.html">
<title>{Title} — Site Name Blog</title>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "...",
  "description": "...",
  "url": "...",
  "datePublished": "...",
  "author": {"@type": "Person", "name": "Owner Name"},
  "publisher": {"@type": "Organization", "name": "Site Name", "url": "https://sitename.com"}
}
</script>
```

### 4.3 Blog index page

Create `/blog/index.html` with:
- Same header as main site
- Blog title + tagline
- Card grid showing all posts (date, title, description, read-more link)
- Scroll reveal animation using IntersectionObserver
- Same CSS as main site + blog-specific styles

### 4.4 Internal linking rules

Every blog post MUST link to at least 2 internal pages:
1. A **service page** or **product page** related to the post topic
2. The **contact page** or **CTA** at the bottom

Bonus: link to other blog posts where relevant ("Read more about [related topic]").

---

## 5. Phase 4: SEO Infrastructure Updates

Always update these files:

### sitemap.xml
Add entries for all new pages. Include lastmod dates. Format:
```xml
<url>
  <loc>https://sitename.com/blog/post-slug.html</loc>
  <lastmod>YYYY-MM-DD</lastmod>
  <priority>0.8</priority>
</url>
```

### robots.txt
Ensure it points to the updated sitemap:
```
Sitemap: https://sitename.com/sitemap.xml
```

### Main nav
Add a "Blog" link to the main site header nav on all pages (homepage, service pages, etc.)

---

## 6. Phase 5: Deploy

### Git workflow (GitHub + Zeabur auto-deploy)
```bash
cd /path/to/repo
git add -A
git commit -m "feat: add blog — 3 SEO posts + sitemap + nav update"
git push origin main
```

**Zeabur auto-deploys** on push to main. No manual deploy step needed.

### Verification
After deploy (wait 1-2 min), verify:
```bash
curl -sI https://sitename.com/blog/ | grep "200"
curl -s https://sitename.com/sitemap.xml | grep "blog"
```

---

## 7. Pitfalls

| Pitfall | Mitigation |
|---------|------------|
| **Blog pages don't match site design** | Copy the EXACT header block from the existing HTML. Use the site's existing styles.css. Only add page-specific override styles. |
| **Zeabur auto-deploy not triggering after push** | GitHub → Zeabur auto-deploy can silently fail even when the remote shows the latest commit. Check the live site after push — if the sitemap or new pages still show old content after 2+ minutes, log into the Zeabur dashboard and manually trigger a redeploy. An empty commit (`git commit --allow-empty -m "chore: trigger Zeabur redeploy" && git push`) can sometimes wake it up but is not guaranteed. |
| **Sitemap not showing new pages** | The live sitemap is your canary — if it doesn't show blog URLs, Zeabur hasn't deployed. Check with `curl -s https://sitename.com/sitemap.xml | grep blog`. |
| **Zeabur not actually the deploy target** | Check `x-zeabur-request-id` header on the live site. If absent, check for Cloudflare tunnel, Cloudflare Pages, or other hosting. Run `curl -sI https://sitename.com/ \| grep -i 'x-zeabur\\|server\\|cf-ray'`. |
| **Zeabur auto-deploy doesn't trigger** | GitHub push may succeed but Zeabur doesn't always pick it up. Verify deployment by checking `curl -sI https://sitename.com/sitemap.xml` — if it still shows old content, Zeabur didn't deploy. Wait 2-3 minutes first (sometimes just slow). If still stale: push an empty commit (`git commit --allow-empty -m "chore: trigger redeploy" && git push`). If that fails too, the user needs to trigger manual redeploy from Zeabur dashboard. The blog files ARE on main — this is a deployment pipeline issue, not a code issue. |
| **Multiple site versions exist** | Check with `ps aux \| grep 'flask\\|node\\|gunicorn'` and `ss -tlnp` to see what's serving on what port. Compare what the live domain serves vs localhost. |
| **Nav doesn't include blog link** | Update landing page nav bars. Do NOT touch product pages (e.g., Agent Ready, subdomain apps) — the user may consider those off-limits. If unsure which pages are \"product\" vs \"landing,\" ask. |
| **Blog posts written with generic placeholder content** | Each post must be useful, specific, and actionable. No \"AI can revolutionize\" fluff — use concrete workflows, time savings, and \"how to start\" sections. |
| **Sitemap not updated with blog URLs** | After creating blog pages, update `sitemap.xml` with all new URLs. Verify with `curl -s https://sitename.com/sitemap.xml | grep blog`. |
| **Raw GitHub check shows 404 for new files** | raw.githubusercontent.com has its own cache; may lag behind `git ls-tree -r origin/main`. Verify with `git ls-tree` first — if files show there, the push succeeded and the issue is downstream (GitHub cache or Zeabur deploy). |

---

## 8. File Structure Convention

```
repo-root/
  index.html              # Main site (update nav)
  styles.css              # Site design system (reference, don't modify)
  sitemap.xml             # Update with new pages
  robots.txt              # Update sitemap reference
  blog/
    index.html            # Blog index (create)
    post-slug-1.html      # Blog post (create)
    post-slug-2.html      # Blog post (create)
```

---

## 9. Quality Checks Before Push

- [ ] All new pages have meta description, title, canonical, OG tags
- [ ] All blog posts have BlogPosting JSON-LD schema
- [ ] Sitemap includes all new pages
- [ ] Nav on ALL existing pages includes Blog link
- [ ] Blog index page lists all posts with descriptions
- [ ] Each post has ≥ 2 internal links to services/product/contact
- [ ] Design matches main site (same header, CSS vars, fonts)
- [ ] No absolute paths that break when deployed (/assets/ not ./assets/ for files at root level)
- [ ] `git remote -v` confirms correct repo before push
