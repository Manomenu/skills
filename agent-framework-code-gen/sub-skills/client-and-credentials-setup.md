# Client and Credentials Setup

## Overview

Proper client and credential setup is the foundation of any Microsoft Agent Framework application. This skill covers establishing the connection to Microsoft Foundry models with correct authentication.

## Mandatory Client: FoundryChatClient

### Why FoundryChatClient?

The `FoundryChatClient` is the only recommended client for agent development with Microsoft Agent Framework. It provides:

- Direct connection to Microsoft Foundry project endpoints
- Model deployment management
- Full agent management capabilities in code
- Proper credential handling

### Deprecated Clients (Do NOT Use)

- `AzureAIClient` - Legacy, do not use
- `AzureOpenAIChatClient` - Legacy, do not use
- `AzureAIAgentClient` - Legacy, do not use
- Any other custom clients unless explicitly requested

## Credential Setup

### Mandatory: Sync DefaultAzureCredential

**Always use sync version from `azure.identity`:**

```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
```

### NOT Async

- **Do NOT use `AsyncDefaultAzureCredential`** - Must use synchronous version
- Agent Framework handles async/await at a higher level
- Mixing async credentials causes runtime errors

### Why Sync?

The Agent Framework SDK is designed to work with sync credentials for client initialization. The async context is managed internally by the framework during agent execution.

## Client Initialization

### Complete Setup Pattern

```python
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential
import os

# Initialize credential
credential = DefaultAzureCredential()

# Create client
client = FoundryChatClient(
    project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
    model=os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME"),
    credential=credential,
)
```

### Required Environment Variables

- `FOUNDRY_PROJECT_ENDPOINT` - Your Foundry project endpoint URL
- `FOUNDRY_MODEL_DEPLOYMENT_NAME` - Name of your model deployment

## Client Reusability

### One Client, Multiple Agents

**Key benefit:** A single `FoundryChatClient` instance can be reused across multiple agents:

```python
# Client created once
client = FoundryChatClient(
    project_endpoint="...",
    model="...",
    credential=credential,
)

# Reuse for different agents
agent1 = Agent(client, name="Agent1", instructions="...")
agent2 = Agent(client, name="Agent2", instructions="...")

# Both agents can be used independently
```

This pattern:
- Reduces authentication overhead
- Improves performance
- Simplifies connection management

## Best Practices

1. **Initialize early** - Create client once at application startup
2. **Use environment variables** - Never hardcode credentials or endpoints
3. **Reuse instances** - One client can serve multiple agents
4. **Keep credential lifecycle simple** - DefaultAzureCredential handles token refresh automatically
5. **Error handling** - Wrap client creation in try-catch for initialization errors

## Troubleshooting

### Authentication Errors

- Verify `DefaultAzureCredential` has permission (managed identity, service principal, or user account)
- Check `FOUNDRY_PROJECT_ENDPOINT` is correct format
- Ensure RBAC permissions exist in Foundry

### Endpoint Format

Endpoints should follow: `https://{region}.foundry.microsoft.com/projects/{project-id}`

### Model Deployment Name

- Must exactly match deployed model name in your Foundry project
- Case-sensitive
- Verify in Foundry portal

---

*Related: Agent Creation, SDK Version Pinning, Deployment Patterns*
