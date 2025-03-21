LangGraph (for multi-agent workflows, LangRPG-style coordination) and
Pydantic-AI (for schema enforcement and inter-agent validation).

The system is already integrated with a hotel admin dashboard. The LLM
must modify or trigger changes to the admin dashboard when required,
including reflecting guest requests in real time or updating booking
data.

🔄 Split Workflows:

🧳 Guest-Facing (Customer) Features:

1\. Check-ins (ID + payment verification) --- syncs with CRM booking
info

2\. Entertainment (sleep stories, meditations)

3\. Cab booking

4\. Room service requests (e.g. towels, pillows)

5\. Extend stay

6\. Laundry alerts

7\. Stock-up requests (e.g. coffee, tea, sugar)

8\. Door access (matches guest booking ID with room door ID)

9\. Trip planner

10\. Food recommendations

11\. Critical complaints logging

12\. Wellness mode (2-3 min breathing or meditation session)

13\. Book meeting rooms, spa, gym

14\. Time-aware reasoning (use time/date to recommend or prepare for
upcoming events)

15\. RAG-enabled hotel events module (e.g. happy hours, theme nights via
admin input)

16\. Alarm or reminder setting with app notifications

🏨 Admin-Facing (Business Owner) Features:

• View and manage incoming guest requests (check-in, room service,
laundry, etc.)

• Get alerts from LLM agents (e.g. critical complaints, alarm reminders,
spa bookings)

A rag module for admin to add details of hotel like (car parking info,
checkin, checkout info, etc )

• View suggested updates to guest itineraries or stay durations

• Input events and promotions into RAG module (happy hours, theme
nights, etc.)

• Approve or reject LLM-driven decisions when needed

• View analytics on agent workflows (e.g. most requested services,
delays)

📦 Technical Requirements:

• Use LangGraph to model autonomous agent flows for each major hotel
operation.

• Use Pydantic-AI to define structured schemas for agent communication
and data validation.

• Each agent must have clear input/output schemas, memory (where
needed), and be independently testable.

• Agents must be able to:

• Trigger updates to the admin dashboard (via API or DB layer)

• Access time, date, and booking context

• React to user inputs from the guest landing page

• Build 2 UI layers: one for Guest interactions, one for Admin actions.

• Support external integrations (e.g. CRM, IoT door locks, calendar
APIs, cab booking APIs).

• Design an event-driven architecture where LLM agent outputs trigger
real-time admin updates.

• Provide a plug-and-play interface for adding new agents.

📦 Deliverables:

1\. High-level system architecture diagram

2\. Python project layout with modular directories

3\. Three sample agents (e.g. CheckinAgent, RoomServiceAgent,
WellnessAgent)

4\. LangGraph flow connecting agents based on guest queries

5\. Pydantic-AI models for inter-agent messaging

6\. Example admin dashboard update API or DB integration

7\. Webhook or CLI to trigger workflows

8\. Tests for agent logic and flow coordination

All code should be async-compatible, follow clean architecture, and
include docstrings and type hints. Include setup instructions and
configuration loading using .env.
