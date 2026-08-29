# ⚡ RevMatrix AI — Autonomous AI Revenue Recovery Engine
### **Razorpay Buildathon — Track 03: AI Revenue Recovery**
*Find revenue that's slipping away and win it back autonomously across Indian payment rails.*

---

## 📋 Hackathon Submission Answers (Copy & Paste Ready)

### 🏷️ 1. Project Name / Title
> **RevMatrix AI — Autonomous Multi-Channel Revenue Recovery Engine with Cryptographic Auditability & Bounded Escalations**

---

### 🎯 2. Project Objectives: What does it solve?
> In Indian SaaS, D2C, and B2B commerce, 10% to 25% of top-line revenue is silently lost to payment degradation, checkout drop-offs, involuntary subscription churn, and aged receivables. Traditional dunning relies on dumb fixed-interval retries and ignored email blasts.
> 
> **RevMatrix AI closes the entire loop from detection to diagnosis, intervention, and settlement:**
> 1. **Payment Degradation & Root Cause Diagnosis:** Detects real-time issuer bank degradations (e.g. SBI/Paytm downtime) and distinguishes Soft vs Hard declines with confidence scoring.
> 2. **Checkout Drop-Off 1-Click Rescue:** Rescues abandoned checkouts within minutes using dynamic 1-click Razorpay UPI intent links and smart incentives.
> 3. **Failed Subscription Dunning:** Prevents involuntary churn with automated instrument swaps and conversational renewal links.
> 4. **B2B Receivables Chaser:** Multi-tier compliant aged-debt escalation (AP Reminder → CFO Alert → Legal notice draft) with automated Razorpay Smart Invoices.
> 5. **Mandate Retry Sequencer:** Optimizes UPI Autopay & card retries around Indian salary cycles (1st–7th of month) and NPCI peak success clearing windows.
> 6. **Hinglish AI Voice Recovery:** High-converting, respectful conversational Hinglish audio desk for Indian customers.
> 7. **Promise-to-Pay (PTP) State Machine:** Extracts natural date commitments, halts suspension, and schedules reminder queues.
> 8. **"The Bar" Compliance & Cryptographic Audit Trail:** Bounded anti-harassment stopping rules (3 attempts/48h, RBI quiet hours 9 PM–8 AM, dispute freezes) with tamper-evident SHA-256 block-linked audit logs and measurable batch ROI (₹ & %).

---

### 🧗 3. Build Challenges & Technical Obstacles: What issues did you face and how did you solve them?
> 1. **Differentiating Soft vs Hard Declines across Indian Banks:** Error codes from Indian gateways vary widely. We built a normalized heuristic classification matrix combined with real-time bank switch health telemetry so expired cards are never spammed, and degraded bank downtime triggers smart delays.
> 2. **Anti-Harassment Guardrails & Regulatory Quiet Hours:** Preventing over-communication required implementing strict stateful stopping rules: enforcing RBI quiet hours (9 PM to 8 AM IST), auto-freezing recovery outreach immediately upon dispute/chargeback detection, and capping attempts to 3 contacts per 48 hours.
> 3. **Natural Promise-to-Pay (PTP) Commitment Parsing:** Indian consumers frequently make commitments like *"Salary 5th ko aayegi, tab pay karunga"* or *"Friday ko clear karta hoon"*. We engineered an intent parser and state machine that extracts target dates, sets automated holds on service cancellation, and activates timely reminder queues.
> 4. **Verifiable Auditability ("The Bar"):** To ensure every agent action, tool invocation, and stopping rule is tamper-evident for finance controllers, we created a cryptographic SHA-256 block-linked audit trail engine.

---

## 🏗️ System Architecture

```
                                  ┌──────────────────────────────────────────────┐
                                  │      RevMatrix AI Core Orchestrator          │
                                  │     (FastAPI + Python Agent Engine)          │
                                  └──────────────────────┬───────────────────────┘
                                                         │
               ┌─────────────────────────────────────────┼─────────────────────────────────────────┐
               ▼                                         ▼                                         ▼
┌───────────────────────────────┐         ┌───────────────────────────────┐         ┌───────────────────────────────┐
│     1. Diagnostic Engine      │         │     2. Autonomous Workers     │         │      3. Recovery Channels     │
├───────────────────────────────┤         ├───────────────────────────────┤         ├───────────────────────────────┤
│ • Root-cause classifier       │         │ • Mandate Sequencer Agent     │         │ • 1-Click Razorpay UPI Links  │
│ • Bank downtime telemetry     │         │ • B2B Receivables Chaser      │         │ • Hinglish Voice Agent Engine │
│ • Hard vs Soft Decline model  │         │ • Drop-Off Rescue Worker      │         │ • WhatsApp / SMS Simulator    │
│ • Salary/Payday prediction    │         │ • PTP State Machine           │         │ • Email Dunning Dispatcher    │
└───────────────────────────────┘         └───────────────────────────────┘         └───────────────────────────────┘
                                                         │
                                                         ▼
                                  ┌──────────────────────────────────────────────┐
                                  │       Real-Time Executive Dashboard          │
                                  │  (Live Batch Recovery, Audio Agent, Audit)   │
                                  └──────────────────────────────────────────────┘
```

---

## 🌟 The 7 Unified Recovery Pillars

| # | Feature / Direction | How RevMatrix AI Implements It | Razorpay API / Tool Executed |
|---|---|---|---|
| 1 | **Payment Degradation & Root-Cause Diagnosis** | Real-time gateway anomaly detector (bank downtime, 3DS latency spikes, soft vs hard decline classification) | Dynamic route fallback, smart delay, Razorpay Orders API |
| 2 | **Checkout Drop-Off Recovery** | Detects abandoned checkouts & cart dropouts; triggers contextual multi-channel rescue with dynamic 1-click UPI intent links | Razorpay Payment Links API, WhatsApp Business API Simulation |
| 3 | **Failed Subscription Recovery (Dunning)** | Handles recurring card/mandate failures with progressive smart dunning and payment method switching | Razorpay Subscriptions API, Customer Update APIs |
| 4 | **B2B Receivables & Invoice Chaser** | Autonomous aged-debt recovery with compliant multi-tier escalations (Gentle Reminder -> CFO Alert -> Legal Notice draft) | Razorpay Invoices API, Smart Payment Links |
| 5 | **Mandate Retry Sequencer (UPI Autopay & Cards)** | ML/Heuristic engine that predicts optimal retry windows based on salary dates (1st-7th), bank success rate heatmaps, and time-of-day | Razorpay Mandates / Subscriptions Retry Scheduler |
| 6 | **Hinglish Conversational Voice/Chat Recovery** | Natural Hinglish AI recovery agent with audio playback & interactive chat for high conversion among Indian consumers | Web Speech / Audio Engine + WhatsApp Chatbot |
| 7 | **Promise-to-Pay (PTP) Tracker** | Conversational agreement parsing ("I will pay this Friday"); sets automated hold on account suspension and triggers precision reminders | State Machine with scheduled trigger queue & SLA manager |

---

## 🚀 Quickstart & Local Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
# or: pip install fastapi uvicorn razorpay httpx pydantic pydantic-settings
```

### 2. Start Application
```bash
python run.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

### 3. Run Automated Integration Tests (Optional)
```bash
python test_verification.py
```

---

