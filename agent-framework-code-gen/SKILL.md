# Microsoft Foundry Agent Framework Code Generation - Complete Knowledge Base

## Skill Overview

**Skill Name:** `microsoft-foundry-agent-framework-code-gen`

**Purpose:** Generate, create, scaffold, build, enhance, fix, or debug AI agent and workflow code for Microsoft Foundry using Microsoft Agent Framework SDK.

### Scope

#### ✅ Use This Skill For:
- Create Foundry agent code
- Build agent app for Foundry
- Scaffold agent project
- Generate agent code with Agent Framework
- Fix agent code
- Enhance existing agent
- Add tools to agent
- Make app agentic
- Multi-agent workflow for Foundry

#### ❌ Do NOT Use This Skill For:
- Manage Foundry resources
- RBAC (Role-Based Access Control)
- Quotas management

---

## Required Workflow (MANDATORY)

When this skill is activated, you MUST follow these steps in order:

### Step 1: Load Best Practices
- Review the latest SDK best practices, version pins, and coding patterns
- Apply all best practices to the code you generate

### Step 2: Execute with Microsoft Foundry Skill
- Use the `microsoft-foundry` skill → **create** sub-skill
- Also reference the `agentframework` reference under the **create** sub-skill folder
- This provides starter samples, project structure, and framework-specific patterns

### Step 3: Verify
- After code generation, verify the output follows the best practices from Step 1
- Check: SDK version pins, correct client usage, HTTP server pattern, debug support
- Use **Post-Handoff Verification Checklist** (see below)

---

## Mandatory Defaults (ALWAYS Apply)

**When the user does not specify a preference, these defaults are mandatory.**
**If user explicitly states a preference that conflicts, follow the user's preference.**

### Client Selection
- **Use `FoundryChatClient`** as the AI client
- **Do NOT use:**
  - `AzureAIClient`
  - `AzureOpenAIChatClient`
  - `AzureAIAgentClient`
  - Any other client unless explicitly requested

### Deployment Pattern
- **Use HTTP server pattern** via the hosting adapter (`from_agent_framework`)
- Ensures the agent is deployable as a web service
- **Do NOT generate console-only scripts** unless explicitly asked

### Debug Support
- **Add full debug support** including:
  - VS Code debug configurations for `agentdev` CLI
  - AI Toolkit Agent Inspector configurations
  - Detailed debug templates

---

## SDK Version Pinning

**CRITICAL:** The SDK is in preview with frequent breaking renames. **Always pin versions.**

### Python Requirements
- **Requires Python 3.10+**
- **IMPORTANT INSTALLATION ORDER:** Install agentserver and agent-dev-cli **first**, then agent-framework packages
  - `agentserver` pins `agent-framework-core<=rc3`
  - Installing `agent-framework` rc6 afterward overrides it
  - This order prevents dependency resolution conflicts

```bash
# Step 1: agentserver + agent-dev-cli (pulls in agent-framework-core==rc3)
pip install azure-ai-agentserver-agentframework==1.0.0b16 azure-ai-agentserver-core==1.0.0b16 agent-dev-cli==0.0.1b260316

# Step 2: agent-framework rc6 (overrides rc3)
pip install agent-framework-core==1.0.0rc6 agent-framework-foundry==1.0.0rc6 agent-framework-openai==1.0.0rc6
```

### .NET Requirements
```bash
dotnet add package Microsoft.Agents.AI.AzureAI --prerelease
dotnet add package Microsoft.Agents.AI.OpenAI --prerelease
dotnet add package Microsoft.Agents.AI.Workflows --prerelease
```

### Version-Specific Coding Patterns

The pinned version (`1.0.0rc6`) uses specific API names that differ from newer/older versions or online docs.

**Use these exact patterns:**

---

## Core Coding Patterns

### Pattern 1: Default Client Setup

**Use `FoundryChatClient` with sync `DefaultAzureCredential`:**

