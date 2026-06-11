# Streaming and Production Patterns

## Overview

Production-grade agent applications require streaming responses for real-time feedback and proper response finalization. This skill covers streaming patterns and distinguishes between development and production approaches.

## Streaming vs Non-Streaming

### When to Use Streaming

**Production applications:** Always use streaming for:
- Real-time user feedback
- Long-running operations
- Interactive applications
- Web services
- Chat interfaces

**Testing/Development:** Non-streaming acceptable for:
- Unit tests
- Quick validation
- Simple scripts
- Debugging

## Production-Grade Streaming Pattern

### The Complete Pattern

```python
print("Agent: ", end="", flush=True)
stream = agent.run("hello", stream=True)
async for chunk in stream:
    if chunk.text:
        print(chunk.text, end="", flush=True)
print("\n")
await stream.get_final_response()  # CRITICAL: Must finalize
```

### Key Components

1. **Enable streaming** - `stream=True` parameter
2. **Iterate chunks** - `async for chunk in stream:`
3. **Check text content** - `if chunk.text:`
4. **Flush output** - `flush=True` ensures immediate display
5. **Finalize** - `await stream.get_final_response()` is mandatory

### Why Each Step Matters

**stream=True**
- Enables real-time chunked responses
- Without this, response is buffered until complete

**if chunk.text:**
- Chunks contain different content types
- Only text chunks have displayable content
- Other chunks (metadata, events) need filtering

**flush=True**
- Ensures immediate console output
- Important for real-time UX
- Without it, output may buffer

**get_final_response() (MANDATORY)**
- Finalizes the streaming session
- Commits response to session history (if using sessions)
- Without this, state may not be persisted
- Must be awaited - it's async

## Non-Streaming Pattern (Testing Only)

### Simple Execution

```python
result = await agent.run("hello")
print(f"Agent: {result.text}")
```

### Use Case

- Unit tests
- Simple scripts
- Debugging
- Quick validation

### Limitations

- No real-time feedback
- Entire response buffered in memory
- Blocks until complete response received

## Chunk Structure

### Available Chunk Attributes

```python
async for chunk in stream:
    # Check text content
    if chunk.text:
        print(chunk.text, end="", flush=True)
    
    # Check for tool calls or other events
    if chunk.raw_representation:
        event = chunk.raw_representation.raw_representation
        # Process event...
```

### Event Processing Example

```python
async for chunk in stream:
    if chunk.text:
        print(chunk.text, end="", flush=True)
    elif chunk.raw_representation and chunk.raw_representation.raw_representation:
        event = chunk.raw_representation.raw_representation
        if (hasattr(event, 'type') 
            and event.type == 'response.output_item.done' 
            and hasattr(event, 'item') 
            and hasattr(event.item, 'name')):
            args = getattr(event.item, 'arguments', None)
            status = getattr(event.item, 'status', None)
            print(f"\n[Tool: {event.item.name}] args={args} status={status}")
```

## Streaming with Sessions

### Stateful Streaming

```python
session = agent.create_session()

stream = agent.run(
    "What's the weather in Seattle?",
    session=session,
    stream=True
)

async for chunk in stream:
    if chunk.text:
        print(chunk.text, end="", flush=True)
print("\n")
await stream.get_final_response()  # Persists to session
```

### Important: Finalization Persists History

Without `await stream.get_final_response()`:
- Streaming works fine
- Response displays correctly
- **BUT:** Session history is not persisted
- Subsequent calls won't have access to previous messages

This is why finalization is **MANDATORY** for stateful applications.

## Handling Streaming Errors

### Error During Stream

```python
try:
    stream = agent.run("query", stream=True)
    async for chunk in stream:
        if chunk.text:
            print(chunk.text, end="", flush=True)
    await stream.get_final_response()
except Exception as e:
    print(f"\nError: {e}")
    # Don't finalize if error occurred
```

### Graceful Shutdown

```python
stream = agent.run("query", stream=True)
try:
    async for chunk in stream:
        if chunk.text:
            print(chunk.text, end="", flush=True)
finally:
    # Always finalize, even on error
    await stream.get_final_response()
```

## Performance Considerations

### Memory Usage

**Streaming:**
- Processes chunks as they arrive
- Minimal memory overhead
- Good for long responses

**Non-streaming:**
- Buffers entire response
- Higher memory for large responses
- Acceptable for small responses

### Latency

**Streaming:**
- User sees first token immediately
- Lower perceived latency
- Better UX

**Non-streaming:**
- User waits for complete response
- Higher perceived latency

## Web Service Integration

### Streaming to HTTP Response

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

@app.post("/ask")
async def ask_agent(query: str):
    async def generate():
        stream = agent.run(query, stream=True)
        async for chunk in stream:
            if chunk.text:
                yield chunk.text
        await stream.get_final_response()
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

## Deprecated Pattern (DO NOT USE)

```python
# ❌ WRONG - run_stream is deprecated
stream = agent.run_stream("hello")
async for chunk in stream:
    print(chunk)
```

**Use instead:**
```python
# ✅ CORRECT
stream = agent.run("hello", stream=True)
async for chunk in stream:
    if chunk.text:
        print(chunk.text, end="", flush=True)
await stream.get_final_response()
```

## Best Practices

1. **Always use streaming in production** - Better UX
2. **Always finalize** - `await stream.get_final_response()`
3. **Filter chunk content** - Check `chunk.text` before printing
4. **Use flush=True** - For real-time output
5. **Use sessions for stateful** - Save context between calls
6. **Handle errors gracefully** - Try/finally with finalization
7. **Test streaming behavior** - Verify finalization works

## Testing Streaming

### Unit Test Example

```python
async def test_agent_streaming():
    agent = Agent(client, name="TestAgent", instructions="...")
    
    chunks = []
    stream = agent.run("test query", stream=True)
    async for chunk in stream:
        if chunk.text:
            chunks.append(chunk.text)
    final = await stream.get_final_response()
    
    assert len(chunks) > 0
    assert final is not None
    assert final.text == "".join(chunks)
```

---

*Related: Session Management, Agent Creation, HTTP Server Deployment*
