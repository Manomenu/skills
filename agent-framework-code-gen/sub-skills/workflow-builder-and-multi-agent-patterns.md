# Workflow Builder and Multi-Agent Patterns

## Overview

WorkflowBuilder enables orchestration of multiple agents and complex task flows. This skill covers building workflows, managing multiple agents, and designing agentic systems.

## What is a Workflow?

**Workflow** = Orchestrated execution of tasks/agents

A workflow:
- Chains multiple agents together
- Routes tasks to appropriate agents
- Manages information flow
- Handles conditional logic
- Enables parallel execution

## WorkflowBuilder Basics

### Core Pattern (CRITICAL)

```python
from agent_framework import WorkflowBuilder

workflow = WorkflowBuilder(start_executor=initial_handler).add_edge(...).build()
```

### Deprecated Pattern (DO NOT USE)

```python
# ❌ WRONG
workflow = WorkflowBuilder().set_start_executor(...).add_edge(...).build()

# ✅ CORRECT
workflow = WorkflowBuilder(start_executor=...).add_edge(...).build()
```

The `start_executor` parameter must be passed in the constructor, not set with a method.

## Creating Handlers

### Handler Definition

```python
from agent_framework import handler
from agent_framework.models import Message
from agent_framework.workflow import WorkflowContext

@handler
async def initial_handler(
    self,
    messages: list[Message],
    ctx: WorkflowContext[...]
) -> str:
    """First handler in workflow."""
    # Process messages
    response = "Processing input..."
    return response
```

### Handler Signature

- `@handler` decorator marks function as workflow handler
- `messages: list[Message]` - Incoming messages
- `ctx: WorkflowContext` - Workflow context for state management
- **Return type** - String or structured output
- **async** - All handlers are async

## Simple Workflow Example

### Two-Handler Workflow

```python
from agent_framework import WorkflowBuilder, handler
from agent_framework.models import Message
from agent_framework.workflow import WorkflowContext

@handler
async def handler1(self, messages: list[Message], ctx: WorkflowContext) -> str:
    """First handler - validate input."""
    user_input = messages[-1].content if messages else ""
    if not user_input:
        return "No input provided"
    return f"Validated: {user_input}"

@handler
async def handler2(self, messages: list[Message], ctx: WorkflowContext) -> str:
    """Second handler - process."""
    context = ctx.state.get("result", "")
    return f"Processing: {context}"

# Build workflow
workflow = (
    WorkflowBuilder(start_executor=handler1)
    .add_edge(handler1, handler2)
    .add_edge(handler2, "end")
    .build()
)
```

## Multi-Agent Workflow

### Routing Between Agents

```python
class MultiAgentWorkflow:
    def __init__(self, client):
        self.client = client
        self.weather_agent = Agent(
            client=client,
            name="WeatherAgent",
            instructions="Provide weather information",
            tools=[get_weather]
        )
        self.calendar_agent = Agent(
            client=client,
            name="CalendarAgent",
            instructions="Manage calendar events"
        )
    
    async def classify_and_route(
        self,
        user_input: str
    ) -> str:
        """Route request to appropriate agent."""
        if "weather" in user_input.lower():
            result = await self.weather_agent.run(user_input)
            return f"Weather: {result.text}"
        elif "calendar" in user_input.lower() or "meeting" in user_input.lower():
            result = await self.calendar_agent.run(user_input)
            return f"Calendar: {result.text}"
        else:
            return "Request type not recognized"
```

## Workflow Execution

### Running Workflows

```python
async def run_workflow():
    # Create workflow
    workflow = WorkflowBuilder(start_executor=handler1).build()
    
    # Prepare input
    input_messages = [Message(role="user", content="What's 2+2?")]
    
    # Execute
    result = await workflow.run(input_messages)
    print(f"Result: {result}")
```

### Workflow with Session

```python
# Create persistent session
session = workflow.create_session()

# Multiple workflow executions
result1 = await workflow.run(messages1, session=session)
result2 = await workflow.run(messages2, session=session)

# Workflow maintains context
```

## Workflow Context Management

### Storing State

```python
@handler
async def stateful_handler(
    self,
    messages: list[Message],
    ctx: WorkflowContext
) -> str:
    # Read state
    previous_result = ctx.state.get("result", None)
    
    # Process
    new_result = process(messages)
    
    # Store state
    ctx.state["result"] = new_result
    
    return new_result
```

### State Types

```python
ctx.state = {
    "user_id": "user123",
    "conversation_id": "conv456",
    "results": [...],
    "metadata": {...}
}
```

## Conditional Logic in Workflows

