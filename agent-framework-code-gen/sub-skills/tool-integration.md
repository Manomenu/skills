# Tool Integration

## Overview

Tools (Function Calling) enable agents to interact with external APIs, databases, and services. This skill covers defining, integrating, and managing custom tools for agents.

## Tool Definition Basics

### Mandatory: Use Type Annotations with Annotated

**Required pattern:**

```python
from typing import Annotated

def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."
```

### Why This Pattern?

- `Annotated[type, "description"]` provides both type and documentation
- The string description tells the agent how to use the parameter
- Enables the agent to make intelligent decisions about when/how to call

### Components

1. **Function name** - Descriptive, snake_case
2. **Parameters** - Annotated with type and description
3. **Return type** - Explicitly declared
4. **Docstring** - Explains what the function does

## Tool Registration with Agent

### Single Tool

```python
async with Agent(
    client=client,
    name="MyAgent",
    instructions="You are a helpful agent.",
    tools=[get_weather],  # Pass as list
) as agent:
    result = await agent.run("What's the weather in Seattle?")
```

### Multiple Tools

```python
def get_time(zone: Annotated[str, "Timezone (e.g., 'UTC', 'PST')"]) -> str:
    """Get current time in specified timezone."""
    # Implementation...
    pass

def get_location(address: Annotated[str, "Street address"]) -> dict:
    """Get coordinates from address."""
    # Implementation...
    pass

tools = [get_weather, get_time, get_location]

async with Agent(
    client=client,
    name="MyAgent",
    instructions="You are a helpful agent.",
    tools=tools,
) as agent:
    result = await agent.run("What's the weather in Seattle right now?")
```

## Tool Parameter Types

### Supported Types

```python
def tool_example(
    name: Annotated[str, "Agent's name"],
    age: Annotated[int, "Age in years"],
    confidence: Annotated[float, "Confidence score 0.0-1.0"],
    is_active: Annotated[bool, "Whether active"],
    tags: Annotated[list[str], "List of tags"],
    config: Annotated[dict, "Configuration dictionary"],
) -> str:
    """Example tool with various parameter types."""
    pass
```

### Optional Parameters

```python
from typing import Optional

def search(
    query: Annotated[str, "Search query"],
    max_results: Annotated[Optional[int], "Max results (default 10)"] = None,
) -> list[dict]:
    """Search for documents."""
    max_results = max_results or 10
    # Implementation...
    pass
```

## Tool Execution Flow

### Agent's Decision Making

1. **Analyze request** - Agent reads user query
2. **Check available tools** - Looks at registered tools
3. **Decide on usage** - Determines if/when to call tool
4. **Call with args** - Invokes function with parameters
5. **Use result** - Incorporates response in final answer

### Example: Multi-Turn with Tools

```python
session = agent.create_session()

# First turn: Agent decides to use tool
stream = agent.run(
    "What's the weather in Seattle?",
    session=session,
    stream=True
)
async for chunk in stream:
    if chunk.text:
        print(chunk.text, end="", flush=True)
await stream.get_final_response()

# Second turn: Agent uses context from first
stream = agent.run(
    "How should I dress?",  # No location specified
    session=session,
    stream=True
)
async for chunk in stream:
    if chunk.text:
        print(chunk.text, end="", flush=True)
await stream.get_final_response()
```

The agent remembers "Seattle" from the first turn and applies the weather to the second question.

## Tool Error Handling

### Robust Tool Implementation

```python
def get_data(
    source: Annotated[str, "Data source name"],
) -> dict:
    """Fetch data from source."""
    try:
        if not source:
            return {"error": "Source name required"}
        
        data = fetch_from_source(source)
        
        if not data:
            return {"error": f"No data found for {source}"}
        
        return {"status": "success", "data": data}
    
    except Exception as e:
        return {"error": f"Failed to fetch: {str(e)}"}
```

### Agent Handles Errors

The agent framework:
- Catches exceptions from tools
- Includes errors in reasoning
- May retry with different parameters
- Or inform user of failure

## Tool Best Practices

### 1. Clear Documentation

```python
def book_flight(
    from_city: Annotated[str, "Departure city (e.g., 'San Francisco')"],
    to_city: Annotated[str, "Destination city (e.g., 'New York')"],
    date: Annotated[str, "Departure date (YYYY-MM-DD format)"],
) -> dict:
    """Book a flight between two cities on specified date."""
    pass
```

### 2. Specific Descriptions

❌ **Vague:**
```python
location: Annotated[str, "where"]
```

✅ **Clear:**
```python
location: Annotated[str, "City name (e.g., 'Seattle', 'New York') for weather lookup"]
```

### 3. Type Safety

```python
from typing import Literal

def process(
    action: Annotated[
        Literal["create", "update", "delete"],
        "Action to perform"
    ]
) -> str:
    """Process document with specific action."""
    pass
```

### 4. Return Meaningful Data

```python
# ❌ Not helpful
return "ok"

# ✅ Informative
return {
    "status": "success",
    "items_processed": 42,
    "next_action": "review_results",
    "details": [...]
}
```

### 5. Consistent Error Format

```python
def tool():
    try:
        # Implementation
        pass
    except Exception as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "suggestion": "Try again with..."
        }
```

## Performance Considerations

### Tool Response Time

- **Fast tools** (< 1s) - Good for interactive use
- **Medium tools** (1-5s) - Acceptable with streaming
- **Slow tools** (> 5s) - Consider async patterns

### Rate Limiting

```python
import asyncio
from datetime import datetime, timedelta

class RateLimitedTool:
    def __init__(self, max_calls=10, window_seconds=60):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = []
    
    def __call__(self, *args, **kwargs):
        now = datetime.now()
        # Clean old calls
        self.calls = [
            call_time for call_time in self.calls
            if now - call_time < timedelta(seconds=self.window_seconds)
        ]
        
        if len(self.calls) >= self.max_calls:
            raise Exception(f"Rate limit exceeded: {self.max_calls} calls per {self.window_seconds}s")
        
        self.calls.append(now)
        return self.execute(*args, **kwargs)
    
    def execute(self, *args, **kwargs):
        # Actual implementation
        pass
```

## Advanced Patterns

### Stateful Tools

```python
class DatabaseConnection:
    def __init__(self, connection_string):
        self.conn = None
        self.connection_string = connection_string
    
    def connect(self) -> str:
        """Establish database connection."""
        self.conn = create_connection(self.connection_string)
        return "Connected to database"
    
    def query(
        self,
        sql: Annotated[str, "SQL query to execute"]
    ) -> list[dict]:
        """Execute query on connected database."""
        if not self.conn:
            raise Exception("Not connected. Call connect() first.")
        return self.conn.execute(sql).fetchall()
```

### Tool Dependencies

```python
def tool_a(param: Annotated[str, "Input"]) -> str:
    """First tool."""
    return f"Result from A: {param}"

def tool_b(
    input_from_a: Annotated[str, "Output from tool_a"]
) -> str:
    """Tool that uses output from tool_a."""
    return f"Result from B: {input_from_a}"

# Agent can chain them automatically
tools = [tool_a, tool_b]
```

## Troubleshooting

### Tool Not Being Called

- Check agent's instructions mention the capability
- Verify tool description is clear
- Test with direct question that requires the tool

### Tool Error Messages

- Ensure error returns structured format
- Include specific error type
- Suggest correction/retry approach

### Performance Issues

- Profile tool execution time
- Consider caching results
- Implement async patterns for I/O

---

*Related: MCP Tools, Agent Creation, Session Management*
