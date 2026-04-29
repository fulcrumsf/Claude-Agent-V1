---
title: "CLAUDE.md — Upkeeply"
type: config
domain: app-dev
tags: [config, app-dev, ai-agents, upkeeply]
---

# CLAUDE.md — Upkeeply

## Vault Access

Before starting work: Read `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/000_VAULT-INDEX.md`

This department's knowledge is organized in the vault under:
- Skills: `/Obsidian-Vault/000_Skills/` (shared development workflows)
- Tools: `/Obsidian-Vault/003_Tools/` (API documentation, model selection)

**Vault-first rule:** Search the vault for context before asking the user. If you need clarification, ask a focused question instead of requesting extensive background.

---

## What This Is
A home maintenance tracking app with an AI chatbot at its core. Homeowners chat with it, send photos of equipment labels (HVAC units, filters, water heaters, etc.), and the AI extracts model numbers, specs, and maintenance intervals automatically. It then tracks everything, sets reminders, and suggests the exact replacement parts — with Amazon/Walmart affiliate links built in.

**Current status:** Concept + PRD complete. Frontend scaffolded. Not yet in active development.

---

## The Core Value Proposition
> "I just replaced my air filter — remind me when to do it again."

User sends a photo of their AC unit sticker → app reads the model number → identifies the correct 16x20 filter → logs the task → schedules the next reminder → suggests the exact filter on Amazon with an affiliate link.

No manual data entry. No Googling model numbers. The AI does it.

---

## Key Features (MVP)

### Conversational Capture (Core Differentiator)
- Chat-first interface — default home screen is the chatbot
- Users can type, dictate, or send photos
- AI extracts: manufacturer, model, filter size, maintenance intervals
- Auto-creates an Asset and links a Task to it

### Assets
Things in your home that need maintenance:
- HVAC units, air handlers
- Pool / spa / hot tub
- Smoke detectors, CO detectors
- Water filters (whole-house, fridge, hot tub)
- Light bulbs (by room/fixture)
- Anything else the user logs

Each asset stores: name, category, location, manufacturer, model, serial, photos, key specs

### Tasks & Reminders
- Recurring reminders (fixed interval, seasonal, or manual)
- Push notifications, calendar sync (Google + Apple), email, SMS
- Completion history with optional notes and photos
- Grouped notifications for households with many devices

### Affiliate Monetization
- When AI identifies a specific product with 100% confidence (exact model/filter/bulb), it surfaces Amazon or Walmart product links
- Affiliate revenue from purchases
- Only suggest products when confident — do not guess

### Household Features
- Multi-user: invite household members by email
- Timeline view per asset and globally
- Export: ICS (calendar), CSV/JSON backup

---

## Tech Stack
- **Frontend:** React 19 + TypeScript + Vite
- **Styling:** Tailwind CSS + tailwind-merge + clsx
- **Routing:** React Router DOM v7
- **Animation:** Framer Motion
- **AI:** Google Generative AI (`@google/generative-ai`) — Gemini
- **Backend/Auth/DB:** Firebase
- **Icons:** Lucide React
- **Build:** Vite (not Next.js — this is a Vite SPA)
- **Target:** iOS first, then Android, then web dashboard

---

## Project Structure
```
Upkeeply/
├── CLAUDE.md               ← This file
├── Upkeeply_App_PRD.md     ← Full product requirements document
├── src/                    ← React app source
├── public/                 ← Static assets
├── scripts/                ← Utility scripts
├── dist/                   ← Build output
├── .env                    ← API keys (never commit)
├── index.html
├── vite.config.js
└── package.json
```

---

## Agent Priorities
1. **AI accuracy first** — if the model isn't confident about a product match, ask the user rather than guess. Wrong affiliate links destroy trust.
2. **Chat is the UI** — don't build complex forms. Everything flows through the conversation.
3. **Mobile-first** — all UI decisions should work on a phone screen
4. **Affiliate links are the business model** — product suggestions must include affiliate tracking, only when confidence is high
5. **Firebase is the backend** — auth, Firestore for data, Storage for photos

---

## Out of Scope (MVP)
- Contractor marketplace / booking
- Renovation project management / budgets
- Smart home integrations (HomeKit, Home Assistant)

---

## Monetization Strategy
- Amazon Associates affiliate links (primary)
- Walmart affiliate program (secondary)
- Trigger: AI identifies exact replacement product from model number/photo
- Future: subscription tier for premium features (multi-property, export, priority reminders)