```python
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential  # sync version (not aio)

client = FoundryChatClient(
    project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
    model=os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME"),
    credential=DefaultAzureCredential(),
)
```

**Key Points:**
- Use sync `DefaultAzureCredential` from `azure.identity` (NOT async)
- Can reuse one client instance for different agents

### Pattern 2: Agent Creation

**Use `Agent(client,...)` with `async with` or `.as_agent()` method:**

```python
async with Agent(
    client=client,
    name="MyAgent",
    instructions="You are a helpful agent."
) as agent:
    result = await agent.run("hello")
```

**Alternative Method:**
```python
agent = client.as_agent(instructions="...", name="MyAgent")
```

**Key Points:**
- Use `Agent(client,...)` or `.as_agent()` (NOT `create_agent()`)
- Can reuse one client for different agents
- Agent names should follow: "start and end with alphanumeric characters, can contain hyphens in the middle, not exceed 63 characters"
- Good names: `SampleAgent`, `agent-1`, `myagent`
- Bad names: `-agent`, `agent-`, `sample_agent`

### Pattern 3: Workflow Builder

**Use `start_executor=...` parameter:**

```python
workflow = WorkflowBuilder(start_executor=...).add_edge(...).build()
```

**NOT:**
```python
# ❌ WRONG
workflow = WorkflowBuilder().set_start_executor(...).add_edge(...).build()
```

### Pattern 4: Streaming Responses (Production-Grade)

**Use `.run(..., stream=True)` and call `await stream.get_final_response()` at the end:**

```python
print("Agent: ", end="", flush=True)
stream = agent.run("hello", stream=True)
async for chunk in stream:
    if chunk.text:
        print(chunk.text, end="", flush=True)
print("\n")
await stream.get_final_response()  # CRITICAL: finalize the response
```

**NOT:**
```python
# ❌ WRONG
stream = agent.run_stream("hello")  # This method is deprecated
```

**For Testing:**
```python
result = await agent.run("hello")  # no streaming
print(f"Agent: {result.text}")
```

### Pattern 5: HTTP Server via Hosting Adapter

**Use `from_agent_framework` for web service deployment:**

```python
from azure.ai.agentserver.agentframework import from_agent_framework

await from_agent_framework(agent).run_async()
```

**Required Packages:**
- `azure-ai-agentserver-agentframework==1.0.0b16`
- `azure-ai-agentserver-core==1.0.0b16`

### Pattern 6: Workflow Handler Input

**Accept `list[Message]` for HTTP request handling:**

```python
@handler
async def some_handler(
    self, 
    messages: list[Message], 
    ctx: WorkflowContext[...]
) -> ...:
    # handler implementation
```

### Pattern 7: Environment Variables

**Use `load_dotenv(override=False)` to respect Foundry runtime environment:**

```python
from dotenv import load_dotenv

load_dotenv(override=False)  # Foundry runtime env vars take precedence
```

**NOT:**
```python
# ❌ WRONG
load_dotenv()  # uses defaults
load_dotenv(override=True)  # overrides Foundry runtime vars
```

### Pattern 8: Multi-Turn Conversation with Session

**Create and reuse session for context persistence:**

```python
async def multi_turn_conversation() -> None:
    client = FoundryChatClient(
        project_endpoint="<your-foundry-project-endpoint>",
        model="<your-foundry-model-deployment>",
        credential=DefaultAzureCredential(),
    )
    async with Agent(
        client,
        name="MyAgent",
        instructions="You are a helpful agent.",
    ) as agent:
        # Create a new session
        session = agent.create_session()

        # First conversation
        print("Agent: ", end="", flush=True)
        stream = agent.run("What's the weather like in Seattle?", session=session, stream=True)
        async for chunk in stream:
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")
        await stream.get_final_response()  # finalize to persist history

        # Second conversation using same session - maintains context
        print("Agent: ", end="", flush=True)
        stream = agent.run("Pardon?", session=session, stream=True)
        async for chunk in stream:
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")
        await stream.get_final_response()
```

