# Research-to-Blog Pipeline

When a blog post needs deep research (statistical claims, industry data, expert quotes), use a two-stage pipeline instead of writing from scratch.

## Pipeline

### Stage 1: Research (Sherlock)
Delegate to Sherlock or a research subagent:
- Topic, target audience, keyword targets
- Output: structured markdown article with sources, stats, and quotes
- Save to `/home/ubuntu/<topic>_blog_article.md`

### Stage 2: HTML Build
Read the research markdown and convert to the blog HTML template:
- Match the site's design system (see `blog-design-system.md`)
- Preserve all statistical claims and source attributions
- Add internal links to services/product/contact
- Add BlogPosting JSON-LD schema
- Use `delegate_task` if the article is long (2000+ words) to parallelize conversion

## Example (May 2026)
- Sherlock researched "AI in Education" → produced 291-line markdown at `/home/ubuntu/ai_in_education_blog_article.md`
- Clark drafted the article structure
- Coding Officer converted to HTML matching the humangood.ai design system
- Result: `blog/ai-in-education-guide-school-leaders.html` (pillar post)

## When to Use This Pipeline
- Post targets a specific industry/vertical (schools, nonprofits)
- Post needs credible statistics and citations
- Post is a "pillar" or long-form guide (1500+ words)
- User says "research and write" or "use Sherlock to research"

## When NOT to Use
- Simple listicle or how-to posts (write directly)
- Post is under 800 words
- Topic is well-known to the agent (no research needed)
