# Model Context Protocol (MCP) Tools

## Overview

Model Context Protocol (MCP) enables agents to connect with complex tool ecosystems. MCP tools provide standardized interfaces for browser automation, documentation access, and other capabilities. This skill covers integrating MCP tools with agents.

## What is MCP?

**MCP (Model Context Protocol)** is a standard interface that:
- Defines how tools expose capabilities
- Allows agents to discover tool functions
- Provides consistent error handling
- Supports both prompts and tools

## MCP Tool Types

### Type 1: Stdio-Based Tools

**Definition:** Tools that run as separate processes communicating via stdio

**Example: Playwright (Browser Automation)**

```python
from agent_framework import MCPStdioTool

MCPStdioTool(
    name="Playwright MCP",
    description="provides browser automation capabilities using Playwright",
    command="npx",
    args=["-y", "@playwright/mcp@latest"],
    load_prompts=False  # Tools only, no prompts
)
```

**Use When:**
- Tool is distributed as npm package
- Tool runs as independent process
- Tool is language-specific (Node.js, Python, Ruby, etc.)

### Type 2: HTTP-Based Tools

**Definition:** Tools exposed via HTTP API endpoints

**Example: Microsoft Learn Documentation**

```python
from agent_framework import MCPStreamableHTTPTool

MCPStreamableHTTPTool(
    name="Microsoft Learn MCP",
    description="bring trusted and up-to-date information directly from Microsoft's official documentation",
    url="https://learn.microsoft.com/api/mcp",
    load_prompts=False  # Tools only, no prompts
)
```

**Use When:**
- Tool provides HTTP API
- Tool is hosted service
- Tool supports streaming responses

## The load_prompts Parameter

### Critical: load_prompts Setting

```python
# If MCP tool provides BOTH tools and prompts
MCPStdioTool(
    name="...",
    command="...",
    args=[...],
    load_prompts=True  # Include tool prompts from MCP
)

# If MCP tool provides ONLY tools (no prompts)
MCPStdioTool(
    name="...",
    command="...",
    args=[...],
    load_prompts=False  # Don't load non-existent prompts
)
```

### Default Behavior

- **Default:** `load_prompts=True`
- **When to override:** When tool has no prompts, set to `False`
- **Why it matters:** Setting to `True` when tool has no prompts causes errors
- **When to use `True`:** Tool explicitly provides custom prompts (rare)

### Tool-Only Pattern (Most Common)

Most tools only provide tool functions, not prompts:

```python
def create_mcp_tools():
    return [
        MCPStdioTool(
            name="Playwright MCP",
            description="Browser automation",
            command="npx",
            args=["-y", "@playwright/mcp@latest"],
            load_prompts=False  # ✅ Correct for tools-only
        ),
        MCPStreamableHTTPTool(
            name="Microsoft Learn MCP",
            description="Microsoft documentation",
            url="https://learn.microsoft.com/api/mcp",
            load_prompts=False  # ✅ Correct for tools-only
        )
    ]
```

## Agent Integration

### Register MCP Tools with Agent

```python
async def agent_with_mcp() -> None:
    client = FoundryChatClient(
        project_endpoint="...",
        model="...",
        credential=DefaultAzureCredential(),
    )
    
    mcp_tools = create_mcp_tools()
    
    async with Agent(
        client=client,
        name="MyAgent",
        instructions="You are a helpful agent with browser and documentation access.",
        tools=mcp_tools,  # Register MCP tools
    ) as agent:
        session = agent.create_session()
        
        stream = agent.run(
            "Can you check the latest Python documentation?",
            session=session,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.text:
                print(chunk.text, end="", flush=True)
        
        await stream.get_final_response()
```

## Streaming Events from MCP Tools

### Handling Tool Execution Events

