# Phase 11 — AI Receptionist (Add-On)

> **Goal**: Voice/SMS/web-chat AI receptionist for service businesses. This is a premium add-on feature, built after the core platform is stable. Uses the same knowledge base as the main agent.

## Status: NOT STARTED — LAST PRIORITY

## Dependencies
- Phase 0 (Foundation)
- Phase 1 (Agent) — shared reasoning architecture
- Phase 5 (Calendar) — appointment booking
- Phase 8 (Knowledge Base) — contextual answers

## Why Last
- Highest complexity: real-time voice AI + telephony integration
- Highest cost: per-minute charges, phone number provisioning
- Smallest initial user base: only relevant for phone-heavy businesses (HVAC, plumbing, salons)
- Can launch the full platform without it — most users need pages, courses, email first

## Alternative to Twilio (Cost Optimization)
Given the goal of avoiding high telephony costs, consider these alternatives:
1. **Vonage (Nexmo)** — competitive pricing, good voice API
2. **Plivo** — cheaper than Twilio for high volume
3. **Telnyx** — mission-grade, competitive pricing
4. **Web-only first**: Start with web chat widget only (zero telephony cost), add voice/SMS later
5. **SIP-based**: Use SIP trunking providers for cheaper per-minute rates

### Recommended approach: Start with **web chat widget only**, add voice via Telnyx or Plivo when demand justifies cost.

## Checklist