### Branching Based on Input

```python
@handler
async def decision_handler(
    self,
    messages: list[Message],
    ctx: WorkflowContext
) -> str:
    user_input = messages[-1].content
    
    if "urgent" in user_input.lower():
        return "ROUTE_TO_PRIORITY"
    elif "complex" in user_input.lower():
        return "ROUTE_TO_EXPERT"
    else:
        return "ROUTE_TO_STANDARD"
```

### Dynamic Routing

```python
workflow = (
    WorkflowBuilder(start_executor=decision_handler)
    .add_edge(
        decision_handler,
        {
            "ROUTE_TO_PRIORITY": priority_handler,
            "ROUTE_TO_EXPERT": expert_handler,
            "ROUTE_TO_STANDARD": standard_handler
        }
    )
    .add_edge(priority_handler, "end")
    .add_edge(expert_handler, "end")
    .add_edge(standard_handler, "end")
    .build()
)
```

## Error Handling in Workflows

### Try-Catch Pattern

```python
@handler
async def safe_handler(
    self,
    messages: list[Message],
    ctx: WorkflowContext
) -> str:
    try:
        result = await risky_operation(messages)
        return result
    except Exception as e:
        ctx.state["error"] = str(e)
        return f"Error occurred: {e}"
```

## Complex Workflow Pattern

### Full Example: Request Processing Pipeline

```python
class RequestProcessingWorkflow:
    def __init__(self, client):
        self.client = client
        self.validator_agent = Agent(client, name="Validator", instructions="Validate requests")
        self.processor_agent = Agent(client, name="Processor", instructions="Process requests")
        self.formatter_agent = Agent(client, name="Formatter", instructions="Format responses")
    
    @handler
    async def validate_handler(
        self,
        messages: list[Message],
        ctx: WorkflowContext
    ) -> str:
        """Step 1: Validate input."""
        user_input = messages[-1].content if messages else ""
        if not user_input or len(user_input) < 3:
            return "INVALID"
        ctx.state["raw_input"] = user_input
        return "VALID"
    
    @handler
    async def process_handler(
        self,
        messages: list[Message],
        ctx: WorkflowContext
    ) -> str:
        """Step 2: Process validated input."""
        raw_input = ctx.state.get("raw_input", "")
        result = await self.processor_agent.run(raw_input)
        ctx.state["processed"] = result.text
        return result.text
    
    @handler
    async def format_handler(
        self,
        messages: list[Message],
        ctx: WorkflowContext
    ) -> str:
        """Step 3: Format output."""
        processed = ctx.state.get("processed", "")
        result = await self.formatter_agent.run(f"Format this: {processed}")
        return result.text
    
    def build_workflow(self):
        return (
            WorkflowBuilder(start_executor=self.validate_handler)
            .add_edge(self.validate_handler, {
                "VALID": self.process_handler,
                "INVALID": "end"
            })
            .add_edge(self.process_handler, self.format_handler)
            .add_edge(self.format_handler, "end")
            .build()
        )
```

## Workflow Testing

### Unit Test Workflow

```python
async def test_workflow():
    workflow = WorkflowBuilder(start_executor=test_handler).build()
    
    messages = [Message(role="user", content="test input")]
    result = await workflow.run(messages)
    
    assert "expected output" in result
```

## Best Practices

1. **Use start_executor parameter** - Not `.set_start_executor()` method
2. **Clear handler responsibilities** - Each handler does one thing
3. **Store state in context** - Don't use global variables
4. **Handle errors gracefully** - Try/catch in handlers
5. **Log transitions** - Track workflow progress
6. **Test individual handlers** - Unit test before integration
7. **Document flow** - Comment complex routing logic
8. **Use meaningful names** - Reflect handler purpose

## Common Patterns

### Sequential Processing

```
Input → Validate → Process → Format → Output
```

### Parallel Processing

```
Input → (Agent A, Agent B in parallel) → Merge → Output
```

### Conditional Routing

```
Input → Classify → Route to Agent A/B/C based on classification → Output
```

### Feedback Loop

```
Input → Process → Validate → If invalid: loop to Process → Output
```

## Performance Considerations

### Sequential vs Parallel

**Sequential:** Handlers execute one after another
- Simpler logic
- Slower for independent operations

**Parallel:** Multiple paths/agents execute simultaneously
- Complex coordination
- Better for independent tasks

### Scaling Workflows

- Monitor handler execution times
- Profile bottlenecks
- Consider parallel routes
- Cache intermediate results

---

*Related: Agent Creation, Tool Integration, HTTP Server Deployment*