```python
async def agent_with_mcp_events() -> None:
    # ... client and agent setup ...
    
    stream = agent.run(query, session=session, stream=True)
    
    async for chunk in stream:
        # Process text responses
        if chunk.text:
            print(chunk.text, end="", flush=True)
        
        # Process tool execution events
        elif chunk.raw_representation and chunk.raw_representation.raw_representation:
            event = chunk.raw_representation.raw_representation
            
            if (hasattr(event, 'type') 
                and event.type == 'response.output_item.done' 
                and hasattr(event, 'item') 
                and hasattr(event.item, 'name')):
                
                tool_name = event.item.name
                args = getattr(event.item, 'arguments', None)
                status = getattr(event.item, 'status', None)
                
                print(f"\n[Tool: {tool_name}] args={args} status={status}")
    
    print("")
    await stream.get_final_response()
```

### Event Structure

Each event contains:
- `type` - Event type (e.g., 'response.output_item.done')
- `item.name` - Tool name that was executed
- `item.arguments` - Arguments passed to tool
- `item.status` - Execution status ('success', 'error', etc.)

## Common MCP Tools

### Playwright (Browser Automation)

```python
MCPStdioTool(
    name="Playwright MCP",
    description="Browser automation for web scraping, testing, and interaction",
    command="npx",
    args=["-y", "@playwright/mcp@latest"],
    load_prompts=False
)
```

**Capabilities:**
- Navigate to URLs
- Extract page content
- Fill forms
- Click buttons
- Take screenshots

### Microsoft Learn (Documentation)

```python
MCPStreamableHTTPTool(
    name="Microsoft Learn MCP",
    description="Access Microsoft's official documentation and learning resources",
    url="https://learn.microsoft.com/api/mcp",
    load_prompts=False
)
```

**Capabilities:**
- Search documentation
- Get API reference
- Find tutorials
- Access learning paths

### Other Available Tools

Ecosystem includes:
- Data processing tools
- File system access
- API integrations
- Database connections
- Cloud service tools

## Combining Custom and MCP Tools

### Mixed Tool Strategy

```python
# Custom tools
def get_weather(location: Annotated[str, "City name"]) -> str:
    """Get weather for location."""
    return f"Sunny in {location}"

# MCP tools
mcp_tools = [
    MCPStdioTool(
        name="Playwright MCP",
        description="Browser automation",
        command="npx",
        args=["-y", "@playwright/mcp@latest"],
        load_prompts=False
    )
]

# Combine them
all_tools = [get_weather] + mcp_tools

async with Agent(
    client=client,
    name="MyAgent",
    instructions="...",
    tools=all_tools,  # Custom + MCP
) as agent:
    # Agent can use both
    result = await agent.run("Use browser to find weather forecast")
```

## Error Handling with MCP Tools

### Tool Initialization Errors

```python
try:
    tool = MCPStdioTool(
        name="MyTool",
        command="npx",
        args=["-y", "@some/tool@latest"],
        load_prompts=False
    )
except Exception as e:
    print(f"Failed to initialize tool: {e}")
    # May indicate tool not installed
```

### Tool Execution Errors

When MCP tool fails:
- Error is captured in event
- Agent receives failure status
- Can retry with different approach
- User informed of limitation

## Performance & Resource Management

### Tool Startup

- First call to tool may be slow (process/connection startup)
- Subsequent calls are faster
- Consider warm-up for critical tools

### Memory Usage

- Stdio tools run as separate processes
- Each has independent memory footprint
- HTTP tools shared connection

### Timeouts

- Tools may timeout on slow operations
- Agent handles gracefully
- Consider tool complexity in instructions

## Best Practices

1. **Set load_prompts=False** for tools-only implementations
2. **Use descriptive names** for tool identification
3. **Include detailed descriptions** for agent understanding
4. **Handle tool errors gracefully** - don't assume success
5. **Monitor event streams** for tool execution debugging
6. **Combine strategically** - Mix custom and MCP tools
7. **Test tools independently** before agent integration
8. **Document tool capabilities** in agent instructions

## Troubleshooting

### Tool Not Available

- Verify tool executable/URL is accessible
- Check command syntax is correct
- Ensure environment can reach tool

### Tool Execution Failed

- Check tool error events for details
- Verify tool arguments are correct
- Test tool manually before debugging agent

### load_prompts=True Causing Errors

- Change to `load_prompts=False`
- Tool doesn't provide prompts
- This is the correct default for most tools

---

*Related: Tool Integration, Custom Tools, Agent Creation*
