# Kavach — Demo Video Script
**Target length: 3 minutes · Screen recording + voiceover**

---

### 0:00–0:20 — Cold open: the stakes
**Visual:** Slide 2 from the deck (stat cards) or a simple black screen with the three numbers appearing one at a time.

> "In 2023, India logged 1.14 million cybercrime complaints — up 60% in a single year. In just nine months of 2024, 'digital arrest' scams alone cost citizens over ₹1,776 crore. These aren't lone scammers — they're industrialised operations, often running from fraud compounds across the border. And by the time a complaint is filed, the money is already gone."

---

### 0:20–0:40 — The reframe
**Visual:** Architecture diagram (`kavach-architecture.svg`), slow pan left to right across the five layers.

> "The problem isn't a lack of evidence after the fact. It's a lack of intelligence before the transfer happens. That's what Kavach is built for — a digital public safety grid that fuses scam-pattern detection, counterfeit vision, fraud-network graphs, and geospatial intelligence into one system, so law enforcement can act at the point of contact, not the point of complaint."

---

### 0:40–1:00 — Introduce the flagship module
**Visual:** Cut to slide 6 (the 4-step flow), then transition into the live browser.

> "Today we're showing the flagship module live: Kavach Shield. It's a citizen-facing tool that assesses digital-arrest scam risk in real time — and every verdict you're about to see is a genuine AI inference, not a scripted demo."

---

### 1:00–1:55 — Live walkthrough (screen recording of `kavach-shield.html`)
**Action beats — record these exactly, in order:**

1. Open the tool. Let the console header and helpline badge sit on screen for 2 seconds.
2. Click the **"CBI parcel scam"** example chip — the textarea auto-fills.
3. Check 3–4 relevant quick-signal boxes (impersonation, video call, urgency, payment demand).
4. Click **"Assess Risk Now."** Let the loading state ("Running classifier...") play fully — don't cut it.
5. When the verdict renders: pause on the gauge animating up to a high score, then pan to the indicator chips and recommended actions.
6. Expand the **"Simulated intelligence alert payload"** panel — hold for 3 seconds so the JSON is readable.

**Voiceover (plays under the recording):**

> "A citizen describes what happened — or just taps the signals that match. The model scores it against known digital-arrest patterns: official impersonation, forced video presence, isolation from family, urgency, and payment demands. In seconds, it returns a risk score, a plain-language explanation, and a ranked list of what to do right now — starting with 'hang up' and 'call 1930,' never 'trust the caller.' Behind the scenes, every high-risk verdict also generates a structured, timestamped alert payload — the shape of what would route to MHA, NCRB, or a telecom provider in production, and what a court would need to see for admissibility."

---

### 1:55–2:15 — Prove the low-false-positive design
**Action:** Reload the tool (or clear it), click the **"Genuine bank alert"** example chip, leave signal boxes unchecked, click Assess.

> "And because false alarms erode trust just as fast as missed scams cost money, we calibrated it the other way too — a genuine bank fraud-alert call, with no OTP or PIN request and no arrest threat, correctly scores low risk."

---

### 2:15–2:40 — Zoom out to the full platform
**Visual:** Deck slide 4 (five-agent grid), then slide 10 (roadmap).

> "Kavach Shield is phase one. The same orchestration layer is designed to carry a Counterfeit Vision Agent for banks and field officers, a Graph Intelligence Agent to map mule networks across jurisdictions, a Geospatial Agent for patrol prioritisation, and a Voice Spoof Agent for AI-cloned callers — all feeding one command centre, and all feeding back into the classifiers as confirmed cases come in."

---

### 2:40–3:00 — Close
**Visual:** Deck slide 12 (closing card).

> "The goal isn't a smarter complaint form. It's catching the call while it's still live. Kavach — a shield, not just software."

**End card on screen:** Kavach logo mark · "National Cybercrime Helpline — 1930 · cybercrime.gov.in" · team name.

---

## Production notes
- Record the live tool at 1280×900 or larger so the verdict card and JSON panel are legible.
- Keep the loading-state animation in the final cut once — it visibly proves the call is live, not cached.
- If recording in a language other than English, switch the **Response Language** dropdown before the "Assess Risk Now" click so the on-screen verdict matches the voiceover language.
- Do not speed up the classifier response — the 2–4 second wait is a proof point, not a flaw.
