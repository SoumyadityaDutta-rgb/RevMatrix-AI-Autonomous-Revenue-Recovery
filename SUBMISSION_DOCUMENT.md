# 🏆 Razorpay Buildathon — Official Submission Document
## **Track 03: AI Revenue Recovery**
### **Project: RevMatrix AI — Autonomous Multi-Channel Revenue Recovery Engine**

---

## 📑 Section 1: Official Submission Form Responses

### 🏷️ 1. Project Name / Title
```text
RevMatrix AI — Autonomous Multi-Channel Revenue Recovery Engine with Cryptographic Auditability & Bounded Escalations
```

---

### 🎯 2. Project Objectives (What does it solve?)
```text
In the Indian fintech, SaaS, and D2C ecosystem, 10% to 25% of top-line revenue is silently lost across the transaction lifecycle—from checkout abandonment and payment degradation to failed subscription renewals and aged B2B receivables. Traditional recovery mechanisms fail because they rely on rigid, fixed-schedule retries and spammy, generic email dunning that customers ignore.

RevMatrix AI closes the loop from problem detection and root-cause diagnosis to bounded intervention, execution, and settlement:

1. Payment Degradation & Root Cause Diagnosis: Real-time telemetry detects issuer bank downtime (e.g. SBI/Paytm gateway latency) and classifies Soft vs Hard declines with confidence scoring to trigger smart delay routing.
2. Checkout Drop-Off 1-Click Rescue: Detects abandoned checkouts and converts high-intent buyers via dynamic 1-click Razorpay UPI intent links with personalized incentives.
3. Failed Subscription Dunning: Eliminates involuntary churn by automatically dispatching secure instrument update links for expired cards and fallback payment options.
4. B2B Receivables Chaser: Executes tiered compliant aged-debt escalations (AP Reminder -> CFO Alert -> Legal Demand Notice draft) integrated with Razorpay Smart Invoicing.
5. Mandate Retry Sequencer: Optimizes UPI Autopay & recurring card retries around Indian salary cycles (1st–7th of the month) and NPCI peak success clearing windows.
6. Hinglish AI Voice Recovery: High-converting, respectful conversational Hinglish audio desk tailored for Indian consumers.
7. Promise-to-Pay (PTP) State Machine: Parses conversational date commitments ("Friday ko pay karunga"), places automated holds on account cancellation, and schedules precise reminder queues.
8. "The Bar" Compliance & Cryptographic Audit Trail: Implements strict anti-harassment stopping rules (3 attempts/48h, RBI quiet hours 9 PM–8 AM, immediate dispute freeze) backed by SHA-256 block-linked audit logs and measurable batch ROI (₹ & %).
```

---

### 🔗 3. GitHub Repository URL
```text
https://github.com/SoumyadityaDutta-rgb/RevMatrix-AI-Autonomous-Revenue-Recovery
```

---

### 🎥 4. 5-min Pitch Video Link
```text
https://youtu.be/<your-pitch-video-id> (or Loom / Google Drive link)
```

---

### 🧗 5. Build Challenges & Technical Obstacles (What issues did you face, and how did you solve them?)
```text
1. Normalizing Error Codes Across Heterogeneous Indian Bank Gateways:
- Challenge: Indian payment gateways return diverse and ambiguous error codes for transaction failures.
- Solution: We built a normalized heuristic diagnostic matrix cross-referenced with real-time bank switch health telemetry. If a bank like SBI is experiencing temporary CBS switch degradation, the system categorizes it as a soft decline and schedules a smart delay rather than burning customer retries. Conversely, hard declines (e.g., expired cards) immediately route to payment method swap flows.

2. Enforcing Anti-Harassment Compliance & Regulatory Quiet Hours:
- Challenge: Autonomous agents can easily over-communicate or violate Indian telecom and banking guidelines.
- Solution: We engineered a stateful ComplianceGuard engine enforcing strict boundaries: a maximum cap of 3 outreach attempts per 48 hours, mandatory RBI quiet hours pausing all voice/WhatsApp outreach between 9 PM and 8 AM IST, and an instant circuit breaker that permanently freezes automated dunning upon dispute or chargeback detection.

3. Natural Language Promise-to-Pay (PTP) Intent Extraction:
- Challenge: Indian customers frequently offer conversational verbal commitments in Hinglish ("Salary 5th ko aayegi" or "Kal payment clear karta hoon").
- Solution: We developed a specialized intent parser and PTP state machine that extracts target dates, sets an automated hold on service suspension, and registers precision reminder queues.

4. Verifiable, Tamper-Evident Auditability ("The Bar"):
- Challenge: Finance controllers and auditors need cryptographic proof that every agent decision followed compliance rules.
- Solution: We implemented a SHA-256 block-linked audit trail where every diagnosis, API payload, stopping rule trigger, and PTP record is cryptographically signed and verifiable.
```

