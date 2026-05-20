# Zeabur Deployment Notes

## GitHub → Zeabur auto-deploy for Python/Flask apps

### Project requirements
- `requirements.txt` with Flask, gunicorn, and all deps
- `Procfile`: `web: gunicorn app:app -w 2 -b 0.0.0.0:$PORT`
- App must read `PORT` from env: `port = int(os.environ.get('PORT', 5000))`

### Critical pitfall: Service type switching

**Zeabur does NOT auto-redetect the service type** when you change languages.
If a repo was originally detected as Node.js (had `package.json`), simply removing
`package.json` and adding `requirements.txt` will NOT make Zeabur switch to Python.

**Manual fix (30 seconds):**
1. Go to [Zeabur Dashboard](https://dash.zeabur.com)
2. Open the project
3. Settings → Service Type → change to **Python** (or back to **Static Site**/Node.js when reverting)
4. Trigger **Redeploy**

Without this, Zeabur will keep serving the old build indefinitely.
**Works both directions** — if reverting a Flask app back to static HTML, change service type back to Static Site.

### Deployment verification

```bash
# Check /llms.txt — old static site returns 404, Flask app returns 200
curl -sI https://humangood.ai/llms.txt

# Look for x-zeabur-* headers to confirm Zeabur is serving
curl -sI https://humangood.ai | grep x-zeabur
```

### Example: HumanGood.AI deployment

- **GitHub repo:** `dman1313/goodhuman` (branch: `main`)
- **Domain:** `humangood.ai`
- **Zeabur project:** HumanGood.AI landing page
- **Original type:** Static / Node.js
- **New type:** Python (Flask + gunicorn)
- **Deploy:** Push to `main` → Zeabur auto-deploys (after service type switch)

## Force-Push Restore (Reverting to a Previous State)

When a deployment goes wrong and you need to restore a repo to an earlier commit:
```bash
cd /path/to/repo
git log --oneline -20                          # Find the target commit
git reset --hard <commit-hash>                 # Reset to that commit
git push --force origin main                   # Push (req. force-push permission)
```
**After force-pushing, Zeabur may serve the old cached deployment** until the service type is corrected and a redeploy triggers. Check with `curl -sI https://domain.com/` — if the HTML doesn't match the reset commit, the old deployment is still cached.

## Quick VPS Preview (Before Domain Deployment)

When you need a live preview without routing through the production domain:
```bash
# Serve static files
cd /path/to/static-site
python3 -m http.server 8765 &     # background the server

# Open firewall
sudo ufw allow 8765/tcp

# Get VPS IP
curl -s ifconfig.me

# Access: http://<vps-ip>:8765
```
Clean up with `sudo ufw delete allow 8765/tcp` when done.
