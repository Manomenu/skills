# Verification and Quality Checks

## Overview

This skill provides a comprehensive verification checklist to ensure agent code follows Microsoft Agent Framework best practices and pinned SDK patterns. Use this checklist after code generation, enhancements, or before deployment.

## When to Use This Checklist

✅ **Use after:**
- Generating new agent code
- Enhancing existing agents
- Major refactoring
- Before deployment
- When migrating versions

❌ **Skip for:**
- Brownfield enhancements (minor fixes)
- When user explicitly requested different patterns
- Non-agent code

## Pre-Implementation Verification

### Project Setup Checks

Before writing code, verify:

- [ ] Python 3.10+ (or .NET 8.0+) available
- [ ] Virtual environment created
- [ ] SDK dependencies installed in correct order
- [ ] Environment variables defined (.env file)
- [ ] Azure credentials configured
- [ ] Foundry project endpoint accessible
- [ ] Model deployment name verified in Foundry portal

## SDK Patterns Verification Checklist

### Client Pattern

| Item | Expected | Action if Wrong |
|------|----------|-----------------|
| **Client Type** | `FoundryChatClient` | Replace `AzureAIClient` / `AzureOpenAIChatClient` / `AzureAIAgentClient` |
| **Credential Type** | Sync `DefaultAzureCredential` | Change from async to `from azure.identity import DefaultAzureCredential` |
| **Credential Location** | `from azure.identity` | Update import path |
| **Client Parameters** | `project_endpoint`, `model`, `credential` | Add missing parameters |
| **Client Reuse** | Same instance for multiple agents | Refactor to share client |

### Agent Creation Pattern

| Item | Expected | Action if Wrong |
|------|----------|-----------------|
| **Creation Method** | `Agent(client,...)` or `.as_agent()` | Remove `create_agent()` calls |
| **Context Manager** | `async with Agent(...)` | Add context manager or explicit cleanup |
| **Agent Parameters** | `client`, `name`, `instructions` | Ensure all required params present |
| **Agent Name** | Alphanumeric start/end, hyphens OK | Fix invalid characters/format |
| **Name Length** | ≤ 63 characters | Shorten if too long |
| **Invalid Names** | No: `-agent`, `agent-`, `sample_agent` | Use patterns: `MyAgent`, `agent-1` |

### Workflow Pattern

| Item | Expected | Action if Wrong |
|------|----------|-----------------|
| **Constructor Parameter** | `WorkflowBuilder(start_executor=...)` | Change `.set_start_executor(...)` to constructor param |
| **Method Chain** | `.add_edge(...).build()` | Ensure proper method sequence |
| **Handler Signature** | `async def handler(self, messages: list[Message], ctx: WorkflowContext)` | Fix parameter types and async |
| **@handler Decorator** | Present on handlers | Add decorator if missing |

### Streaming Pattern

| Item | Expected | Action if Wrong |
|------|----------|-----------------|
| **Streaming Call** | `.run(input, stream=True)` | Change from `.run_stream(input)` |
| **Chunk Processing** | `if chunk.text:` before printing | Add text check |
| **Finalization** | `await stream.get_final_response()` | Add after streaming loop |
| **Finalization Location** | After loop, before next operation | Move to correct location |
| **Finalization Type** | `async` (awaited) | Add `await` keyword |

### Tools Pattern

| Item | Expected | Action if Wrong |
|------|----------|-----------------|
| **Tool Parameters** | `Annotated[type, "description"]` | Add type annotations with descriptions |
| **Tool Docstring** | Present and clear | Add/improve docstring |
| **Tool Registration** | `tools=[tool1, tool2]` in Agent | Register all tools |
| **Return Type** | Explicitly declared | Add return type annotation |
| **Error Handling** | Structured error returns | Implement error responses |

### MCP Tools Pattern

| Item | Expected | Action if Wrong |
|------|----------|-----------------|
| **load_prompts Parameter** | `load_prompts=False` (for tools-only) | Change from `True` if tool has no prompts |
| **Tool Type** | `MCPStdioTool` or `MCPStreamableHTTPTool` | Use correct MCP tool type |
| **Tool Registration** | In `tools=` list of Agent | Add to tools list |
| **Event Processing** | Check `event.type` before accessing | Add proper event checks |

### Environment Variables Pattern

| Item | Expected | Action if Wrong |
|------|----------|-----------------|
| **load_dotenv Call** | `load_dotenv(override=False)` | Change from `override=True` |
| **Env Var Names** | `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL_DEPLOYMENT_NAME` | Use correct names |
| **Env Var Definition** | In `.env` or deployment config | Add missing variables |
| **Sensitive Data** | Not hardcoded | Move to environment |

### Deployment Pattern

| Item | Expected | Action if Wrong |
|------|----------|-----------------|
| **HTTP Server** | `from_agent_framework(agent).run_async()` | Add hosting adapter |
| **Import** | `from azure.ai.agentserver.agentframework import from_agent_framework` | Fix import path |
| **Async Context** | Inside `async def main()` or `async with Agent(...)` | Ensure async context |
| **Server Startup** | `await` before `run_async()` | Add await keyword |

### Debugging Configuration

| Item | Expected | Action if Wrong |
|------|----------|-----------------|
| **launch.json** | Present with `agentdev` configs | Add from `aitk-add_agent_debug` |
| **tasks.json** | Present with agent tasks | Add from `aitk-add_agent_debug` |
| **Debug Breakpoints** | Possible to set | Verify debugging setup |

## Version Verification Checklist

### Installed Versions