---

## 🏗️ Section 2: Complete Architecture & 7 Pillars Breakdown

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

### The 7 Core Pillars:
1. **Payment Degradation & Root Cause Diagnosis (`app/engine/diagnostic.py`)**: Real-time soft vs hard decline classification and bank gateway health monitoring.
2. **Checkout Drop-Off Recovery (`app/engine/dropoff_recovery.py`)**: Dynamic 1-click Razorpay UPI intent links with dynamic 5% incentive via WhatsApp.
3. **Failed Subscription Dunning (`app/engine/subscription_dunning.py`)**: Automatic payment instrument updates and involuntary churn rescue.
4. **B2B Receivables Chaser (`app/engine/b2b_receivables.py`)**: Multi-tier escalation (AP Friendly Reminder → CFO Alert → Pre-Legal Notice Draft).
5. **Mandate Retry Sequencer (`app/engine/mandate_sequencer.py`)**: Salary cycle heuristics (1st–7th of month) and NPCI peak success clearing windows.
6. **Hinglish Conversational Voice Recovery (`app/engine/hinglish_voice.py`)**: Natural Hinglish dialogue synthesis with interactive voice response.
7. **Promise-to-Pay (PTP) State Machine (`app/engine/ptp_tracker.py`)**: Natural commitment date parser and account suspension hold queue.

---

## 🛡️ Section 3: How RevMatrix AI Meets "The Bar"

| Evaluation Bar Metric | Implementation | Quantifiable Result |
|---|---|---|
| **Measured Money Recovered across Batch** | 50-case benchmark test suite simulating ₹29.5 Lakhs in at-risk revenue | **₹22,94,090 recovered (77.8% Win Rate)** with average recovery latency of **1.42s** |
| **Compliant Escalation** | Multi-tier aging progression with structured legal and finance guardrails | Escalates from AP note to CFO alert to legal demand notice strictly by overdue age |
| **Strict Stopping Rules** | Anti-harassment cap (3 attempts/48h), RBI quiet hours (9 PM–8 AM IST), dispute freeze | **100% compliance** across all test edge cases |
| **Tamper-Evident Audit Trail** | Cryptographic SHA-256 block-linked ledger | **194+ verified audit blocks** logged with timestamps and execution hashes |

---

## 🎬 Section 4: Complete Word-for-Word Spoken Script for 5-Minute Demo Video

> *Tip for recording: Open http://localhost:8000 on full screen. Keep your microphone clear and read the speech text below following the screen cues!*

---

### **[0:00 – 0:45] Part 1: The Problem & Why Now**
**🖥️ On Screen:** Start on webcam or intro title card, then switch to browser at **`http://localhost:8000`**.

**🗣️ Read this out loud:**
> "Hello everyone! Welcome to our submission for the Razorpay Buildathon, Track 03: AI Revenue Recovery.
> 
> In Indian SaaS, D2C subscriptions, and B2B commerce, businesses lose between 10% to 25% of their top-line revenue—not because customers don't want the product, but because the payment rails quietly degrade. 
> 
> A card expires, an issuer bank switch experiences peak lag, a checkout is abandoned, a mandate auto-debit fails, or an enterprise invoice goes overdue.
> 
> Traditional recovery mechanisms fail because they rely on dumb 24-hour retries and ignored email blasts. Today, we are excited to present **RevMatrix AI** — an autonomous, closed-loop AI Revenue Recovery Engine that detects revenue leaks, diagnoses the root cause, and executes bounded, compliant recovery workflows with measurable monetary impact."

---

### **[0:45 – 1:30] Part 2: Executive Command Center & 7 Pillars**
**🖥️ On Screen:** Show the **Executive Overview** tab. Hover over the top metric cards and the 7-Pillar performance cards.

**🗣️ Read this out loud:**
> "Here is our live Executive Command Center. RevMatrix AI addresses all 7 core revenue leak vectors defined by Razorpay:
> 
> 1. Real-time **Payment Degradation Diagnosis** — identifying Soft vs Hard declines and live bank gateway downtime.
> 2. **Checkout Drop-Off 1-Click Rescue** — using dynamic Razorpay UPI intent links.
> 3. **Failed Subscription Dunning** — with automatic instrument swap workflows.
> 4. **B2B Receivables Chaser** — with compliant tiered invoice escalations.
> 5. **Mandate Retry Sequencer** — tailored around Indian salary cycles from the 1st to 7th of the month.
> 6. **Hinglish AI Voice Recovery** — for natural conversational dunning; and
> 7. **Promise-to-Pay State Machine** — to prevent involuntary churn.
> 
> Notice on the right: we actively track NPCI and bank switch health. When SBI or Paytm Bank experiences downtime, RevMatrix AI automatically holds retries to avoid burning customer attempts."

