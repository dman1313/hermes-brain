---
name: sapper
description: Elite technical obstacle removal and path-clearing skill for overcoming complex system barriers, debugging failures, and creating pathways through difficult technical terrain.
tags: [debugging, obstacle-removal, system-integration, technical-debt, path-clearing]
version: 1.0.0
---

# Sapper Skill

**Mission:** Clear paths through technical obstacles, remove system barriers, and create pathways for progress where conventional approaches fail.

## When to Use This Skill

Use the sapper skill when facing:
- Complex system failures with unclear root causes
- Integration roadblocks between incompatible systems
- Technical debt that's blocking new development
- Performance bottlenecks requiring deep investigation
- Legacy code that needs to be navigated or removed
- Multi-system dependencies causing cascading failures
- Any situation where "something is blocking progress" and needs to be cleared

## Core Principles

1. **Assess the Terrain First** - Never charge in blind. Understand the full scope of the obstacle.
2. **Identify the Critical Path** - What's the minimum viable path through the obstacle?
3. **Use the Right Demolition Tools** - Different obstacles require different approaches.
4. **Build Bridges, Not Just Breaches** - Create sustainable solutions, not temporary fixes.
5. **Clear the Debris** - Remove the obstacle completely so it doesn't block others.

## The Sapper Workflow

### Phase 1: Reconnaissance & Assessment

**Step 1: Map the Battlefield**
```bash
# Get system overview
terminal(command="ps aux | head -20")
terminal(command="df -h")
terminal(command="netstat -tulpn | head -20")

# Check logs for recent failures
terminal(command="sudo journalctl -xe --no-pager | tail -100")
search_files(pattern="ERROR|FAIL|Exception|panic", target="content", path="/var/log", file_glob="*.log", limit=20)
```

**Step 2: Identify the Obstacle**
- What specific error or failure is occurring?
- When did it start? (Check timestamps)
- What systems/components are involved?
- Is this a new issue or recurring problem?

**Step 3: Trace Dependencies**
```bash
# Check service dependencies
terminal(command="systemctl list-dependencies --reverse <service> 2>/dev/null || echo 'Not a systemd service'")

# Check network connections
terminal(command="ss -tulpn | grep <port_or_service>")

# Check file dependencies
terminal(command="lsof <path_to_file> 2>/dev/null || echo 'File not in use'")
```

### Phase 2: Demolition & Clearance

**For Code/Technical Debt Obstacles:**
```bash
# Analyze code complexity
terminal(command="find . -name '*.py' -exec wc -l {} + | sort -rn | head -10")

# Find dead code
search_files(pattern="TODO|FIXME|HACK|XXX", target="content", path=".", output_mode="content")

# Check for circular imports (Python example)
terminal(command="python -m py_compile <file> 2>&1 | grep -i 'circular' || echo 'No circular imports found'")
```

**For Performance Bottlenecks:**
```bash
# Quick performance checks
terminal(command="top -bn1 | head -20")
terminal(command="iostat -x 1 3")
terminal(command="free -h")

# Database performance (if applicable)
terminal(command="pg_stat_activity for PostgreSQL or SHOW PROCESSLIST for MySQL")
```

**For Integration Roadblocks:**
```bash
# Test connectivity
terminal(command="curl -v <endpoint> 2>&1 | head -50")
terminal(command="telnet <host> <port> 2>&1 | head -10")

# Check API compatibility
terminal(command="curl -H 'Accept: application/json' <api_endpoint> | jq . 2>/dev/null || curl -H 'Accept: application/json' <api_endpoint>")
```

### Phase 3: Bridge Building & Pathway Creation

**Step 1: Create Minimal Working Path**
- What's the simplest fix that unblocks progress?
- Can we create a temporary bridge while building a permanent solution?
- Document the workaround clearly.

**Step 2: Implement Sustainable Solution**
- Fix root causes, not just symptoms
- Add monitoring to detect recurrence
- Create documentation for future maintainers

