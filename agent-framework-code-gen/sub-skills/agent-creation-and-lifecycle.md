# Agent Creation and Lifecycle

## Overview

Creating and managing agent instances is the core capability of the Microsoft Agent Framework. This skill covers agent instantiation, lifecycle management, and naming conventions.

## Agent Creation Methods

### Method 1: Agent Constructor with async with (Recommended)

**Best practice for context management:**

```python
from agent_framework import Agent

async with Agent(
    client=client,
    name="MyAgent",
    instructions="You are a helpful agent."
) as agent:
    # Use agent here
    result = await agent.run("hello")
    # Cleanup happens automatically
```

**Advantages:**
- Automatic resource cleanup via context manager
- Clear scope visibility
- Guaranteed proper teardown

### Method 2: Client as_agent Method

**Alternative pattern:**

```python
agent = client.as_agent(
    name="MyAgent",
    instructions="You are a helpful agent."
)
```

**Use when:**
- Managing multiple agents without context managers
- Need explicit lifecycle control

### Method 3: Manual Agent Lifecycle

```python
agent = Agent(
    client=client,
    name="MyAgent",
    instructions="You are a helpful agent."
)

# Use agent...
await agent.run("hello")

# Manual cleanup if needed
await agent.aclose()
```

## Mandatory: DO NOT Use `create_agent()`

The method `create_agent()` is deprecated. Always use:
- `Agent(client, ...)` constructor, or
- `client.as_agent(...)` method

```python
# ❌ WRONG
agent = create_agent(client, name="...", instructions="...")

# ✅ CORRECT
agent = Agent(client, name="...", instructions="...")
```

## Agent Naming Conventions

### Naming Rules

Agents must follow these rules for deployment readiness:

- **Start and end with alphanumeric characters** (a-z, A-Z, 0-9)
- **Can contain hyphens in the middle** (-) for readability
- **Not exceed 63 characters** in length

### Valid Agent Names

✅ Good examples:
- `SampleAgent`
- `agent-1`
- `myagent`
- `weather-assistant`
- `document-analyzer-v2`

### Invalid Agent Names

❌ Bad examples:
- `-agent` (starts with hyphen)
- `agent-` (ends with hyphen)
- `sample_agent` (uses underscore)
- `my.agent` (uses period)
- `my agent` (uses space)
- `a` (too short, though technically valid)
- `-myagent-` (starts and ends with hyphen)

### Naming Best Practices

1. **Use descriptive names** - Reflects agent purpose
2. **Use hyphens for separation** - `weather-assistant` instead of `weatherassistant`
3. **Avoid special characters** - Stick to alphanumerics and hyphens
4. **Keep it concise** - Memorable and less likely to exceed 63 chars

## Core Agent Parameters

### Required Parameters

```python
Agent(
    client=...,          # FoundryChatClient instance (required)
    name="...",          # Agent name following conventions (required)
    instructions="..."   # System instructions for agent (required)
)
```

### Optional Parameters

```python
Agent(
    client=...,
    name="...",
    instructions="...",
    tools=[...],         # List of tools/functions (optional)
    system_prompt="..." # Alternative to instructions (optional)
)
```

## Agent Execution Patterns

### Basic Execution

```python
result = await agent.run("hello")
print(f"Response: {result.text}")
```

### With Session (Stateful)

```python
session = agent.create_session()
result = await agent.run("hello", session=session)
```

### Streaming Execution

```python
stream = agent.run("hello", stream=True)
async for chunk in stream:
    if chunk.text:
        print(chunk.text, end="", flush=True)
await stream.get_final_response()
```

## Agent Lifecycle States

1. **Created** - Agent object instantiated
2. **Active** - Inside context manager or explicitly activated
3. **Running** - Executing a task with `agent.run()`
4. **Idle** - Waiting for next task
5. **Closed** - Cleanup completed

## Resource Management

### Context Manager (Recommended)

```python
async with Agent(client, name="...", instructions="...") as agent:
    # Resources acquired
    await agent.run("task")
    # Resources automatically released
```

### Manual Resource Cleanup

```python
agent = Agent(client, name="...", instructions="...")
try:
    await agent.run("task")
finally:
    await agent.aclose()
```

## Error Handling

### Invalid Name Handling

```python
try:
    agent = Agent(
        client=client,
        name="invalid-name-with-underscore_here",
        instructions="..."
    )
except ValueError as e:
    print(f"Invalid agent name: {e}")
    # Fix the name and retry
```

### Client Not Available

```python
try:
    agent = Agent(client=None, name="...", instructions="...")
except TypeError as e:
    print(f"Client required: {e}")
```

## Best Practices

1. **Always use async with** when possible for automatic cleanup
2. **Follow naming conventions strictly** for deployment compatibility
3. **Reuse client instances** across multiple agents
4. **Keep instructions concise but complete** - guides agent behavior
5. **Test agent with simple inputs first** - verify basic functionality
6. **Don't create agents in loops** - Reuse instances when possible

---

*Related: Client Setup, Tool Integration, Session Management*
