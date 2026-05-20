---
name: homer-dashboard
description: Quick setup, restart, and health-check of the OpenClaw Bot Dashboard (Flask + gunicorn).
prerequisites:
  - Python 3.8+
  - pip
  - gunicorn
  - psutil
  - flask
steps:
  - label: Quick setup
    commands:
      - cd /opt/openclaw-dashboard
      - python -m venv venv && source venv/bin/activate
      - pip install flask psutil gunicorn
  - label: Run dev server
    command: python dashboard.py
    note: serves on port 8888
  - label: Run production
    command: gunicorn --bind 0.0.0.0:8888 --workers 2 dashboard:app
  - label: Health-check port
    command: curl -s -o /dev/null -w "%{http_code}" http://localhost:8888
    expected: "200"
  - label: Check process
    command: pgrep -f "gunicorn.*dashboard:app"
  - label: Inspect logs
    commands:
      - cat ~/.hermes/logs/hermes.log
      - cat ~/.hermes/hermes.log
notes:
  - Dashboard shows: bot ONLINE/OFFLINE, uptime, CPU/Mem/Disk %, recent logs.
  - Auto-refresh every 10s.
  - Use systemd or supervisor for persistent service management.
---