**Step 3: Clear the Debris**
```bash
# Clean up temporary files
terminal(command="find /tmp -name '*temp*' -mtime +1 -delete 2>/dev/null || true")

# Clear caches if appropriate
terminal(command="sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || echo 'Cannot clear cache'")

# Restart services if they were modified
terminal(command="sudo systemctl daemon-reload 2>/dev/null || true")
```

## Specialized Demolition Tools

### The Debugging Charge (For Complex Bugs)
```bash
# Increase logging verbosity
patch(path="config_file", old_string="log_level = INFO", new_string="log_level = DEBUG")

# Add debug statements at critical points
execute_code(code="""
from hermes_tools import read_file, patch
content = read_file('problematic_file.py')['content']
# Insert debug logging at function entry points
import re
new_content = re.sub(r'def (\\w+)\\(', r'def \\1(\\n    print(f"[DEBUG] Entering \\1")\\n    ', content)
write_file('problematic_file.py', new_content)
""")
```

### The Integration Breach (For API/Protocol Issues)
```bash
# Create a test harness to isolate the problem
write_file(path="test_integration.py", content="""
import requests
import json
import sys

def test_endpoint(url, method='GET', data=None):
    try:
        if method == 'GET':
            resp = requests.get(url, timeout=10)
        else:
            resp = requests.post(url, json=data, timeout=10)
        
        print(f"Status: {resp.status_code}")
        print(f"Headers: {dict(resp.headers)}")
        try:
            print(f"Body: {resp.json()}")
        except:
            print(f"Body (text): {resp.text[:500]}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_endpoint(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000')
""")

terminal(command="python test_integration.py <problem_endpoint>")
```

### The Performance Minefield (For Slow Systems)
```bash
# Profile Python code
write_file(path="profile_script.py", content="""
import cProfile
import pstats
import io
from your_module import problematic_function

pr = cProfile.Profile()
pr.enable()
problematic_function()
pr.disable()

s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(20)
print(s.getvalue())
""")
```

## Verification & Quality Control

**After clearing an obstacle, always verify:**
1. **Functionality restored?** - Test the core use case
2. **No new issues introduced?** - Run existing tests
3. **Monitoring in place?** - Add alerts for recurrence
4. **Documentation updated?** - Future maintainers need to know

```bash
# Quick verification checklist
terminal(command="echo '=== Verification Checklist ==='")
terminal(command="curl -f <health_endpoint> && echo 'Health check: PASS' || echo 'Health check: FAIL'")
terminal(command="systemctl is-active <critical_service> && echo 'Service active: PASS' || echo 'Service active: FAIL'")
terminal(command="grep -q 'FIXED' <changelog> && echo 'Documentation: PASS' || echo 'Documentation: FAIL'")
```

## Pitfalls to Avoid

⚠️ **Don't demolish without assessment** - You might bring down a critical system
⚠️ **Don't create temporary bridges as permanent solutions** - Technical debt compounds
⚠️ **Don't work alone on critical systems** - Use `delegate_task` for complex obstacles
⚠️ **Don't forget to communicate** - Let stakeholders know about the obstacle and ETA
⚠️ **Don't ignore the debris** - Clean up after yourself

## Sapper Mindset

Remember: You're not just fixing bugs, you're **clearing paths**. Your work enables others to move forward. Be methodical, be thorough, and leave the terrain better than you found it.

**Sapper Creed (Adapted):**
"I am a Sapper, the cutting edge of technical progress. I will always endeavor to clear the path, regardless of the obstacles. My flexibility and special training shall provide my team with the tools to overcome insurmountable technical challenges."

## Related Skills

- `systematic-debugging` - For structured debugging approaches
- `subagent-driven-development` - For complex implementation challenges  
- `writing-plans` - For mapping multi-step solutions
- `test-driven-development` - For ensuring quality after clearance

---
*Skill created: April 16, 2026*  
*Inspired by 250 years of military engineering excellence*