# Session Management

## Overview

Sessions enable stateful, multi-turn conversations by maintaining context across agent interactions. This skill covers creating, using, and managing sessions for context persistence.

## What is a Session?

**Session** = Persistent conversation context

A session:
- Stores conversation history
- Maintains context between turns
- Enables multi-turn reasoning
- Can be serialized and restored
- Improves agent decision-making

## Basic Session Usage

### Creating a Session

```python
session = agent.create_session()
```

**Notes:**
- Create once per conversation
- Reuse across multiple agent.run() calls
- Each session is independent

### Single-Turn with Session

```python
session = agent.create_session()

result = await agent.run("What's the weather?", session=session)
print(result.text)
```

### Multi-Turn with Session

```python
session = agent.create_session()

# Turn 1
result1 = await agent.run("What's the weather in Seattle?", session=session)
print(f"Q1: {result1.text}")

# Turn 2 - Agent remembers "Seattle"
result2 = await agent.run("Should I bring an umbrella?", session=session)
print(f"Q2: {result2.text}")

# Turn 3 - Full context maintained
result3 = await agent.run("Thanks! Any other tips?", session=session)
print(f"Q3: {result3.text}")
```

## Streaming with Sessions

### Critical: Always Finalize

```python
session = agent.create_session()

# Turn 1: Streaming with finalization
stream = agent.run("Question 1?", session=session, stream=True)
async for chunk in stream:
    if chunk.text:
        print(chunk.text, end="", flush=True)
print("\n")
await stream.get_final_response()  # MUST finalize

# Turn 2: Finalization persists history
stream = agent.run("Follow-up question?", session=session, stream=True)
async for chunk in stream:
    if chunk.text:
        print(chunk.text, end="", flush=True)
print("\n")
await stream.get_final_response()  # MUST finalize
```

### Why Finalization Matters

Without `await stream.get_final_response()`:
- ✅ Streaming works fine
- ✅ Response displays correctly
- ❌ Session history NOT persisted
- ❌ Next turn loses context

## Session State Management

### What Sessions Store

```
Session contains:
├─ Message History
│  ├─ User messages
│  ├─ Agent responses
│  └─ Tool call logs
├─ Context
│  └─ Information from previous turns
└─ Metadata
   ├─ Timestamps
   └─ Session ID
```

### Information Persistence

```python
session = agent.create_session()

# Turn 1: Introduce information
await agent.run(
    "My name is Alice and I work in finance",
    session=session
)

# Turn 2: Agent remembers Alice and finance role
response = await agent.run(
    "What task should I do?",  # No name/role mentioned
    session=session
)
# Agent can reference Alice and her role from history
```

## Session Storage

### Default: In-Memory Store

```python
session = agent.create_session()
# Uses in-memory storage
# Data lost when agent closes
```

**Use for:**
- Development/testing
- Short-lived conversations
- Debugging

### Persistent Storage (Advanced)

For production-grade persistence:
- Search agent-framework source repo for examples
- May involve database backing
- Custom session handlers
- Serialization/deserialization

**Example use cases:**
- Long-term conversation history
- Multi-session user interactions
- Analytics and logging

## Multi-Turn Conversation Pattern

### Complete Example

```python
async def multi_turn_assistant():
    client = FoundryChatClient(
        project_endpoint="...",
        model="...",
        credential=DefaultAzureCredential(),
    )
    
    async with Agent(
        client=client,
        name="Assistant",
        instructions="You are a helpful assistant that remembers context."
    ) as agent:
        session = agent.create_session()
        
        # Setup turn
        await agent.run(
            "I'm planning a trip to Japan for 2 weeks in April.",
            session=session
        )
        
        # Context turn 1
        response1 = await agent.run(
            "What's the weather like?",
            session=session
        )
        print(f"Q1: {response1.text}")
        
        # Context turn 2
        response2 = await agent.run(
            "What should I pack?",
            session=session
        )
        print(f"Q2: {response2.text}")
        
        # Refinement turn
        response3 = await agent.run(
            "Any specific recommendations for Tokyo?",
            session=session
        )
        print(f"Q3: {response3.text}")
```

## Session with Tools

### Tool State Across Turns

```python
def get_weather(
    city: Annotated[str, "City name"]
) -> str:
    """Get weather for city."""
    return f"Sunny in {city}"

session = agent.create_session()

# Turn 1: Get weather for Seattle
await agent.run(
    "Tell me the weather in Seattle",
    session=session
)

# Turn 2: Agent remembers Seattle, may use tool again
response = await agent.run(
    "Is it better than last week?",
    session=session
)
# Agent has context of Seattle weather from Turn 1
```

### Tool Results in History

Session stores:
- Which tools were called
- What arguments were passed
- What results were returned
- Agent's use of results

## Session Context Window

### Context Awareness

Agents consider:
- Entire conversation history
- All previous tool calls
- All previous results
- Cumulative context

### Large Conversations

For very long conversations:
- Context window may fill up
- Agent behavior depends on model limits
- Consider summarization for very long sessions
- Typically not an issue for < 100 turns

## Advanced Session Patterns

### Conditional Sessions

```python
should_remember = True  # User preference

if should_remember:
    session = agent.create_session()
else:
    session = None  # Stateless

result = await agent.run("Query", session=session)
```

### Session Per User

```python
user_sessions = {}  # user_id -> session

def get_user_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = agent.create_session()
    return user_sessions[user_id]

# In request handler
user_session = get_user_session(request.user_id)
result = await agent.run(request.query, session=user_session)
```

### Session Cleanup

```python
user_sessions = {}

async def chat_endpoint(user_id: str, message: str):
    # Get or create session
    if user_id not in user_sessions:
        user_sessions[user_id] = agent.create_session()
    
    session = user_sessions[user_id]
    result = await agent.run(message, session=session)
    
    # Optional: cleanup old sessions
    if len(user_sessions) > 1000:
        # Remove oldest sessions
        oldest_user = min(user_sessions, key=lambda k: user_sessions[k].created_at)
        del user_sessions[oldest_user]
    
    return result
```

## Session Testing

### Unit Test with Session

```python
async def test_multi_turn_context():
    session = agent.create_session()
    
    # Setup
    await agent.run("I like coffee", session=session)
    
    # Test context is remembered
    response = await agent.run(
        "What do I like?",
        session=session
    )
    
    assert "coffee" in response.text.lower()
```

## Best Practices

1. **Always use sessions** for multi-turn applications
2. **Always finalize streams** - `await stream.get_final_response()`
3. **Create once per conversation** - Don't recreate needlessly
4. **Reuse across turns** - Same session for entire conversation
5. **Handle cleanup** - Manage session lifecycle
6. **Test context** - Verify information persists
7. **Consider persistence** - For production scenarios
8. **Monitor performance** - Long sessions may slow down

## Troubleshooting

### Session Context Lost

- **Symptom:** Agent forgets earlier information
- **Check:** Are you calling `await stream.get_final_response()`?
- **Fix:** Always finalize streams before next turn

### Memory Issues

- **Symptom:** Application memory grows with sessions
- **Check:** Are old sessions being cleaned up?
- **Fix:** Implement session cleanup/expiration

### Session Serialization

- **Symptom:** Can't save/restore sessions
- **Check:** Are you using custom persistence?
- **Fix:** Implement serialization handlers (framework-dependent)

---

*Related: Streaming Patterns, Agent Creation, Multi-Agent Workflows*
