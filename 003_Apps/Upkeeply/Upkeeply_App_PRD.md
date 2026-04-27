## 1–2 sentence summary

A mobile app (iOS + Android) that tracks home assets (HVAC, pools, spas, safety devices) and automates maintenance reminders by letting users talk to a built‑in chat model, upload photos of equipment labels, and sync reminders to calendars, email, and SMS.[1][2]

***

## Product vision

Create the **fastest way** for a homeowner to go from “I did this maintenance task” or “I need to remember this” to a fully tracked asset with smart, recurring reminders and a searchable history—without manual data entry or complex setup.[2][1]

Success looks like:

- Users can log a new asset and a first reminder in under 60 seconds via chat + photo.  
- Users trust the app enough to centralize all key maintenance (filters, pools/spas, smoke detectors) instead of defaulting to generic reminder apps.[3][1]

***

## Target users & primary use cases

**Primary users**

- Single‑family homeowners or long‑term renters who:  
  - Have HVAC systems, at least one smoke/CO detector, and possibly a pool or spa.  
  - Use smartphones daily and already rely on Google/Apple Calendar, email, or SMS notifications.[4][3]

**Core use cases (MVP)**

1. “I just did a task.”  
   - User: “I replaced my upstairs air filter today, here’s a photo of the unit label.”  
   - App: Extracts equipment model, infers filter size/interval, creates asset “Upstairs HVAC,” logs the event, and schedules the next reminder.

2. “Set up a system.”  
   - User: “I have a saltwater pool, keep me on top of filters and chlorine.”  
   - App: Asks 2–3 clarifying questions (size, climate, usage) and generates a maintenance plan template with recurring tasks.

3. “Safety compliance.”  
   - User: “Track all my smoke detectors and remind me to test monthly and change batteries yearly.”  
   - App: Creates multiple assets (by room) and linked recurring tasks with grouped notifications.  

4. “Global schedule view + integrations.”  
   - User sees a calendar/list of upcoming tasks and can sync/remap specific tasks to Google/Apple Calendar or opt into email/SMS for critical items.[5][6]

***

## Key features (MVP)

### A. Conversational capture with photos (core differentiator)

- Chat interface as default home screen.  
- Users can:  
  - Type or dictate maintenance events (“Drained and refilled spa today”).  
  - Attach photos of labels, equipment, receipts, or the work done.  
- Backend:  
  - Extracts manufacturer/model, key specs (e.g., filter size), and recommended maintenance intervals from label text + web manuals where possible.[7][8][5]
  - Auto‑creates or updates an **Asset** and links the **Task** to it.

### B. Asset & task model

- **Assets**: HVAC unit, pool, spa, smoke detector, etc., each with:  
  - Name, category, location, manufacturer, model, serial (optional), photos.  
  - Key parameters (e.g., filter size, chlorine type, salt vs. chlorine pool).  
- **Tasks**:  
  - Fields: asset, title, description, frequency (fixed interval, seasonal, or manual), due date, last completed date.  
  - History: log of completions with optional notes and photos.

### C. Opinionated templates for HVAC, pools, spa, safety

- Prebuilt templates for:  
  - Air filter replacement, coil cleaning, HVAC service.  
  - Pool: filter cleaning/backwash, chlorine/salt checks, shock, pH tests.[9][5]
  - Spa/Jacuzzi: filter cleaning, sanitizer maintenance, water change.  
  - Smoke/CO detectors: testing cadence and battery replacement.[10][1]
- Chat model suggests these templates automatically based on user messages + photos.

### D. Reminders & integrations

- Reminder channels per user and per task:  
  - Push notifications (default).  
  - Calendar sync: create/update events in Google Calendar and Apple Calendar.  
  - Email notifications; SMS for “critical” tasks if user enables.  
- Simple settings for reminder timing (e.g., 7 days before, day‑of, and overdue nudges).  

### E. Household & timeline

- Multi‑device and multi‑user: invite household members by email.  
- Unified **Timeline** per asset and global view: “What did I do to the pool this year?”  
- Export options:  
  - ICS for calendar tasks.  
  - CSV/JSON backup of assets/tasks for trust/transparency.[5]

***

## Non‑functional requirements

- **Platforms:** iOS first (iPhone), then Android; responsive API for possible web dashboard.  
- **Performance:** Core flows (open app → log task via chat) must feel real‑time on 4G.  
- **Reliability:**  
  - Offline‑first where possible with local queue of events.  
  - Safe sync and conflict handling; no silent data loss.  
- **Privacy:**  
  - Photos and extracted data encrypted at rest and in transit.  
  - Clear policy on how long media is stored and how it’s used.  

***

## Out of scope (MVP)

- Contractor marketplace or booking (TaskRabbit/Angi style).  
- Full renovation/project management and budgeting dashboards.  
- Smart‑home direct integrations (Home Assistant, HomeKit, etc.)—these can come after core is stable.[6][1]

***

## Five name recommendations

Each is designed to feel consumer‑friendly, easy to remember, and clearly about “home + upkeep + memory.”

1. **HouseMind** – Implies the app “remembers” and thinks about your house so you don’t have to.  
2. **KeepUp Home** – Speaks directly to staying ahead of maintenance; easy to verbalize (“I use KeepUp”).  
3. **HomeMemento** – Emphasizes the stored memory of everything done to the home, plus photos.  
4. **NudgeNest** – Slightly playful; “nest” = home, “nudge” = gentle reminders.  
5. **Upkeeply** – Modern, SaaS‑y vibe centered on home upkeep and recurring care.

