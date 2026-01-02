# Async Agent Question Handling

When agents are triggered via webhooks (async, non-interactive), they cannot use interactive tools like `askUserQuestion` that expect real-time user input. This document outlines the architecture for handling agent questions in async scenarios.

## Current Implementation

Interactive tools (`askUserQuestion`) are **disabled** for webhook-triggered agents. The agent must work with the information provided in the webhook payload.

## Future Architecture: Async Question Handling

For scenarios where agents genuinely need clarification or additional input, we can implement an async callback system with human-in-the-loop.

### High-Level Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Webhook   │────▶│    Agent     │────▶│  Question       │
│   Trigger   │     │   Executor   │     │  Detected       │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                   │
                    ┌──────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    STATE PERSISTENCE                         │
│  - Save agent execution state (session_id)                  │
│  - Store pending question + context                         │
│  - Record original payload + progress                       │
└─────────────────────────────────────┬───────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────┐
          ▼                           ▼                       ▼
┌─────────────────┐       ┌─────────────────┐      ┌─────────────────┐
│  Callback URL   │       │   Slack Bot     │      │    Web UI       │
│  (webhook out)  │       │   Integration   │      │   Dashboard     │
└────────┬────────┘       └────────┬────────┘      └────────┬────────┘
         │                         │                        │
         └─────────────────────────┼────────────────────────┘
                                   ▼
                    ┌──────────────────────────┐
                    │  POST /answer/{session}  │
                    │  { "answer": "..." }     │
                    └──────────────┬───────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │   Resume Agent from      │
                    │   Saved State            │
                    └──────────────────────────┘
```

### Database Schema

```sql
CREATE TABLE agent_sessions (
    id TEXT PRIMARY KEY,                    -- UUID session ID
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'running', -- running, pending_input, completed, failed
    original_payload JSON NOT NULL,
    execution_state JSON,                   -- serialized agent state for resumption
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_questions (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES agent_sessions(id),
    question TEXT NOT NULL,
    context JSON,                           -- additional context for the question
    answer TEXT,
    answered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_status ON agent_sessions(status);
CREATE INDEX idx_questions_session ON agent_questions(session_id);
```

### API Endpoints

#### 1. Get Pending Questions

```http
GET /agent/questions?status=pending
```

Response:
```json
{
  "questions": [
    {
      "id": "q-123",
      "session_id": "sess-456",
      "agent_name": "write-poem",
      "question": "What style would you prefer? (free verse, rhyming, sonnet, haiku)",
      "context": {
        "original_topic": "love",
        "asked_at": "2024-01-01T12:00:00Z"
      }
    }
  ]
}
```

#### 2. Submit Answer

```http
POST /agent/answer/{session_id}
Content-Type: application/json

{
  "question_id": "q-123",
  "answer": "haiku"
}
```

Response:
```json
{
  "ok": true,
  "status": "resumed",
  "session_id": "sess-456"
}
```

#### 3. Get Session Status

```http
GET /agent/session/{session_id}
```

Response:
```json
{
  "id": "sess-456",
  "agent_name": "write-poem",
  "status": "completed",
  "result": {
    "poem_path": "poem/love-haiku-2024.md"
  },
  "questions_asked": 1,
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:05:00Z"
}
```

### Callback Webhook (Optional)

When a question is generated, send a callback to a configured URL:

```http
POST {callback_url}
Content-Type: application/json
X-Agent-Session: sess-456

{
  "event": "question_pending",
  "session_id": "sess-456",
  "agent_name": "write-poem",
  "question": {
    "id": "q-123",
    "text": "What style would you prefer?",
    "options": ["free verse", "rhyming", "sonnet", "haiku"],
    "context": { "topic": "love" }
  },
  "answer_url": "https://your-server.com/agent/answer/sess-456"
}
```

### Integration Options

#### Slack Integration

```python
# When question is pending, send to Slack
async def notify_slack(question: AgentQuestion):
    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Agent Question*\n{question.text}"}
        },
        {
            "type": "actions",
            "elements": [
                {"type": "button", "text": {"type": "plain_text", "text": opt}, 
                 "action_id": f"answer_{question.id}_{opt}"}
                for opt in question.options
            ]
        }
    ]
    await slack_client.post_message(channel=AGENT_CHANNEL, blocks=blocks)
```

#### Email Integration

```python
async def notify_email(question: AgentQuestion, recipient: str):
    body = f"""
    An agent needs your input:
    
    Question: {question.text}
    
    Click to answer:
    - Option A: {answer_url}?answer=a
    - Option B: {answer_url}?answer=b
    
    Or reply to this email with your answer.
    """
    await send_email(to=recipient, subject="Agent Question", body=body)
```

### Configuration

```python
# settings.py
class Settings:
    # Async question handling
    agent_question_callback_url: str | None = None  # URL to POST questions to
    agent_question_timeout_seconds: int = 3600      # 1 hour timeout for answers
    agent_question_notify_slack: bool = False
    agent_question_slack_channel: str | None = None
```

### Implementation Phases

#### Phase 1 (Current)
- Disable interactive tools for webhook agents
- Agent works with payload data only

#### Phase 2
- Add `agent_sessions` and `agent_questions` tables
- Implement question persistence
- Add `/agent/answer/{session_id}` endpoint

#### Phase 3
- Add callback webhook support
- Implement session resumption

#### Phase 4
- Slack bot integration
- Web UI for question management
- Email notifications

### Edge Cases

1. **Question Timeout**: If no answer within `agent_question_timeout_seconds`, fail the session or use a default answer.

2. **Multiple Questions**: Agent may ask multiple questions. Queue them all and present together, or handle sequentially.

3. **Session Expiry**: Clean up old sessions after configurable period.

4. **Duplicate Answers**: Ignore duplicate answer submissions; only first answer counts.

5. **Invalid Session**: Return 404 if session doesn't exist or is already completed.

### Example Agent Config

For agents that may need questions in async mode:

```yaml
# agents/complex-research.md
---
name: complex-research
model: sonnet
async_questions: true  # Enable async question handling
question_callback: https://hooks.slack.com/...
question_timeout: 3600
---
```

When `async_questions` is enabled:
- `askUserQuestion` becomes an async operation
- Questions are persisted and callbacks sent
- Agent pauses until answer received or timeout

