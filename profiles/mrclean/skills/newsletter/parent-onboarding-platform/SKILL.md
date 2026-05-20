---
name: parent-onboarding-platform
description: >
  Parent Onboarding Platform — a two-sided Flask app for private/IB schools. 
  School admin dashboard + parent onboarding flow with 5-phase checklists, 
  document management, child profiles, event scheduling, and AI FAQ.
domain: education
tags: [flask, school, onboarding, parent, enrollment, ib]
---

# Parent Onboarding Platform

## Location
`~/human-good-ai/parent-onboarding/`
Running on port **8583**.

## Architecture
- **Flask** backend with SQLite (`data/onboarding.db`)
- **Tailwind CSS** dark theme (CDN-loaded)
- Templates: `templates/`
- Two auth systems: school admin + parent/family

## Database Tables
- `schools` — school profiles (name, IB status, country, language)
- `onboarding_templates` — phase definitions per school
- `families` — parent accounts linked to schools
- `children` — child profiles under each family
- `tasks` — auto-generated checklist items per family (5 phases)
- `documents` — uploaded docs per family (passport, medical, etc.)
- `events` — orientation, tours, meetings
- `messages` — communication log
- `faq` — school-customizable Q&A (EN/JP bilingual)
- `school_programs` — after-school activities, lunch programs

## Five Onboarding Phases
1. **Pre-Enrollment** 📋 — profile, child info, tuition review, tour, meet teachers
2. **Enrollment** 📝 — passport, records, immunization, contract, payment, medical
3. **Pre-Arrival** 🧳 — uniform, transport, lunch, after-school, handbook, emergency contacts
4. **First Week** 🎒 — orientation, meet teacher, verify contacts, feedback
5. **Ongoing** 🌟 — 30-day check-in, 90-day survey, annual renewal

## Key Routes

### Public
- `/` — Landing page with pricing (¥30k/¥50k/¥80k monthly)
- `/invite/<school_id>` — Direct registration link for families

### School Admin
- `/school/register` — Sign up
- `/school/login` — Login
- `/school/dashboard` — Overview with stats + families by phase
- `/school/families` — All families list with progress bars
- `/school/families/<id>` — Individual family detail (children, tasks, docs, events)
- `/school/faq` — FAQ manager (add/delete Q&A)
- `/school/settings` — School profile (IB status, languages, contact)

### Parent/Family
- `/family/register` — Sign up (requires school code)
- `/family/login` — Login
- `/family/dashboard` — Phase cards with task list + progress bars
- `/family/tasks` — Full task list across all phases
- `/family/children` — Add/edit child profiles (name, grade, allergies, medical, special needs)
- `/family/documents` — Upload documents by category
- `/family/events` — View upcoming events
- `/family/faq` — Searchable school FAQ (expand/collapse Q&A)

## Auto-Task Generation
When a family registers, all 5 phases of tasks are auto-created. Required tasks are marked. Completing all required tasks in a phase auto-advances to the next phase. Completion of last phase marks onboarding as complete.

## Invite Flow
1. School registers → gets a unique ID
2. School shares: `https://[domain]/invite/[school_id]`
3. Parent clicks → registration form pre-filled with school
4. Parent creates account → tasks auto-generated → dashboard appears

## How to Start
```bash
cd ~/human-good-ai/parent-onboarding
python app.py
# Runs on 0.0.0.0:8583
```

## Deployment
Caddy route for `/onboard*` → `localhost:8583`
Add to Caddyfile:
```
handle_path /onboard* {
    reverse_proxy localhost:8583
}
```
