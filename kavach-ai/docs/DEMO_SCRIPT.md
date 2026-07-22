# KAVACH AI: Hackathon Demo Script (6-8 Minutes)

## 1. Problem Statement (45 seconds)
**Speaker**: "Cyber fraud in India has evolved into highly organized, multi-hop rings operating across district borders. Today, when a citizen reports a Digital Arrest scam, the data sits isolated in local jurisdiction silos. By the time the dots are connected, the money is gone."
**Action**: Show a static slide or briefly show the empty dashboard.
**Speaker**: "Enter KAVACH AI: an event-driven intelligence platform that connects the dots instantly."

## 2. Architecture Overview (45 seconds)
**Action**: Display `ARCHITECTURE.md` diagram.
**Speaker**: "We built 6 distinct microservices. A FastAPI Gateway handles intake. Kafka streams events to our LangGraph AI Orchestrator, which extracts entities. Those entities are streamed into a Neo4j Graph for network analysis and a PostGIS database for geospatial clustering. All of this feeds into our National Cyber Command Center in real-time."

## 3. The National Cyber Command Center (60 seconds)
**Action**: Open `http://localhost:3000` (Dashboard).
**Speaker**: "Here is the Command Center. Notice the live intelligence feed on the right—Kafka is actively streaming system events. The KPIs are updating. In a degraded environment, if our Graph database goes down, React Query isolates the failure, keeping the rest of the dashboard online."

## 4. Geospatial Intelligence (45 seconds)
**Action**: Click the "Threat Map" tab.
**Speaker**: "Our Geospatial service runs incremental DBSCAN clustering on the fly. You can see a massive high-risk hotspot in Mewat, Haryana. We don't just plot pins; we cluster threat densities so patrols can be dispatched efficiently."

## 5. Fraud Network Analysis (60 seconds)
**Action**: Click the "Fraud Network" tab.
**Speaker**: "By extracting entities using our Llama-3 AI, we push relationships into Neo4j. Here, you see Fraud Ring Alpha. Notice how 25 different complaints from across the country all link back to a single shared UPI ID and Phone Number. We found the nexus."

## 6. Explainable AI Analysis (60 seconds)
**Action**: Click the "AI Intelligence" tab.
**Speaker**: "Law enforcement can't act on a black box. Our AI Orchestrator provides a 92% threat score for this Digital Arrest case. More importantly, it provides a chronologically verifiable timeline of how it reached that conclusion, and actionable recommendations—like freezing the specific HDFC account."

## 7. Wrap-up (30 seconds)
**Speaker**: "We didn't just build a dashboard; we built a horizontally scalable, event-driven intelligence backbone that can integrate with national infrastructure tomorrow. Thank you."