**Key Points:**
- Default uses in-memory store
- For persistent stores, search agent-framework source repo for more samples
- Session persists conversation history

### Pattern 9: Add Tools to Agent

**Define function and add to agent `tools` parameter:**

```python
from typing import Annotated

def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."

async def agent_with_tools() -> None:
    client = FoundryChatClient(
        project_endpoint="<your-foundry-project-endpoint>",
        model="<your-foundry-model-deployment>",
        credential=DefaultAzureCredential(),
    )
    async with Agent(
        client,
        name="MyAgent",
        instructions="You are a helpful agent.",
        tools=[get_weather],  # add tools here
    ) as agent:
        stream = agent.run("What's the weather like in Seattle?", stream=True)
        async for chunk in stream:
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")
        await stream.get_final_response()
```

### Pattern 10: Model Context Protocol (MCP) Tools

**Connect with MCP tools for enhanced capabilities:**

```python
from agent_framework import MCPStdioTool, ToolTypes, MCPStreamableHTTPTool
from typing import Any

def create_mcp_tools() -> list[ToolTypes | Any]:
    return [
        # stdio sample - Playwright
        MCPStdioTool(
            name="Playwright MCP",
            description="provides browser automation capabilities using Playwright",
            command="npx",
            args=["-y", "@playwright/mcp@latest"],
            load_prompts=False  # False if using tools only
        ),
        # streamable http sample - Microsoft Learn
        MCPStreamableHTTPTool(
            name="Microsoft Learn MCP",
            description="bring trusted and up-to-date information directly from Microsoft's official documentation",
            url="https://learn.microsoft.com/api/mcp",
            load_prompts=False  # False if using tools only
        )
    ]

async def agent_with_mcp() -> None:
    client = FoundryChatClient(
        project_endpoint="<your-foundry-project-endpoint>",
        model="<your-foundry-model-deployment>",
        credential=DefaultAzureCredential(),
    )
    async with Agent(
        client,
        name="MyAgent",
        instructions="You are a helpful agent.",
        tools=create_mcp_tools(),  # use MCP tools
    ) as agent:
        session = agent.create_session()
        
        stream = agent.run(USER_INPUTS, session=session, stream=True)
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
        print("")
        await stream.get_final_response()
```

**Key Points:**
- For tools only (without prompts), set `load_prompts=False`
- Default is `load_prompts=True`
- Supports both stdio-based and HTTP-based MCP tools

---

## Existing Agent Enhancement Tips

When enhancing existing agents (update, fix, add feature) built with Microsoft Agent Framework:

### Respect Existing Types
- Keep existing `*Client`, `*Credential`, etc. patterns
- No migration unless explicitly requested by user

### Respect Existing Environment
- Detect and use existing Python environment
- Never override unless explicitly requested

### Leverage Existing Patterns
- Respect existing patterns and conventions

---

## Post-Handoff Verification Checklist

**After the create sub-skill finishes, review generated files and fix mismatches against the pinned SDK patterns above.**

**Skip for brownfield enhancements or when user requested a different framework.**

