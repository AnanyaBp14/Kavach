// Kavach Shield — backend server
// Serves the frontend and exposes a single API endpoint that calls the
// Groq API server-side (the API key never reaches the browser).
// Groq offers a free, no-credit-card tier — see README for setup.

require("dotenv").config();
const express = require("express");
const path = require("path");
const Groq = require("groq-sdk");

const app = express();
const PORT = process.env.PORT || 3000;
const MODEL = process.env.GROQ_MODEL || "llama-3.3-70b-versatile";

if (!process.env.GROQ_API_KEY) {
  console.warn(
    "\n⚠️  GROQ_API_KEY is not set. Copy .env.example to .env and add your key.\n" +
    "   Get a free key (no credit card) at https://console.groq.com/keys\n"
  );
}

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
});

app.use(express.json({ limit: "100kb" }));
app.use(express.static(path.join(__dirname, "public")));

// Basic in-memory rate limiting (per IP) — replace with a real store (Redis)
// before production use at scale. Kept conservative to stay under Groq's
// free-tier per-minute request cap (shared across the whole app).
const RATE_LIMIT_WINDOW_MS = 60 * 1000;
const RATE_LIMIT_MAX = 10;
const hits = new Map();

function rateLimit(req, res, next) {
  const ip = req.ip;
  const now = Date.now();
  const windowStart = now - RATE_LIMIT_WINDOW_MS;
  const timestamps = (hits.get(ip) || []).filter((t) => t > windowStart);
  if (timestamps.length >= RATE_LIMIT_MAX) {
    return res.status(429).json({ error: "Too many requests. Please wait a minute and try again." });
  }
  timestamps.push(now);
  hits.set(ip, timestamps);
  next();
}

const SYSTEM_PROMPT_TEMPLATE = (lang) => `You are a classifier trained on patterns from India's "digital arrest" scam wave (CBI/ED/Customs/RBI impersonation, video-call psychological coercion, fake warrants, urgency + isolation + payment demands) as well as common genuine-caller scenarios (real bank fraud alerts, real courier delays, etc). Reference known MHA/NCRB advisory patterns.

Given a citizen's free-text description and/or checked signal tags, output a risk assessment.

Respond with ONLY a raw JSON object (no markdown fences, no preamble), with this exact shape:
{
  "risk_score": <integer 0-100>,
  "verdict_short": "<3-6 word verdict>",
  "explanation": "<2-3 sentence explanation of WHY, written for a worried citizen, in ${lang}>",
  "indicators": ["<short indicator phrase>", ...up to 6, in ${lang}],
  "recommended_actions": ["<short actionable step>", ...4-6 steps, in ${lang}, ordered by urgency],
  "confidence": "<low|medium|high>"
}

Calibration: genuine bank/delivery calls that never ask for OTP/PIN/full card number and don't threaten arrest should score LOW (under 25). Any call combining official impersonation + urgency + isolation + payment/OTP demand should score HIGH (75+). Be precise — false positives on genuine calls erode citizen trust, false negatives cost lives' savings.`;

app.post("/api/assess", rateLimit, async (req, res) => {
  try {
    const { story, signals, lang } = req.body || {};
    const safeStory = typeof story === "string" ? story.slice(0, 4000) : "";
    const safeSignals = Array.isArray(signals) ? signals.slice(0, 20).map(String) : [];
    const safeLang = typeof lang === "string" && lang.length < 40 ? lang : "English";

    if (!safeStory.trim() && safeSignals.length === 0) {
      return res.status(400).json({ error: "Provide a description or at least one signal." });
    }

    const completion = await groq.chat.completions.create({
      model: MODEL,
      temperature: 0.2,
      max_tokens: 1000,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: SYSTEM_PROMPT_TEMPLATE(safeLang) },
        {
          role: "user",
          content: JSON.stringify({
            citizen_description: safeStory || "(no free text provided)",
            checked_signals: safeSignals,
          }),
        },
      ],
    });

    const text = (completion.choices[0]?.message?.content || "")
      .trim()
      .replace(/^```json\s*|```$/g, "")
      .trim();

    let result;
    try {
      result = JSON.parse(text);
    } catch (e) {
      console.error("Model returned non-JSON:", text);
      return res.status(502).json({ error: "Classifier returned an unexpected response. Please try again." });
    }

    // Basic shape validation before trusting the model output downstream.
    if (typeof result.risk_score !== "number") {
      return res.status(502).json({ error: "Classifier response was incomplete. Please try again." });
    }

    const alertPayload = {
      alert_type: "DIGITAL_ARREST_SCAM_SUSPECTED",
      generated_at: new Date().toISOString(),
      risk_score: result.risk_score,
      confidence: result.confidence,
      indicators: result.indicators,
      source: "Kavach Shield — Citizen Self-Report",
      routing:
        result.risk_score >= 66
          ? ["MHA Cyber Alert Queue", "NCRB 1930 Pre-fill Draft", "Telecom Caller-ID Flag (if number provided)"]
          : ["Logged for pattern analysis only — below alert threshold"],
      evidence_hash: "sha256:" + require("crypto").randomBytes(24).toString("hex"),
      note: "Simulated payload for demo purposes — illustrates evidence packaging for court-admissible intelligence.",
    };

    res.json({ ...result, alert_payload: alertPayload });
  } catch (err) {
    console.error(err);
    if (err?.status === 401) {
      return res.status(500).json({ error: "Server misconfigured: GROQ_API_KEY is missing or invalid." });
    }
    if (err?.status === 429) {
      return res.status(429).json({ error: "Groq's free-tier rate limit was hit. Wait a moment and try again." });
    }
    res.status(500).json({ error: "Something went wrong while assessing risk. Please try again." });
  }
});

app.get("/api/health", (req, res) => res.json({ status: "ok" }));

app.listen(PORT, () => {
  console.log(`Kavach Shield server running at http://localhost:${PORT}`);
});