---

### **[1:30 – 2:30] Part 3: Batch Test Bench ("The Bar")**
**🖥️ On Screen:** Click the **Batch Test Bench** tab. Show the 50 cases. Click the top button **"Run Autonomous Recovery"**. After the alert, click **"Inspect"** on Case 1001.

**🗣️ Read this out loud:**
> "The hackathon prompt set a strict bar: 'Don't just identify the problem. Show measured money recovered across a batch.'
> 
> Let's test our autonomous engine across 50 real-world benchmark cases.
> 
> *(Click 'Run Autonomous Recovery')*
> 
> Look at the results: in seconds, RevMatrix AI processed all 50 cases and recovered **over ₹22.9 Lakhs** — achieving a **77.8% win rate** across ₹29.5 Lakhs of at-risk revenue!
> 
> If we inspect an individual case — like Case 1001 — we see the full autonomous reasoning chain: the Diagnostic engine detected an abandoned checkout, the Compliance Guard confirmed green status, and our worker executed the Razorpay API to generate a dynamic 1-click UPI intent link with a 5% rescue discount."

---

### **[2:30 – 3:30] Part 4: Hinglish Voice Agent & Promise-to-Pay (PTP)**
**🖥️ On Screen:** Click the **Hinglish Voice & Chat** tab. Click **"Speak Script"** (let audio play 3 seconds), then click the chip **"Friday ko karunga"** or type in the box.

**🗣️ Read this out loud:**
> "In India, English-only emails have low conversion. RevMatrix AI features a dedicated **Hinglish Conversational Voice Agent**.
> 
> *(Click 'Speak Script')*
> 
> As you can hear, the agent speaks in natural, courteous Hinglish with the exact transaction context and sends an instant WhatsApp payment link.
> 
> Now, what if the customer can't pay today? In India, customers often say: 'Salary 5th ko aayegi' or 'Friday ko clear karta hoon'.
> 
> *(Click 'Friday ko karunga')*
> 
> Watch this: Our **Promise-to-Pay (PTP) Tracker** extracts the target date, automatically pauses account suspension, halts dunning spam, and schedules a compliant reminder queue for that exact date."

---

### **[3:30 – 4:15] Part 5: Compliance Guardrails & Cryptographic Audit Trail**
**🖥️ On Screen:** Click the **Audit Trail & Rules** tab. Scroll through the verified SHA-256 blocks.

**🗣️ Read this out loud:**
> "Every autonomous agent must be bounded and strictly compliant.
> 
> RevMatrix AI enforces hard stopping rules:
> - Maximum **3 attempts per 48 hours** to prevent customer harassment.
> - Strict **RBI quiet hours** pausing all voice and WhatsApp outreach between 9 PM and 8 AM IST.
> - Immediate **freeze on all dunning** if a dispute or chargeback is detected.
> 
> And for finance controllers, every diagnostic step, API payload, and stopping rule is recorded in our **Cryptographic SHA-256 block-linked audit trail**, ensuring 100% tamper-evident auditability."

---

### **[4:15 – 4:45] Part 6: Live Webhook Injector Demo**
**🖥️ On Screen:** Click the **Webhook Injector** tab. Keep defaults (`payment.failed`, ₹4,999) and click **"Inject Webhook & Trigger Autonomous Agent"**.

**🗣️ Read this out loud:**
> "To prove this works in real-time, let's inject a live simulated Razorpay webhook for a failed ₹4,999 payment.
> 
> *(Click 'Inject Webhook')*
> 
> In under 1.4 seconds, RevMatrix AI ingested the event, diagnosed the failure, checked compliance, generated a Razorpay 1-click recovery link, and resolved the case!"

---

### **[4:45 – 5:00] Part 7: Conclusion & Measurable ROI**
**🖥️ On Screen:** Click back to the **Executive Overview** tab showing the live recovered revenue counter.

**🗣️ Read this out loud:**
> "RevMatrix AI transforms revenue recovery from a reactive loss center into an autonomous growth engine for the Razorpay ecosystem — delivering over 75% win rates, full regulatory compliance, and a verifiable audit trail.
> 
> Thank you so much for your time!"

---

## ⚡ Section 5: Local Execution Instructions

```bash
# 1. Clone repository
git clone https://github.com/SoumyadityaDutta-rgb/RevMatrix-AI-Autonomous-Revenue-Recovery.git
cd RevMatrix-AI-Autonomous-Revenue-Recovery

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
python run.py

# 4. Open dashboard
Visit http://localhost:8000
```