| Check | Pattern | Wrong → Fix |
|-------|---------|------------|
| **Client** | FoundryChatClient | `AzureAIClient` / `AzureOpenAIChatClient` / `AzureAIAgentClient` → `FoundryChatClient` |
| **Credential** | Sync DefaultAzureCredential | Async credential → Use sync `from azure.identity import DefaultAzureCredential` |
| **Agent Creation** | Agent(client,...) or .as_agent() | `create_agent()` → Use `Agent(client,...)` with `async with` |
| **WorkflowBuilder** | WorkflowBuilder(start_executor=X) | `.set_start_executor(X)` → `WorkflowBuilder(start_executor=X)` |
| **Streaming** | .run(input, stream=True) | `.run_stream(input)` → `.run(input, stream=True)` |
| **Stream Finalization** | await stream.get_final_response() | Missing finalization → Add `await stream.get_final_response()` |
| **load_dotenv** | load_dotenv(override=False) | `load_dotenv()` or `override=True` → `load_dotenv(override=False)` |
| **Versions** | Pinned rc6 & b16 | Wrong version → Pin `agent-framework-core/foundry/openai==1.0.0rc6`, `azure-ai-agentserver-*==1.0.0b16` |
| **Install Order** | agentserver first, then agent-framework | Wrong order → Install agentserver + agent-dev-cli first, then agent-framework rc6 |
| **Hosting** | from_agent_framework(agent).run_async() | Missing HTTP server → Verify `from_agent_framework(agent).run_async()` entry point |
| **Environment Variables** | Fill in Foundry-related vars | Missing .env vars → If `.env`/`.env.template` used, fill in Foundry variables |
| **Debugging** | .vscode/launch.json & tasks.json | Missing debug configs → Verify VS Code launch configurations for `agentdev` CLI and Agent Inspector |
| **Agent Name** | Alphanumeric start/end, hyphens OK | Invalid naming → Use patterns like: `SampleAgent`, `agent-1`, `myagent` |
| **Tools** | Defined with Annotated types | Wrong tool pattern → Define tools with proper type annotations |
| **MCP Tools** | load_prompts=False for tools only | Missing setting → Set `load_prompts=False` on MCP tools if using tools only |

---

## Important Implementation Tips

### Stability & Common Errors Prevention

- **Client option:** Use `FoundryChatClient` (recommended) to connect Foundry model using project endpoint and model deployment name, with full agent management in code
- **Credential:** Use sync credential from `azure.identity` (NOT async)
- **Agent instance:** Can be created via either `Agent(...)` constructor or `client.as_agent(...)` method
- **Deployment-ready naming:** Fit agent name to "start and end with alphanumeric characters, can contain hyphens in the middle, and not exceed 63 characters"
- **MCP tools:** When using MCP tools for tools only (without prompts), explicitly set `load_prompts=False`
- **Default:** `load_prompts=True` if not specified

---

## Summary: Quick Reference

| Item | Pattern |
|------|---------|
| **Client** | `FoundryChatClient` with sync `DefaultAzureCredential` |
| **Agent** | `async with Agent(client, name=..., instructions=...)` |
| **Tools** | Pass `tools=[func1, func2]` to Agent constructor |
| **Streaming** | `stream = agent.run(input, stream=True)` + `await stream.get_final_response()` |
| **Session** | `session = agent.create_session()` then `agent.run(..., session=session)` |
| **HTTP Server** | `from_agent_framework(agent).run_async()` |
| **Workflow** | `WorkflowBuilder(start_executor=...).add_edge(...).build()` |
| **Environment** | `load_dotenv(override=False)` |
| **Python Version** | 3.10+ required |
| **Key Versions** | `agent-framework-core==1.0.0rc6`, `azure-ai-agentserver-*==1.0.0b16` |

---

## Workflow Decision Tree

```
User Request
├─ Create/Build/Scaffold agent code?
│  ├─ YES → Execute Required Workflow (Steps 1-3)
│  │        └─ Step 1: Load Best Practices
│  │        └─ Step 2: Use microsoft-foundry skill → create
│  │        └─ Step 3: Verify against Post-Handoff Checklist
│  └─ NO → Continue below
│
├─ Enhance/Fix/Add feature to existing agent?
│  ├─ YES → Respect existing patterns & types
│  │        └─ Use Additional Tools for context
│  │        └─ Verify against Post-Handoff Checklist
│  └─ NO → Continue below
│
└─ Deploy/RBAC/Quotas/Other Foundry operations?
   └─ Use microsoft-foundry skill directly (not this skill)
```

---

## Related Skills

- **microsoft-foundry skill** → For deployment, resource management, RBAC, quotas

---

*Last Updated: April 2026*
*Based on Microsoft Agent Framework SDK pinned version 1.0.0rc6*
