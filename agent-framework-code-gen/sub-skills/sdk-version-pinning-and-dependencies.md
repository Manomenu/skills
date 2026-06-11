# SDK Version Pinning and Dependencies

## Critical Importance

The Microsoft Agent Framework SDK is in preview with **frequent breaking renames and API changes**. **Always pin versions exactly** - never use floating versions or latest tags.

## Why Version Pinning Matters

- **Breaking Changes** - API methods change frequently between versions
- **Dependency Conflicts** - Different packages pull different versions
- **Production Stability** - Pinned versions ensure predictable behavior
- **Reproducibility** - Same versions across environments

## Python SDK Versions

### Current Pinned Versions

```
agent-framework-core==1.0.0rc6
agent-framework-foundry==1.0.0rc6
agent-framework-openai==1.0.0rc6
azure-ai-agentserver-agentframework==1.0.0b16
azure-ai-agentserver-core==1.0.0b16
agent-dev-cli==0.0.1b260316
```

### Python Version Requirement

- **Minimum:** Python 3.10+
- **Recommended:** Python 3.11 or later
- **Incompatible:** Python 3.9 and earlier

## Installation Order (CRITICAL)

**The order of installation matters. Install in this exact sequence:**

### Step 1: Install AgentServer and CLI First

This pulls in compatible versions including `agent-framework-core==1.0.0rc3`:

```bash
pip install \
  azure-ai-agentserver-agentframework==1.0.0b16 \
  azure-ai-agentserver-core==1.0.0b16 \
  agent-dev-cli==0.0.1b260316
```

### Step 2: Install Agent Framework rc6 (Overrides rc3)

After agentserver is installed, upgrade to the required rc6 versions:

```bash
pip install \
  agent-framework-core==1.0.0rc6 \
  agent-framework-foundry==1.0.0rc6 \
  agent-framework-openai==1.0.0rc6
```

### Why This Order?

- `azure-ai-agentserver-*` pins `agent-framework-core<=1.0.0rc3`
- Installing rc6 afterward overrides the rc3 version
- Doing it in reverse order causes dependency resolver conflicts
- This approach ensures clean, reproducible installs

## Why NOT Just Install Everything at Once?

```bash
# ❌ DON'T DO THIS
pip install \
  azure-ai-agentserver-agentframework==1.0.0b16 \
  agent-framework-core==1.0.0rc6 \
  ... # other packages
```

**Problem:** Pip tries to resolve both constraints simultaneously, often failing or choosing wrong versions.

**Solution:** Install in sequence (Step 1, then Step 2).

## .NET SDK Versions

### Package Installation

```bash
dotnet add package Microsoft.Agents.AI.AzureAI --prerelease
dotnet add package Microsoft.Agents.AI.OpenAI --prerelease
dotnet add package Microsoft.Agents.AI.Workflows --prerelease
```

### .NET Version Requirement

- **Minimum:** .NET 8.0+
- **Recommended:** .NET 9.0 or later

### Using --prerelease Flag

The `--prerelease` flag is required because these packages are in preview. Without it, dotnet will not resolve the packages.

## Version-Specific API Patterns

The pinned version `1.0.0rc6` uses specific API names that **differ from online documentation or older versions**.

### Always Use These Exact Patterns

When you see examples online or in official docs that differ from these patterns, check the version. Our pinned version (rc6) may have different API names.

**Example inconsistency:**
- Older versions: `create_agent()`
- rc6 (current): `Agent(...)` constructor

### Where to Find Version-Specific Patterns

See "Core Coding Patterns" section in the main knowledge base for all 10 patterns specific to rc6.

## Updating to New Versions

When Microsoft releases new versions, follow these steps:

1. **Check breaking changes** in the release notes
2. **Update ALL packages together** to maintain compatibility
3. **Follow new installation order** if provided
4. **Test thoroughly** with your agents before deployment
5. **Update documentation** with new version numbers

## Dependency Management

### Core Dependencies

```
agent-framework-core
agent-framework-foundry
agent-framework-openai
```

### Server/Hosting Dependencies

```
azure-ai-agentserver-agentframework
azure-ai-agentserver-core
```

### Development/Debug Dependencies

```
agent-dev-cli
```

### Transitive Dependencies

These are pulled in automatically:
- `azure-identity` (for credentials)
- `azure-core` (for HTTP client)
- `pydantic` (for data validation)

## Requirements.txt Example

```
# Agent Framework - PINNED VERSIONS
agent-framework-core==1.0.0rc6
agent-framework-foundry==1.0.0rc6
agent-framework-openai==1.0.0rc6

# Agent Server - INSTALL FIRST
azure-ai-agentserver-agentframework==1.0.0b16
azure-ai-agentserver-core==1.0.0b16

# Development
agent-dev-cli==0.0.1b260316

# Support packages
azure-identity>=1.13.0
python-dotenv>=1.0.0
```

### Installation from requirements.txt

```bash
# If using file for first install:
pip install -r requirements.txt

# Or follow manual step-by-step approach for safety
```

## Version Verification

### Check Installed Versions

```bash
pip show agent-framework-core
pip show azure-ai-agentserver-agentframework
```

### In Python Code

```python
import agent_framework
print(agent_framework.__version__)
```

## Best Practices

1. **Pin all versions** in requirements.txt or setup.py
2. **Use exact pinning** (`==` not `>=` or `~=`)
3. **Document the installation order** in README
4. **Test installation procedure** before deployment
5. **Update all packages together** when upgrading
6. **Keep a change log** of version updates
7. **Review breaking changes** in release notes before upgrading

## Troubleshooting

### ImportError: No module named 'agent_framework'

- Verify installation completed successfully
- Check Python version is 3.10+
- Reinstall following exact step order

### AttributeError: Agent has no attribute 'run_stream'

- This method doesn't exist in rc6
- Use `.run(..., stream=True)` instead
- Check version with `pip show agent-framework-core`

### Dependency Resolution Errors

- Follow the two-step installation process exactly
- Don't mix installation orders
- Consider using virtual environment
- Delete `build/` and `.egg-info/` directories, then retry

---

*Related: Client Setup, Deployment Patterns, Environment Configuration*
