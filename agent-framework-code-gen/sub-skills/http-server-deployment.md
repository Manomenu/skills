# HTTP Server Deployment

## Overview

Deploying agents as HTTP services enables production-grade accessibility. This skill covers the hosting adapter pattern and deployment strategies.

## The Hosting Adapter Pattern

### Mandatory Pattern

```python
from azure.ai.agentserver.agentframework import from_agent_framework

async with Agent(client, name="...", instructions="...") as agent:
    await from_agent_framework(agent).run_async()
```

### What This Does

- Converts agent into HTTP server
- Enables RESTful access
- Handles request routing
- Manages connection lifecycle
- Supports production deployment

### Required Dependencies

```
azure-ai-agentserver-agentframework==1.0.0b16
azure-ai-agentserver-core==1.0.0b16
```

These must be installed as part of the initial setup (see SDK Version Pinning skill).

## Basic HTTP Server Setup

### Minimal Server

```python
import os
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential
from azure.ai.agentserver.agentframework import from_agent_framework
from dotenv import load_dotenv

async def main():
    load_dotenv(override=False)
    
    # Setup client
    client = FoundryChatClient(
        project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        model=os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME"),
        credential=DefaultAzureCredential(),
    )
    
    # Create agent
    async with Agent(
        client=client,
        name="MyAgent",
        instructions="You are a helpful assistant."
    ) as agent:
        # Start HTTP server
        await from_agent_framework(agent).run_async()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Server Configuration

### Default Behavior

- **Host:** localhost
- **Port:** 8000 (or env var AGENT_PORT)
- **Endpoint:** `http://localhost:8000/chat`

### Custom Configuration

```python
import os

# Set via environment
os.environ["AGENT_HOST"] = "0.0.0.0"  # Listen on all interfaces
os.environ["AGENT_PORT"] = "5000"      # Custom port

# Then run server
await from_agent_framework(agent).run_async()
```

## HTTP Endpoints

### Chat Endpoint

**POST `/chat`**

```json
{
  "messages": [
    {
      "role": "user",
      "content": "What's 2+2?"
    }
  ]
}
```

**Response:**
```json
{
  "message": {
    "role": "assistant",
    "content": "2+2 equals 4."
  }
}
```

### Health Check

**GET `/health`**

Returns server status.

## Production Deployment

### Docker Containerization

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies (in correct order!)
RUN pip install \
    azure-ai-agentserver-agentframework==1.0.0b16 \
    azure-ai-agentserver-core==1.0.0b16 \
    agent-dev-cli==0.0.1b260316 && \
    pip install \
    agent-framework-core==1.0.0rc6 \
    agent-framework-foundry==1.0.0rc6 \
    agent-framework-openai==1.0.0rc6 && \
    pip install -r requirements.txt

# Copy application
COPY . .

# Run server
CMD ["python", "-m", "agent_server"]
```

### Environment Variables for Deployment

```bash
FOUNDRY_PROJECT_ENDPOINT=<your-endpoint>
FOUNDRY_MODEL_DEPLOYMENT_NAME=<your-model>
AZURE_SUBSCRIPTION_ID=<subscription>
AGENT_HOST=0.0.0.0
AGENT_PORT=8080
```

### Running in Docker

```bash
docker build -t my-agent:latest .
docker run -p 8080:8080 \
  -e FOUNDRY_PROJECT_ENDPOINT=$ENDPOINT \
  -e FOUNDRY_MODEL_DEPLOYMENT_NAME=$MODEL \
  my-agent:latest
```

## Kubernetes Deployment

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-agent-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-agent
  template:
    metadata:
      labels:
        app: my-agent
    spec:
      containers:
      - name: agent
        image: myregistry.azurecr.io/my-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: FOUNDRY_PROJECT_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: foundry-endpoint
        - name: FOUNDRY_MODEL_DEPLOYMENT_NAME
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: model-name
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: my-agent-service
spec:
  selector:
    app: my-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

## Integration with Web Frameworks

### FastAPI Integration

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

@app.post("/chat")
async def chat(request: dict):
    """Chat endpoint using agent."""
    user_message = request.get("message", "")
    
    async def generate():
        stream = agent.run(user_message, stream=True)
        async for chunk in stream:
            if chunk.text:
                yield chunk.text
        await stream.get_final_response()
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
```

### Flask Integration

```python
from flask import Flask, jsonify, request
import asyncio

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint using agent."""
    data = request.json
    user_message = data.get("message", "")
    
    async def run_agent():
        result = await agent.run(user_message)
        return result.text
    
    response = asyncio.run(run_agent())
    return jsonify({"response": response})

@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})
```

## Error Handling in Deployment

### Connection Errors

```python
try:
    client = FoundryChatClient(
        project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        model=os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME"),
        credential=DefaultAzureCredential(),
    )
except Exception as e:
    print(f"Failed to initialize client: {e}")
    # Retry with exponential backoff
    # Or fail fast in dev, graceful in prod
```

### Request Timeout

```python
# Set reasonable timeouts
import asyncio

async def run_with_timeout():
    try:
        result = await asyncio.wait_for(
            agent.run("query"),
            timeout=30.0  # 30 second timeout
        )
        return result
    except asyncio.TimeoutError:
        return {"error": "Request timed out"}
```

## Scaling Considerations

### Load Balancing

- Run multiple agent instances
- Use load balancer (nginx, Azure Load Balancer)
- Route requests across instances
- Session affinity for stateful operations

### Connection Pooling

```python
# Reuse client across multiple agents/requests
client = FoundryChatClient(...)  # Create once

# Multiple agents can share client
agent1 = Agent(client, name="Agent1", ...)
agent2 = Agent(client, name="Agent2", ...)
```

## Monitoring and Logging

### Basic Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting agent server")
    
    # ... setup code ...
    
    logger.info("Server ready to accept requests")
    await from_agent_framework(agent).run_async()
```

### Structured Logging

```python
import json
from datetime import datetime

def log_request(user_message, response, duration):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_message": user_message,
        "response_length": len(response),
        "duration_ms": duration * 1000
    }
    print(json.dumps(log_entry))
```

## Best Practices

1. **Use from_agent_framework adapter** for deployment
2. **Environment variables** for all configuration
3. **Health checks** for monitoring
4. **Error handling** at all levels
5. **Request timeouts** to prevent hangs
6. **Connection pooling** for efficiency
7. **Graceful shutdown** handlers
8. **Load testing** before production
9. **Monitor performance** metrics
10. **Keep dependencies pinned** for reproducibility

## Troubleshooting

### Port Already in Use

```bash
# Find process on port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
AGENT_PORT=8001 python server.py
```

### Authentication Failures

- Verify credentials are available
- Check Azure CLI login: `az account show`
- Verify RBAC permissions in Foundry

### Timeouts

- Check server logs for slow operations
- Increase timeout values
- Optimize agent instructions/tools
- Check network connectivity

---

*Related: Agent Creation, Streaming Patterns, Workflow Builder*
