# CivicAI – 5-Minute Competition Demonstration Guide

This guide provides a minute-by-minute presentation script designed to showcase every feature of CivicAI to judges, evaluators, and stakeholders within 5 minutes.

---

## ⏱️ Quick Demonstration Timeline

| Time | Stage | Page / URL | Core Focus & Judge Highlights |
|---|---|---|---|
| **0:00 - 0:45** | **Executive Overview** | [Home Page (`/`)](http://127.0.0.1:5001/) | Civic problem, dark navy theme, live SQLite KPIs. |
| **0:45 - 2:00** | **Citizen Submission & AI Engine** | [Submit (`/submit`)](http://127.0.0.1:5001/submit) | Real-time AI triage radar, category, priority scoring, duplicate detection. |
| **2:00 - 3:15** | **Admin GIS Map & Hotspots** | [Dashboard (`/admin`)](http://127.0.0.1:5001/admin) | Google Maps clarity, street/satellite switch, GIS hotspot clustering. |
| **3:15 - 4:15** | **Triage & Department Routing** | [Console (`/admin/complaints`)](http://127.0.0.1:5001/admin/complaints) | Triage modal, department/officer dispatch, SQLite persistence. |
| **4:15 - 5:00** | **Citizen Tracking & Resolution** | [Track (`/track`)](http://127.0.0.1:5001/track) | 5-stage stepper, Google Maps field pin, resolution closure banner. |

---

## 🎙️ Minute-by-Minute Presentation Script

### Minute 0:00 – 0:45 | Introduction & Problem Statement
- **Open**: [http://127.0.0.1:5001/](http://127.0.0.1:5001/)
- **Speaker**:
  > *"Judges, modern municipal grievance portals fail citizens for three reasons: complaints disappear into black boxes, duplicate submissions overwhelm departments, and urgent safety emergencies get buried under routine maintenance requests.*
  >
  > *This is CivicAI — a smart civic complaint management system designed to bring transparent AI triage, geospatial intelligence, and end-to-end audit accountability to municipal operations."*
- **Action**:
  - Point to the live KPI cards: **Total Complaints (40)**, **Pending (35)**, **Resolved (5)**, **Urgent (8)**.
  - Explain that every number is computed in real time from SQLite with zero hardcoded values.
  - Click **"Report a Problem"**.

---

### Minute 0:45 – 2:00 | Live AI Triage Radar & Duplicate Detection
- **Open**: [http://127.0.0.1:5001/submit](http://127.0.0.1:5001/submit)
- **Speaker**:
  > *"When a citizen files a complaint, CivicAI doesn't wait for submission to analyze it. Our live AI triage radar evaluates the issue as the citizen types in real time."*
- **Action**:
  1. Type in Description: `Water is entering houses because of road flooding near 5th Main Indiranagar.`
  2. Location: `Indiranagar 5th Main`.
  3. **Show the AI Live Triage Panel on the right**:
     - **Category**: Automatically detects `Waterlogging` (95% confidence).
     - **Priority**: Assigns `High Priority` (85/100) with explainable reasons:
       - *Risk to residential properties.*
       - *Potential safety hazard.*
       - *Immediate attention required.*
     - **Routing**: Recommends `Stormwater & Flood Management Division`.
  4. Now type in a duplicate test:
     - Clear and paste: `Heavy road flooding and water entering homes on Indiranagar 5th Main.`
     - **Show the Duplicate Banner**: CivicAI flags an instant amber alert:
       > *Matches existing complaint CIV-2026-SYN01 with 92% similarity in this vicinity.*
     - Explain how this prevents duplicate truck dispatches and saves city tax dollars.

---

### Minute 2:00 – 3:15 | Municipal Command Center & GIS Hotspot Clustering
- **Open**: [http://127.0.0.1:5001/admin](http://127.0.0.1:5001/admin)
- **Speaker**:
  > *"Now let's switch to the Municipal Control Center. City engineers need spatial awareness to deploy field crews efficiently."*
- **Action**:
  1. **Show the GIS Map**:
     - Point out the high-clarity **Google Maps** integration.
     - Click the layer switcher in the top right to toggle between **Google Streets** and **Google Satellite / Hybrid** to show building outlines and road labels.
  2. **Highlight Hotspots**:
     - Point to the animated concentric circles on the map.
     - Show the **Hotspot Intelligence Panel** on the right:
       - *Indiranagar Ward 12*: 8 complaints, Critical Severity (Waterlogging).
       - *Outer Ring Road*: 7 complaints, Critical Severity (Road Damage).
       - *Shivaji Market*: 7 complaints, Moderate Severity (Garbage).
  3. **Filter Map**:
     - Change the Category Filter to `Road Damage` $\rightarrow$ The map filters dynamically to only road incidents.
  4. **Click a Pin**:
     - Click a Red priority pin $\rightarrow$ Popup shows incident summary, tracking ID, priority badge, and an **"Open in Google Maps"** navigation button.

---

### Minute 3:15 – 4:15 | Administrative Triage & Lifecycle Dispatch
- **Open**: [http://127.0.0.1:5001/admin/complaints](http://127.0.0.1:5001/admin/complaints)
- **Speaker**:
  > *"In the Complaint Management Console, operations officers manage the end-to-end lifecycle across all 5 municipal stages."*
- **Action**:
  1. Click the **Triage** button on complaint `CIV-2026-SYN10` (Outer Ring Road crater).
  2. In the modal:
     - Update Status to `In Progress`.
     - Department: `Department of Roads & Infrastructure`.
     - Field Officer: `Engineer Ramesh Rao`.
     - Action Note: `Cold-mix asphalt patch truck dispatched with safety cones.`
     - Click **"Save & Apply Changes"**.
  3. Show the instant green toast notification and explain that both `complaints` and `activity_logs` tables in SQLite were updated atomically.

---

### Minute 4:15 – 5:00 | Citizen Tracking & Complete Transparency
- **Open**: [http://127.0.0.1:5001/track](http://127.0.0.1:5001/track)
- **Speaker**:
  > *"Finally, let's look at the citizen experience. Citizens can track their grievance anytime using their unique tracking ID without making phone calls."*
- **Action**:
  1. Click the quick demonstration pill: **`CIV-2026-SYN40 (Resolved)`** (or type `CIV-2026-SYN40`).
  2. Show the results:
     - **5-Stage Lifecycle Stepper**: All 5 steps (`Submitted`, `Under Review`, `Assigned`, `In Progress`, `Resolved`) completed with emerald green checkmarks.
     - **Resolution Banner**: Prominent green verified closure card showing official remediation remarks.
     - **Field Geolocation Map**: Exact incident coordinates on Google Maps with a 250m response perimeter.
     - **Redressal Audit Trail**: Full chronological log showing every officer, timestamp, and remark from submission to resolution.
  3. **Closing Statement**:
     > *"CivicAI transforms civic complaint handling from a slow, opaque paperwork process into a fast, transparent, AI-prioritized, and spatially intelligent system for citizens and city leaders alike. Thank you!"*

---

## 🏆 Key Talking Points for Judge Q&A

- **Q: Is the AI real or fake?**
  - **A**: *CivicAI uses transparent, explainable rule-based NLP and Jaccard n-gram similarity. We deliberately chose not to connect a mock external API or pretend to use an opaque black box. Every classification and priority score is 100% explainable and verifiable.*
- **Q: How does duplicate detection work?**
  - **A**: *It combines description keyword overlap, bigram phrasing, and geographic location constraint. If two complaints have similar text but are in separate neighborhoods 15 km apart, CivicAI knows they are separate incidents and does not flag a false duplicate.*
- **Q: How does hotspot detection work?**
  - **A**: *It uses Haversine spatial distance clustering with an 850-meter radius to find clusters of 2 or more active complaints, calculating the centroid and dominant failure category.*