```bash
pip show agent-framework-core
# Should show: Version: 1.0.0rc6

pip show azure-ai-agentserver-agentframework  
# Should show: Version: 1.0.0b16

pip show agent-dev-cli
# Should show: Version: 0.0.1b260316
```

### requirements.txt Check

- [ ] `agent-framework-core==1.0.0rc6` (exact pin)
- [ ] `agent-framework-foundry==1.0.0rc6` (exact pin)
- [ ] `agent-framework-openai==1.0.0rc6` (exact pin)
- [ ] `azure-ai-agentserver-agentframework==1.0.0b16` (exact pin)
- [ ] `azure-ai-agentserver-core==1.0.0b16` (exact pin)
- [ ] `agent-dev-cli==0.0.1b260316` (exact pin)
- [ ] No floating versions (`>=`, `~=`, etc.)

### Installation Order Verification

- [ ] agentserver packages installed first
- [ ] agent-dev-cli installed first  
- [ ] agent-framework packages installed after Step 1
- [ ] No version conflicts reported

## Functional Testing Checklist

### Basic Functionality

- [ ] Agent initializes without errors
- [ ] Agent responds to simple queries
- [ ] Agent completes in reasonable time (< 30s)
- [ ] Streaming works (if used)
- [ ] Session persistence works (if used)

### Tool Testing

- [ ] Tools are called when appropriate
- [ ] Tool parameters passed correctly
- [ ] Tool errors handled gracefully
- [ ] Agent uses tool results correctly

### Multi-Turn Testing

- [ ] Session maintains context across turns
- [ ] Agent remembers previous inputs
- [ ] Agent applies context to new queries

### Error Handling

- [ ] Invalid input handled gracefully
- [ ] Auth errors reported clearly
- [ ] Timeout errors handled
- [ ] Network errors handled

## Security Verification Checklist

### Credentials

- [ ] No hardcoded credentials in code
- [ ] Credentials loaded from environment
- [ ] `.env` file not committed to git
- [ ] `.gitignore` includes sensitive files

### Data Handling

- [ ] No PII logged unnecessarily
- [ ] Sensitive data marked confidential
- [ ] Request/response logging secure
- [ ] Session data properly protected

### Access Control

- [ ] RBAC permissions verified in Foundry
- [ ] Service principal has minimal required perms
- [ ] Credentials scoped appropriately
- [ ] No overly permissive credentials

## Performance Verification Checklist

### Response Time

- [ ] Simple queries < 3 seconds
- [ ] Complex queries < 10 seconds
- [ ] Streaming responds immediately
- [ ] Tool calls complete reasonably

### Resource Usage

- [ ] Memory doesn't grow unbounded
- [ ] No connection leaks
- [ ] Concurrent requests handled
- [ ] Graceful degradation under load

### Scalability

- [ ] Multiple agents don't conflict
- [ ] Client instances properly shared
- [ ] Session management scalable
- [ ] Database queries optimized (if applicable)

## Code Quality Checklist

### Style

- [ ] Consistent naming conventions
- [ ] Proper type hints
- [ ] Clear docstrings
- [ ] No TODO comments left

### Documentation

- [ ] Instructions clear for agent behavior
- [ ] Tool descriptions accurate
- [ ] Comments explain complex logic
- [ ] README includes setup steps

### Testing

- [ ] Unit tests for custom tools
- [ ] Integration tests for workflows
- [ ] Error cases tested
- [ ] Edge cases covered

## Pre-Deployment Checklist

### Final Verification

- [ ] All checklist items passed
- [ ] Code reviewed for patterns
- [ ] Tests passing
- [ ] No console errors
- [ ] Environment variables set correctly
- [ ] Credentials valid and non-expired
- [ ] Deployment target ready
- [ ] Rollback plan documented

### Deployment Steps

1. [ ] Code committed to repository
2. [ ] Dependencies installed fresh
3. [ ] All tests passing
4. [ ] Manual smoke test in dev
5. [ ] Deploy to staging
6. [ ] Staging validation complete
7. [ ] Deploy to production
8. [ ] Monitor initial requests
9. [ ] Health checks passing
10. [ ] Rollback plan ready

## Quick Reference: Common Issues

### Issue: Agent won't initialize

**Check:**
- [ ] Client credentials valid
- [ ] Foundry endpoint accessible
- [ ] Model deployment exists
- [ ] Python version ≥ 3.10

### Issue: Context manager warning

**Check:**
- [ ] Using `async with Agent(...)` 
- [ ] Agent closed properly
- [ ] No resource leaks

### Issue: Tools not called

**Check:**
- [ ] Tool registered in `tools=[]`
- [ ] Tool description clear
- [ ] Agent instructions mention capability
- [ ] Tool signature uses `Annotated`

### Issue: Session context lost

**Check:**
- [ ] Using `await stream.get_final_response()`
- [ ] Session object reused across turns
- [ ] No new session created per turn

### Issue: Version conflicts

**Check:**
- [ ] Installation order correct
- [ ] No version floating pins
- [ ] Virtual environment fresh
- [ ] Delete build artifacts, retry

## Automated Checks

### Python Script to Verify

```python
import subprocess
import sys

checks = [
    ("Python version", lambda: sys.version_info >= (3, 10)),
    ("agent-framework-core", lambda: check_version("agent-framework-core", "1.0.0rc6")),
    ("azure-ai-agentserver-agentframework", lambda: check_version("azure-ai-agentserver-agentframework", "1.0.0b16")),
]

def check_version(package, expected):
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True, text=True
        )
        return expected in result.stdout
    except:
        return False

for check_name, check_fn in checks:
    status = "✓" if check_fn() else "✗"
    print(f"{status} {check_name}")
```

---

*Related: All other skills - this is the verification framework*
