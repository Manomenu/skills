# Agent Framework Code Generation - Sub-Skills Index

## Overview

This directory contains specialized skill files for Microsoft Foundry Agent Framework development. Each skill focuses on a specific aspect of agent development with detailed patterns, best practices, and troubleshooting guides.

## Available Skills

### 1. [Client and Credentials Setup](client-and-credentials-setup.md)
**Purpose:** Establish proper connection to Microsoft Foundry models

**Key Topics:**
- Mandatory `FoundryChatClient` usage
- Sync vs Async `DefaultAzureCredential`
- Client reusability across agents
- Environment variable configuration
- Authentication troubleshooting

**When to Use:** Before creating your first agent

---

### 2. [Agent Creation and Lifecycle](agent-creation-and-lifecycle.md)
**Purpose:** Instantiate and manage agent instances

**Key Topics:**
- Two agent creation methods: `Agent()` constructor vs `.as_agent()`
- Context manager patterns
- Agent naming conventions (alphanumeric, hyphens, 63 chars max)
- Resource lifecycle management
- Error handling

**When to Use:** When initializing agents in your code

---

### 3. [SDK Version Pinning and Dependencies](sdk-version-pinning-and-dependencies.md)
**Purpose:** Ensure consistent, reproducible environments

**Key Topics:**
- Exact version pins for Python and .NET
- Critical installation order (agentserver first, then agent-framework)
- Why version pinning matters
- Dependency resolution conflicts
- Updating to new versions safely

**When to Use:** Setting up new projects, debugging version issues

---

### 4. [Streaming and Production Patterns](streaming-and-production-patterns.md)
**Purpose:** Implement production-grade streaming responses

**Key Topics:**
- `.run(..., stream=True)` pattern
- Chunk filtering with `if chunk.text:`
- **Critical:** `await stream.get_final_response()` finalization
- Streaming vs non-streaming tradeoffs
- Web service integration
- Performance considerations

**When to Use:** Building real-time applications

---

### 5. [Tool Integration](tool-integration.md)
**Purpose:** Enable agents to call external functions

**Key Topics:**
- Mandatory `Annotated[type, "description"]` pattern
- Tool parameter types and validation
- Tool registration with agents
- Error handling in tools
- Rate limiting and performance
- Stateful vs stateless tools

**When to Use:** When agents need to perform external actions

---

### 6. [Model Context Protocol (MCP) Tools](mcp-tools-integration.md)
**Purpose:** Connect complex tool ecosystems via MCP standard

**Key Topics:**
- Stdio-based tools (Playwright)
- HTTP-based tools (Microsoft Learn)
- **Critical:** `load_prompts=False` for tools-only
- Streaming events from MCP tools
- Mixing custom and MCP tools
- Common tools and capabilities

**When to Use:** When you need browser automation, documentation access, or ecosystem tools

---

### 7. [Session Management](session-management.md)
**Purpose:** Maintain context across multi-turn conversations

**Key Topics:**
- Creating sessions for context persistence
- **Critical:** Always finalize streams with `await stream.get_final_response()`
- Multi-turn conversation patterns
- Session storage (in-memory and persistent)
- Session cleanup and lifecycle
- Context window considerations

**When to Use:** Building stateful chatbots and multi-turn applications

---

### 8. [Workflow Builder and Multi-Agent Patterns](workflow-builder-and-multi-agent-patterns.md)
**Purpose:** Orchestrate multiple agents and complex task flows

**Key Topics:**
- `WorkflowBuilder(start_executor=...)` pattern (NOT `.set_start_executor()`)
- Handler definitions with `@handler` decorator
- Multi-agent routing strategies
- State management in workflows
- Conditional logic and branching
- Sequential vs parallel processing

**When to Use:** Building complex agentic systems with multiple agents

---

### 9. [HTTP Server Deployment](http-server-deployment.md)
**Purpose:** Deploy agents as production web services

**Key Topics:**
- `from_agent_framework(agent).run_async()` hosting adapter
- Environment configuration
- Docker containerization
- Kubernetes deployment
- Framework integration (FastAPI, Flask)
- Scaling and load balancing
- Monitoring and logging

**When to Use:** Deploying agents to production

---

### 10. [Verification and Quality Checks](verification-and-quality-checks.md)
**Purpose:** Ensure code follows best practices and patterns

**Key Topics:**
- Comprehensive pre/post-generation checklist
- SDK pattern verification matrix
- Version verification
- Functional testing checklist
- Security verification
- Performance verification
- Pre-deployment checklist
- Automated verification scripts