### Web Chat Widget (Start Here — No Telephony Cost)
- [ ] Embeddable chat widget (JavaScript snippet for user's website)
- [ ] Same AI brain as main agent (shared model, tools, KB)
- [ ] Custom appearance: colors, avatar, greeting message, position
- [ ] Capabilities: answer FAQs, collect leads, book appointments, qualify leads
- [ ] Office hours: different behavior during/after business hours
- [ ] Human handoff: "Transfer to human" → notification to owner (email/SMS)
- [ ] Chat transcript saved (for CRM lead creation)
- [ ] Typing indicator, read receipts
- [ ] Multi-language detection and response

### Voice Receptionist (Telnyx/Plivo — Later)
- [ ] Phone number provisioning (local or toll-free)
- [ ] Inbound call handling:
  - [ ] Greeting: custom voice persona (name, tone)
  - [ ] Speech-to-text: real-time transcription (Deepgram)
  - [ ] AI processing: KB-powered responses
  - [ ] Text-to-speech: ElevenLabs or provider TTS
  - [ ] Actions: book appointment, collect info, transfer call
- [ ] Outbound calls:
  - [ ] Appointment reminders
  - [ ] Follow-up calls
  - [ ] Callback scheduling
- [ ] Call recording (with consent prompt)
- [ ] Voicemail: customizable greeting, transcription, email notification

### SMS Handling
- [ ] Inbound SMS: auto-respond with AI
- [ ] Outbound SMS: appointment reminders, follow-ups
- [ ] SMS templates: configurable per scenario
- [ ] Opt-in/opt-out management (TCPA compliance)

### Training Interface
- [ ] Scenario builder: "If caller asks about X, respond with Y"
- [ ] Custom scripts: define conversation flows for common scenarios
- [ ] Knowledge base priority: which docs to search first for receptionist
- [ ] Test conversations: simulate calls/chats in dashboard
- [ ] Feedback loop: review transcripts, correct wrong answers → improve

### Business Hours Logic
- [ ] Schedule configuration: different scripts for business hours vs after-hours
- [ ] After-hours options: voicemail, SMS follow-up, emergency transfer
- [ ] Holiday schedule
- [ ] Timezone-aware

### Escalation Rules
- [ ] Urgency keywords: "emergency", "leak", "no heat" → immediate transfer
- [ ] Sentiment detection: frustrated/angry caller → transfer to human
- [ ] Topic-based: billing questions → transfer, general FAQ → AI handles
- [ ] Max AI turns: if AI can't resolve after N turns, offer human

### Analytics
- [ ] Call volume: daily, weekly, monthly
- [ ] Chat volume: same
- [ ] Resolution rate: % handled fully by AI vs transferred
- [ ] Booking conversion: % of interactions that result in appointment
- [ ] Common questions: word cloud / top queries
- [ ] Sentiment analysis: per-call/chat sentiment score
- [ ] Response time: average time to first response
- [ ] Cost tracking: per-minute spend, per-SMS spend

### Database Schema (Phase 11 additions)
```sql
CREATE TABLE receptionist_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT FALSE,
    persona_name VARCHAR(100) DEFAULT 'Assistant',
    greeting_message TEXT DEFAULT 'Hello! How can I help you today?',
    voice_id VARCHAR(100), -- ElevenLabs voice ID
    language VARCHAR(10) DEFAULT 'en',
    business_hours JSONB, -- same format as availability_schedules
    after_hours_action VARCHAR(50) DEFAULT 'voicemail', -- voicemail, sms, emergency_transfer
    escalation_keywords TEXT[] DEFAULT '{}',
    max_ai_turns INTEGER DEFAULT 10,
    custom_scripts JSONB DEFAULT '[]',
    kb_priority_docs UUID[] DEFAULT '{}', -- prioritized doc IDs
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE phone_numbers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    phone_number VARCHAR(20) NOT NULL,
    provider VARCHAR(50) NOT NULL, -- telnyx, plivo, twilio
    provider_id VARCHAR(255),
    number_type VARCHAR(20), -- local, toll_free
    country VARCHAR(2),
    is_active BOOLEAN DEFAULT TRUE,
    monthly_cost DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE call_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    phone_number_id UUID REFERENCES phone_numbers(id),
    direction VARCHAR(10) NOT NULL, -- inbound, outbound
    caller_number VARCHAR(20),
    status VARCHAR(50), -- completed, missed, voicemail, transferred
    duration_seconds INTEGER,
    recording_url TEXT,
    transcript TEXT,
    summary TEXT, -- AI-generated call summary
    sentiment_score DECIMAL(3,2), -- -1.0 to 1.0
    actions_taken JSONB DEFAULT '[]', -- [{type: "booked_appointment", details: {...}}]
    transferred_to VARCHAR(20),
    cost DECIMAL(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    visitor_id VARCHAR(255), -- anonymous visitor ID
    visitor_name VARCHAR(255),
    visitor_email VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active', -- active, closed, transferred
    channel VARCHAR(20) DEFAULT 'web', -- web, sms
    sentiment_score DECIMAL(3,2),
    actions_taken JSONB DEFAULT '[]',
    source_url TEXT, -- which page they started chat on
    created_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ
);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- visitor, assistant, system
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE sms_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    phone_number_id UUID REFERENCES phone_numbers(id),
    direction VARCHAR(10) NOT NULL,
    from_number VARCHAR(20),
    to_number VARCHAR(20),
    body TEXT,
    status VARCHAR(50), -- sent, delivered, failed
    cost DECIMAL(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Acceptance Criteria
- [ ] Web chat widget embeds on external site and works
- [ ] Chat widget answers questions from knowledge base
- [ ] Chat widget can book appointments (calendar integration)
- [ ] Chat widget collects leads (creates CRM contact)
- [ ] Human handoff works (notification to owner)
- [ ] Different behavior during/after business hours
- [ ] Chat analytics show volume, resolution rate, common queries
- [ ] Voice calls work (if telephony enabled)
- [ ] Call recording with consent
- [ ] SMS auto-responses work
- [ ] Training interface allows customization

## Known Risks
- Real-time voice latency: STT → LLM → TTS pipeline must be < 2 seconds for natural conversation
- Cost: Voice calls are $0.01-0.05/minute + LLM tokens per call. Can add up fast.
- Compliance: Call recording consent laws vary by state/country. Two-party consent states need explicit prompt.
- Voice quality: TTS voices must sound natural, not robotic. ElevenLabs is good but costs ~$0.30/1K chars.

## What's Next
This is the final phase. After this, focus on growth, optimization, and user feedback.