**When to Use:** After generating/enhancing code, before deployment

---

## Quick Navigation Guide

### By Task

**I want to...**

- **Set up a new project** → Start with Skills #1, #3, then #2
- **Create a simple agent** → Skills #1, #2, #4
- **Add tools to my agent** → Skill #5 (or #6 for MCP tools)
- **Build a chatbot** → Skills #1, #2, #4, #7
- **Deploy to production** → Skills #3, #9, #10
- **Build multi-agent system** → Skills #1, #2, #8
- **Debug issues** → Skill #10 (Verification), then relevant skill

### By Skill Level

**Beginner** (Getting Started):
1. Client and Credentials Setup
2. Agent Creation and Lifecycle
3. SDK Version Pinning

**Intermediate** (Building Agents):
4. Streaming and Production Patterns
5. Tool Integration
6. Session Management

**Advanced** (Complex Systems):
7. Workflow Builder and Multi-Agent Patterns
8. MCP Tools Integration
9. HTTP Server Deployment
10. Verification and Quality Checks

---

## Cross-Skill Dependencies

```
Client & Credentials Setup
    ↓
Agent Creation & Lifecycle
    ├─→ Streaming Patterns ─→ Session Management
    ├─→ Tool Integration ─→ MCP Tools
    └─→ HTTP Server Deployment
         ↓
    Workflow Builder & Multi-Agent
         ↓
    Verification & Quality Checks
         ↓
    SDK Version Pinning (all skills)
```

---

## Key Patterns Summary

### Must Know Before Coding

1. **Use `FoundryChatClient`** - Only recommended client
2. **Sync `DefaultAzureCredential`** - Not async
3. **`Agent(client, name=..., instructions=...)`** - Not `create_agent()`
4. **`.run(input, stream=True)`** - Not `.run_stream()`
5. **`await stream.get_final_response()`** - CRITICAL for sessions
6. **`WorkflowBuilder(start_executor=...)`** - Not `.set_start_executor()`
7. **Pin all versions exactly** - No floating versions
8. **Install agentserver first** - Then agent-framework
9. **`load_prompts=False`** - For MCP tools without prompts
10. **Test before deployment** - Use verification checklist

---

## Common Questions Answered

### Where do I find X pattern?
Use the **By Task** section or **Cross-Skill Dependencies** diagram above.

### What's the right way to do X?
Check the specific skill file - each has a "Mandatory Pattern" or "Core Pattern" section.

### Why does my code fail with Y error?
Look for "Troubleshooting" section in each skill - troubleshooting scenarios listed there.

### How do I deploy my agent?
Follow Skill #9 (HTTP Server Deployment) after completing Skill #10 (Verification).

### What if I need version X instead?
Check Skill #3 (SDK Version Pinning) for safe upgrade procedures.

---

## How to Use This Collection

### For New Projects

1. Read Skill #1 (Client Setup) to understand connection patterns
2. Read Skill #3 (Version Pinning) and follow installation order
3. Read Skill #2 (Agent Creation) to create your first agent
4. As needed, read specific skills for your use case

### For Enhancements

1. Check Skill #10 (Verification) for what to validate
2. Find relevant skill(s) for your changes
3. After changes, use Skill #10 checklist

### For Troubleshooting

1. Check Skill #10 (Verification) for symptom/fix pairs
2. Read "Troubleshooting" section in relevant skill
3. Follow step-by-step debugging guidance

### For Deployment

1. Complete Skill #10 (Verification) checklist
2. Follow Skill #9 (HTTP Server Deployment)
3. Use deployment checklist at end of Skill #9

---

## Skill Relationships

Each skill:
- **Stands alone** - Can be read independently
- **References others** - "Related: " section shows connections
- **Provides examples** - Complete, runnable code samples
- **Covers patterns** - Both common and edge cases

---

## Updates and Changes

These skills are based on:
- **Microsoft Agent Framework SDK:** Version 1.0.0rc6 (Python)
- **Azure AI Agentserver:** Version 1.0.0b16
- **As of:** April 2026

When SDK versions update, check Skill #3 for version pin updates.

---

## Using With Main Knowledge Base

- **Main file:** `agent-framework-code-gen.md` - Overview and quick reference
- **Sub-skills:** This directory - Detailed patterns and examples
- **Together:** Comprehensive resource for Agent Framework development

---

*Last Updated: April 2026*
