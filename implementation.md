# Safe Prompts for A2-Agents Backend
# Updated for /Users/aaronlax/Projects/A2/a2-agents
# Run claude code assistant from parent A2 directory

## 00-compose-safe.txt
## 11-frontend-hookup.txt
```
Connect the lovable.dev frontend shell to the A2-agents backend.

**Examine a2-agents/frontend structure first to determine the framework (React, Vue, etc.)**

Update frontend API configuration:

1. **Environment Variables** - Create/update frontend environment file:

   For React (frontend/.env.local):
   ```
   REACT_APP_API_BASE_URL=http://localhost:8080
   REACT_APP_WS_URL=ws://localhost:8080
   ```

   For Vue (frontend/.env.local):
   ```
   VITE_API_BASE_URL=http://localhost:8080
   VITE_WS_URL=ws://localhost:8080
   ```

2. **API Client** - Update frontend API calls to use the backend endpoints:

   ```javascript
   // Frontend API service example
   const API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080';

   export const agentAPI = {
     // Spawn a new agent thread
     spawnAgent: async (role, initialPrompt) => {
       const response = await fetch(`${API_BASE}/agents/${role}/threads`, {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ initial_prompt: initialPrompt })
       });
       return response.json();
     },

     // Send message to thread
     sendMessage: async (threadId, content) => {
       const response = await fetch(`${API_BASE}/threads/${threadId}/messages`, {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ content })
       });
       return response.json();
     },

     // Connect to SSE stream
     connectToStream: (threadId, onMessage) => {
       const eventSource = new EventSource(`${API_BASE}/threads/${threadId}/stream`);

       eventSource.onmessage = (event) => {
         const data = JSON.parse(event.data);
         onMessage(data);
       };

       eventSource.onerror = (error) => {
         console.error('SSE Error:', error);
         eventSource.close();
       };

       return eventSource;
     }
   };
   ```

3. **Agent Components** - Update UI components to display agents from REFERENCE.md:

   ```javascript
   const AGENT_ROLES = [
     'OrchestratorAgent',
     'ResearchAgent',
     'FirmwareEngineer',
     'ROSDeveloper',
     'IntegrationSpecialist',
     'SafetyEngineer',
     'DocumentationMaintainer',
     'QATester'
   ];

   // Agent selector component
   const AgentSelector = ({ onSelect }) => (
     <select onChange={(e) => onSelect(e.target.value)}>
       <option value="">Select an agent...</option>
       {AGENT_ROLES.map(role => (
         <option key={role} value={role}>{role}</option>
       ))}
     </select>
   );
   ```

4. **Thread Management** - Implement thread state management:

   ```javascript
   // Thread state example
   const [threads, setThreads] = useState({});
   const [activeThread, setActiveThread] = useState(null);
   const [messages, setMessages] = useState([]);

   const createThread = async (agentRole) => {
     const { thread_id } = await agentAPI.spawnAgent(agentRole, 'Hello!');
     setThreads(prev => ({
       ...prev,
       [thread_id]: { role: agentRole, messages: [] }
     }));
     setActiveThread(thread_id);

     // Connect to SSE stream
     const eventSource = agentAPI.connectToStream(thread_id, (data) => {
       setMessages(prev => [...prev, data]);
     });
   };
   ```

5. **Message Routing UI** - Implement @ mention routing:

   ```javascript
   // Parse @ mentions in message input
   const parseMessage = (content) => {
     const mentionPattern = /^@(\w+)\s+(.+)/;
     const match = content.match(mentionPattern);

     if (match) {
       return {
         targetAgent: match[1],
         message: match[2],
         isDirect: true
       };
     }

     return {
       targetAgent: 'OrchestratorAgent',
       message: content,
       isDirect: false
     };
   };
   ```

6. **Multi-Panel Layout** - Implement the multi-panel view from REFERENCE.md:

   ```javascript
   // Layout for multiple agent panels
   const MultiAgentView = () => (
     <div className="agent-panels">
       <div className="orchestrator-panel">
         <h2>Orchestrator Overview</h2>
         {/* Thread list, routing status */}
       </div>

       <div className="agent-grid">
         {AGENT_ROLES.map(role => (
           <div key={role} className="agent-panel">
             <h3>{role}</h3>
             {/* Agent-specific messages */}
           </div>
         ))}
       </div>
     </div>
   );
   ```

7. **Update package.json proxy** (if using Create React App):

   ```json
   {
     "proxy": "http://localhost:8080"
   }
   ```

8. **CORS handling** - The API Gateway already has CORS enabled, but ensure frontend runs on expected port (3000).

Test the integration:
1. Start backend: `cd a2-agents && make up`
2. Start frontend: `cd a2-agents/frontend && npm start`
3. Open http://localhost:3000
4. Try spawning an agent and sending messages
Read a2-agents/REFERENCE.md for full system context.

**IMPORTANT: DO NOT DELETE ANY EXISTING FILES. ONLY UPDATE OR ADD NEW FILES.**

Update the existing a2-agents/docker-compose.yaml (or create if missing) matching the architecture in REFERENCE.md section 3:
- api-gateway (fastapi, port 8080, image tag a2/agents-api)
- orchestrator-logic (image tag a2/agents-orch)
- agent-manager (image tag a2/agent-mgr)
- repo-proxy (port 7000, image tag a2/repo-proxy)
- ci-trigger (image tag a2/ci-trigger)
- nats (latest, expose 4222)
- redis (6-alpine, port 6379)
- postgres (15-alpine, db=a2_agents, user=a2user)

Requirements:
- Services under ./services/{service_name} build contexts
- Add health check for NATS: nc -z localhost 4222
- Add health check for postgres: pg_isready -U a2user -d a2_agents
- Use environment variables from REFERENCE.md section 8
- Create volumes: redis-data, postgres-data, repo-data
- Single shared network: a2-network
- Add proper service dependencies with conditions
- Add frontend service if needed for development
- Configure frontend to connect to api-gateway on port 8080

Reference: https://docs.docker.com/compose/compose-file/compose-file-v3/
```

## 00b-frontend-integration.txt
```
Read a2-agents/REFERENCE.md and check a2-agents/frontend structure.

Add frontend service to docker-compose.yaml if it's a React/Node app:

```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8080
      - REACT_APP_WS_URL=ws://localhost:8080
    depends_on:
      - api-gateway
    networks:
      - a2-network
    volumes:
      - ./frontend:/app
      - /app/node_modules
```

Or if frontend is static files, add nginx service:

```yaml
  frontend:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
      - ./frontend/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api-gateway
    networks:
      - a2-network
```

Update frontend configuration to connect to backend:
- API endpoints: http://localhost:8080
- SSE streams: http://localhost:8080/threads/{id}/stream
- WebSocket (if used): ws://localhost:8080

Create frontend/.env.local if React:
```
REACT_APP_API_URL=http://localhost:8080
REACT_APP_SSE_URL=http://localhost:8080
```

## 01-api-gateway-safe.txt
```
Read a2-agents/REFERENCE.md for full system context.

**PRESERVE EXISTING FILES - Only create new files in a2-agents/services/api_gateway/**

Generate FastAPI service in a2-agents/services/api_gateway/main.py with:

Routes (section 7):
- POST /agents/{role}/threads - spawn new agent thread
- POST /threads/{id}/messages - send message to thread
- GET /threads/{id}/stream - SSE event stream
- POST /orchestrator/command - admin commands

Pydantic models:
```python
class MsgIn(BaseModel):
    content: str
    metadata: dict = {}

class MsgOut(BaseModel):
    thread_id: str
    agent: str
    content: str
    timestamp: datetime
    metadata: dict = {}

class ThreadResponse(BaseModel):
    thread_id: str
    agent_role: str
    status: str

class OrchestratorCommand(BaseModel):
    action: Literal["pause", "kill", "dump_state"]
    thread_id: Optional[str] = None
```

NATS integration (section 4):
- Publish to `thread.<id>.from_ui` for incoming messages
- Subscribe to `thread.<id>.to_ui` for SSE streaming
- Use nats-py client with connection to NATS_URL env var

SSE implementation:
- Use async generator pattern
- Set media_type='text/event-stream'
- Format: "data: {json}\n\n"
- Include heartbeat every 30s

Requirements:
- Health check endpoint: GET /health
- CORS middleware for browser access
- Proper error handling with HTTPException
- Connection pooling for NATS

Also create:
- a2-agents/services/api_gateway/requirements.txt
- a2-agents/services/api_gateway/Dockerfile

Reference: https://fastapi.tiangolo.com/advanced/server-sent-events/
```

## 02-agent-manager-safe.txt
```
Read a2-agents/REFERENCE.md for full system context.

**PRESERVE EXISTING FILES - Only create new files in a2-agents/services/agent_manager/**

Write Python service in a2-agents/services/agent_manager/main.py:

Core functionality:
- POST /spawn endpoint accepting (role, thread_id, initial_prompt)
- Use anthropic.messages.create with stream=True
- Map agent roles to Claude settings (e.g., ResearchAgent → claude-3-opus, temp=0.7)

Anthropic streaming:
```python
import anthropic
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

async def spawn_claude(role: str, thread_id: str, prompt: str):
    with client.messages.stream(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        temperature=0.7,
        system=f"You are {role}. {get_role_context(role)}",
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                chunk = event.delta.text
                # Publish to NATS
```

NATS publishing (section 4):
- Publish each chunk to `thread.<thread_id>.agent.<role>`
- Message format: {"chunk": str, "role": str, "timestamp": datetime}

Redis state (section 6):
- Store in hash `claude:<thread_id>` → {role: anthropic_conversation_id}
- Use redis-py with connection pooling

Agent role mappings from lovable spec:
- OrchestratorAgent: system prompt includes routing rules
- ResearchAgent: includes web search capability hint
- FirmwareEngineer: includes Teensy 4.1 context
- ROSDeveloper: includes ROS 2 Humble context
- SafetyEngineer: includes SAFETY-BLOCK privilege

Requirements:
- Graceful shutdown on SIGTERM
- Retry logic for Anthropic API (exponential backoff)
- Health endpoint exposing agent count

Also create:
- a2-agents/services/agent_manager/requirements.txt
- a2-agents/services/agent_manager/Dockerfile

Reference: https://docs.anthropic.com/en/api/messages-streaming
```

## 03-orchestrator-logic-safe.txt
```
Read a2-agents/REFERENCE.md for full system context, especially sections 4-6.

**PRESERVE EXISTING FILES - Only create new files in a2-agents/services/orchestrator_logic/**

Build a2-agents/services/orchestrator_logic/main.py:

NATS subscriptions:
- Subscribe to wildcard `thread.*` to catch all thread traffic
- Parse subject to extract thread_id, source type (from_ui, agent.*, etc)

Routing implementation (section 5):
```python
def route_message(thread_id: str, msg: dict) -> List[str]:
    content = msg.get('content', '')

    # Rule 1: Direct routing
    if content.startswith('@'):
        target = extract_agent_name(content)
        return [f"thread.{thread_id}.agent.{target}"]

    # Rule 2: Default to OrchestratorAgent
    if msg.get('source') == 'ui':
        return [f"thread.{thread_id}.agent.OrchestratorAgent"]

    # Rule 3: Safety block
    if msg.get('type') == 'SAFETY-BLOCK':
        halt_thread(thread_id)
        return []

    # OrchestratorAgent decides broadcast
    if should_broadcast(msg):
        return [f"thread.{thread_id}.broadcast"]

    return determine_targets(msg)
```

Memory management (section 6):
- Append messages to Redis list `conv:{thread_id}`
- Trim to 100 most recent: LTRIM conv:{thread_id} -100 -1
- Track active threads in Redis set `threads`
- Background task every 60s:
  - Batch read old messages beyond 100
  - Bulk insert to Postgres `history` table
  - Schema: (id, thread_id, agent, timestamp, message JSONB)

Thread lifecycle:
- Create thread: add to `threads` set
- Archive thread: move all Redis data to Postgres, remove from set
- Thread states: active, paused, archived

Special handling:
- SafetyEngineer SAFETY-BLOCK: immediately halt, notify all agents
- OrchestratorAgent can open/close threads
- Rate limiting: track in Redis, 30 msgs/min per agent

Postgres schema:
```sql
CREATE TABLE history (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR(64) NOT NULL,
    agent VARCHAR(64) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    message JSONB NOT NULL,
    INDEX idx_thread_time (thread_id, timestamp)
);

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    agent VARCHAR(64),
    action VARCHAR(128),
    details JSONB
);
```

Requirements:
- Async event loop with asyncio
- Graceful shutdown preserving memory
- Publish UI updates to `thread.<id>.to_ui`
- Health check with thread count

Also create:
- a2-agents/services/orchestrator_logic/requirements.txt
- a2-agents/services/orchestrator_logic/Dockerfile
```

## 04-repo-proxy-safe.txt
```
Read a2-agents/REFERENCE.md for full system context, especially section 11 (ACL Matrix).

**PRESERVE EXISTING FILES - Only create new files in a2-agents/services/repo_proxy/**

Create Flask service in a2-agents/services/repo_proxy/main.py enforcing repository access control:

JWT validation:
```python
import jwt
from flask import Flask, request, abort

def validate_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        abort(401)

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        agent = payload.get('agent')
        return agent
    except jwt.InvalidTokenError:
        abort(401)
```

ACL enforcement (section 11):
```python
ACL_MATRIX = {
    'FirmwareEngineer': ['teensy-firmware/', 'firmware/'],
    'ROSDeveloper': ['ros-workspace/', 'ros2_ws/'],
    'DocumentationMaintainer': ['docs/', 'guides/'],
    # Read-only agents have empty lists
}

def check_acl(agent: str, path: str, method: str) -> bool:
    if method == 'GET':
        return True  # All agents can read

    allowed_paths = ACL_MATRIX.get(agent, [])
    for allowed in allowed_paths:
        if path.startswith(allowed):
            return True
    return False
```

Git operations with pygit2:
```python
import pygit2

# GET /repo/<path>
def read_file(repo_path: str):
    repo = pygit2.Repository('/var/repos/A2')
    obj = repo.revparse_single(f'HEAD:{repo_path}')
    if obj.type == pygit2.GIT_OBJ_BLOB:
        return obj.data.decode('utf-8')
    abort(404)

# PUT /repo/<path>
def write_file(repo_path: str, content: str, agent: str):
    # 1. Create feature branch
    # 2. Write file
    # 3. Commit with message f"[{agent}] Update {repo_path}"
    # 4. Push to origin
    # 5. Create PR via GitHub API
```

GitHub PR creation:
```python
import requests

def create_pr(branch: str, title: str, agent: str):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    data = {
        'title': title,
        'head': branch,
        'base': 'dev',
        'body': f'Automated PR from {agent}'
    }
    requests.post(
        'https://api.github.com/repos/War-Against-Work/A2/pulls',
        json=data,
        headers=headers
    )
```

Audit logging:
- Log all write attempts to Postgres `audit_log` table
- Include: timestamp, agent, action, path, success/failure

Submodule handling:
- Check if path maps to submodule from env.submodules
- Use appropriate repo URL for operations

Requirements:
- Port 7000
- Mount /var/repos volume
- Health check endpoint
- Request logging with correlation IDs
- Rate limiting per agent

Also create:
- a2-agents/services/repo_proxy/requirements.txt
- a2-agents/services/repo_proxy/Dockerfile
```

## 05-ci-trigger-safe.txt
```
Read a2-agents/REFERENCE.md for full system context.

**PRESERVE EXISTING FILES - Only create new files in a2-agents/services/ci_trigger/**

Create a2-agents/services/ci_trigger/main.py that subscribes to QATester messages:

NATS subscription:
```python
import asyncio
import nats
from nats.aio.client import Client as NATS

async def run():
    nc = NATS()
    await nc.connect(os.getenv('NATS_URL'))

    async def qa_handler(msg):
        data = json.loads(msg.data.decode())
        thread_id = extract_thread_id(msg.subject)

        if data.get('command') == 'ci_run':
            workflow = data.get('workflow', 'test.yml')
            await trigger_github_action(workflow, thread_id)

    await nc.subscribe('thread.*.agent.QATester', cb=qa_handler)
```

GitHub Actions trigger:
```python
import aiohttp

async def trigger_github_action(workflow: str, thread_id: str):
    url = f"https://api.github.com/repos/War-Against-Work/A2/actions/workflows/{workflow}/dispatches"

    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    data = {
        'ref': 'dev',
        'inputs': {
            'thread_id': thread_id,
            'triggered_by': 'QATester'
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status == 204:
                # Success - publish status back
                await publish_status(thread_id, 'CI triggered successfully')
            else:
                error = await resp.text()
                await publish_status(thread_id, f'CI trigger failed: {error}')
```

Status feedback:
```python
async def publish_status(thread_id: str, status: str):
    msg = {
        'agent': 'ci-trigger',
        'type': 'status',
        'content': status,
        'timestamp': datetime.utcnow().isoformat()
    }
    await nc.publish(
        f'thread.{thread_id}.agent.QATester',
        json.dumps(msg).encode()
    )
```

Supported workflows:
- test.yml: Run full test suite
- safety-check.yml: E-stop latency verification
- integration.yml: Hardware-in-loop tests

Error handling:
- GitHub API rate limiting (check X-RateLimit headers)
- Invalid workflow names
- Network failures with exponential backoff

Requirements:
- Async Python with aiohttp
- GitHub App authentication setup
- Health endpoint returning last trigger time
- Graceful shutdown preserving in-flight requests

Also create:
- a2-agents/services/ci_trigger/requirements.txt
- a2-agents/services/ci_trigger/Dockerfile
```

## 06-dockerfile-safe.txt
```
Read a2-agents/REFERENCE.md for directory structure.

**DO NOT OVERWRITE EXISTING DOCKERFILES - Only create missing ones**

For each service directory that does NOT already have a Dockerfile, create one:

Base Dockerfile template:
```dockerfile
FROM python:3.12-slim

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Default command
CMD ["python", "main.py"]
```

Service-specific requirements.txt examples:

api_gateway:
- fastapi==0.109.0
- uvicorn[standard]==0.27.0
- nats-py==2.6.0
- redis==5.0.1
- sse-starlette==1.8.2

agent_manager:
- anthropic==0.18.0
- nats-py==2.6.0
- redis==5.0.1
- asyncio==3.4.3

orchestrator_logic:
- nats-py==2.6.0
- redis==5.0.1
- asyncpg==0.29.0
- asyncio==3.4.3

repo_proxy:
- flask==3.0.0
- pygit2==1.13.3
- PyJWT==2.8.0
- requests==2.31.0
- psycopg2-binary==2.9.9

ci_trigger:
- nats-py==2.6.0
- aiohttp==3.9.1
- asyncio==3.4.3

Check these directories and only create Dockerfile if missing:
- a2-agents/services/api_gateway/Dockerfile
- a2-agents/services/agent_manager/Dockerfile
- a2-agents/services/orchestrator_logic/Dockerfile
- a2-agents/services/repo_proxy/Dockerfile
- a2-agents/services/ci_trigger/Dockerfile

Similarly, only create requirements.txt if missing for each service.
```

## 07-env-safe.txt
```
Read a2-agents/REFERENCE.md section 8 for environment variables.

**PRESERVE EXISTING .env FILE IF IT EXISTS**

If a2-agents/.env.example does NOT exist, create it with:

```bash
# Anthropic API Configuration
# Get your API key from https://console.anthropic.com/
ANTHROPIC_API_KEY=

# GitHub App Configuration
# Create a GitHub App with repo permissions
GITHUB_APP_ID=
GITHUB_PRIVATE_KEY=

# Database Configuration
# Strong password for PostgreSQL
POSTGRES_PASSWORD=

# Service URLs (usually don't need to change for local dev)
REDIS_URL=redis://redis:6379/1
NATS_URL=nats://nats:4222

# Optional: Override default ports
# API_GATEWAY_PORT=8080
# REPO_PROXY_PORT=7000

# Optional: JWT Secret for repo-proxy auth
# Generate with: openssl rand -hex 32
JWT_SECRET_KEY=

# Optional: GitHub Personal Access Token (alternative to GitHub App)
# GITHUB_TOKEN=

# Optional: Log levels
# LOG_LEVEL=INFO

# Optional: Thread retention
# HISTORY_DAYS=30
# REDIS_TRIM_SIZE=100
```

Also create a2-agents/.env.test for testing:
```bash
ANTHROPIC_API_KEY=test-key
GITHUB_APP_ID=12345
GITHUB_PRIVATE_KEY=test-private-key
POSTGRES_PASSWORD=testpass123
REDIS_URL=redis://redis:6379/2
NATS_URL=nats://nats:4222
JWT_SECRET_KEY=test-secret-key-for-testing-only
LOG_LEVEL=DEBUG
```

Include instructions:
1. Copy .env.example to .env
2. Fill in your actual values
3. Never commit .env file
4. For production, use proper secret management

If a2-agents/.env file already exists with values, DO NOT TOUCH IT.
If a2-agents/.env does not exist but .env.example does, you can copy .env.example to .env

NEVER DELETE OR OVERWRITE AN EXISTING .env FILE WITH ACTUAL VALUES.
```

## 08-makefile-safe.txt
```
Read a2-agents/REFERENCE.md for service names and structure.

**PRESERVE EXISTING MAKEFILE - Only add new targets if missing**

Update or create a2-agents/Makefile with these targets (preserve any existing custom targets):

```makefile
.PHONY: help up down logs test build clean setup

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup    - Initial setup (create dirs, copy env)"
	@echo "  make build    - Build all Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - Follow all service logs"
	@echo "  make test     - Run test suite"
	@echo "  make clean    - Remove containers and volumes"
	@echo "  make ps       - Show running services"
	@echo "  make shell-X  - Shell into service X"

# Initial setup
setup:
	@echo "Setting up A2-agents..."
	@mkdir -p services/{api_gateway,orchestrator_logic,agent_manager,repo_proxy,ci_trigger}/src
	@mkdir -p tests
	@if [ ! -f .env ]; then cp .env.example .env && echo "Created .env file - please edit it"; fi
	@echo "Setup complete!"

# Build all images
build:
	docker compose build

# Start services
up:
	docker compose up -d
	@echo "Services starting... Check http://localhost:8080/health"

# Stop services
down:
	docker compose down

# View logs
logs:
	docker compose logs -f

# Specific service logs
logs-%:
	docker compose logs -f $*

# Run tests
test:
	docker compose -f docker-compose.yaml -f docker-compose.test.yaml run --rm test-runner

# Show running containers
ps:
	docker compose ps

# Shell access to services
shell-api:
	docker compose exec api-gateway /bin/bash

shell-orchestrator:
	docker compose exec orchestrator-logic /bin/bash

shell-agent:
	docker compose exec agent-manager /bin/bash

shell-repo:
	docker compose exec repo-proxy /bin/bash

shell-nats:
	docker compose exec nats sh

shell-redis:
	docker compose exec redis redis-cli

shell-postgres:
	docker compose exec postgres psql -U a2user -d a2_agents

# Clean everything
clean:
	docker compose down -v
	@echo "Removed all containers and volumes"

# Development helpers
dev-init-db:
	docker compose exec postgres psql -U a2user -d a2_agents -f /docker-entrypoint-initdb.d/schema.sql

dev-spawn-agent:
	@curl -X POST http://localhost:8080/agents/ResearchAgent/threads \
		-H "Content-Type: application/json" \
		-d '{"initial_prompt": "Hello, Research Agent!"}'

# Health checks
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8080/health | jq '.' || echo "API Gateway not responding"
	@docker compose exec redis redis-cli ping || echo "Redis not responding"
	@docker compose exec postgres pg_isready || echo "Postgres not responding"
```

Also ensure a2-agents/docker-compose.test.yaml exists:
```yaml
version: '3.9'

services:
  test-runner:
    build:
      context: ./tests
      dockerfile: Dockerfile.test
    environment:
      - API_GATEWAY_URL=http://api-gateway:8080
      - REDIS_URL=redis://redis:6379/2
    depends_on:
      - api-gateway
      - orchestrator-logic
      - agent-manager
    networks:
      - a2-network
    volumes:
      - ./tests:/app/tests
```

DO NOT remove any existing make targets that aren't in this list.
```

## 09-pytest-smoke-safe.txt
```
Read a2-agents/REFERENCE.md for API endpoints and message flow.

**PRESERVE EXISTING TESTS - Only add new test files**

If a2-agents/tests/test_smoke.py does NOT exist, create it:

```python
import pytest
import asyncio
import aiohttp
import json
from datetime import datetime
import os

API_BASE = os.getenv('API_GATEWAY_URL', 'http://localhost:8080')

@pytest.fixture
async def client_session():
    async with aiohttp.ClientSession() as session:
        yield session

class TestSmokeTests:
    """Basic smoke tests for A2-agents system"""

    @pytest.mark.asyncio
    async def test_health_check(self, client_session):
        """All services should be healthy"""
        async with client_session.get(f"{API_BASE}/health") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data['status'] == 'healthy'

    @pytest.mark.asyncio
    async def test_spawn_research_agent(self, client_session):
        """Should spawn a ResearchAgent and return thread_id"""
        payload = {
            "initial_prompt": "What are the latest Stewart platform control algorithms?"
        }

        async with client_session.post(
            f"{API_BASE}/agents/ResearchAgent/threads",
            json=payload
        ) as resp:
            assert resp.status == 200
            data = await resp.json()
            assert 'thread_id' in data
            assert data['agent_role'] == 'ResearchAgent'
            return data['thread_id']

    @pytest.mark.asyncio
    async def test_sse_stream_receives_data(self, client_session):
        """SSE stream should receive agent responses within 5 seconds"""
        # First spawn an agent
        thread_id = await self.test_spawn_research_agent(client_session)

        # Connect to SSE stream
        received_data = []
        start_time = datetime.utcnow()

        async with client_session.get(
            f"{API_BASE}/threads/{thread_id}/stream",
            headers={'Accept': 'text/event-stream'}
        ) as resp:
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'text/event-stream'

            async for line in resp.content:
                if line.startswith(b'data: '):
                    data = json.loads(line[6:].decode('utf-8'))
                    received_data.append(data)

                    # Check if we got agent response
                    if data.get('agent') == 'ResearchAgent':
                        break

                # Timeout after 5 seconds
                if (datetime.utcnow() - start_time).seconds > 5:
                    break

        assert len(received_data) > 0, "No data received from SSE stream"
        assert any(d.get('agent') == 'ResearchAgent' for d in received_data)

    @pytest.mark.asyncio
    async def test_message_routing(self, client_session):
        """Messages should route correctly based on prefix"""
        thread_id = await self.test_spawn_research_agent(client_session)

        # Test direct routing with @prefix
        msg_payload = {
            "content": "@ResearchAgent please explain stewart platforms",
            "metadata": {"test": True}
        }

        async with client_session.post(
            f"{API_BASE}/threads/{thread_id}/messages",
            json=msg_payload
        ) as resp:
            assert resp.status == 200

    @pytest.mark.asyncio
    async def test_orchestrator_command(self, client_session):
        """Orchestrator commands should be accepted"""
        cmd_payload = {
            "action": "dump_state"
        }

        async with client_session.post(
            f"{API_BASE}/orchestrator/command",
            json=cmd_payload
        ) as resp:
            assert resp.status in [200, 202]

@pytest.mark.asyncio
async def test_full_conversation_flow():
    """Integration test: Full conversation flow"""
    async with aiohttp.ClientSession() as session:
        # 1. Spawn OrchestratorAgent
        resp = await session.post(
            f"{API_BASE}/agents/OrchestratorAgent/threads",
            json={"initial_prompt": "Initialize new robot build session"}
        )
        data = await resp.json()
        thread_id = data['thread_id']

        # 2. Send a message requiring multiple agents
        await session.post(
            f"{API_BASE}/threads/{thread_id}/messages",
            json={"content": "I need help with the E-stop implementation"}
        )

        # 3. Verify orchestrator routes to SafetyEngineer
        # This would need SSE monitoring in real test

        await asyncio.sleep(2)  # Allow processing

        # 4. Check thread is active
        # Would need status endpoint

        print(f"✓ Full flow test passed with thread {thread_id}")
```

If a2-agents/tests/conftest.py does NOT exist, create it:
```python
import pytest
import asyncio
import os

# Configure event loop
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Wait for services to be ready
@pytest.fixture(scope="session", autouse=True)
async def wait_for_services():
    import aiohttp
    import asyncio

    async def check_health():
        async with aiohttp.ClientSession() as session:
            for _ in range(30):  # 30 second timeout
                try:
                    async with session.get(f"{os.getenv('API_GATEWAY_URL', 'http://localhost:8080')}/health") as resp:
                        if resp.status == 200:
                            return True
                except:
                    pass
                await asyncio.sleep(1)
        return False

    if not await check_health():
        pytest.fail("Services did not become healthy in time")
```

And a2-agents/tests/Dockerfile.test:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.test.txt .
RUN pip install -r requirements.test.txt

CMD ["pytest", "-v", "--tb=short", "tests/"]
```

a2-agents/tests/requirements.test.txt:
- pytest==7.4.4
- pytest-asyncio==0.23.3
- aiohttp==3.9.1

Only create these files if they don't already exist.
DO NOT DELETE OR OVERWRITE EXISTING TEST FILES.
```

## 10-git-init-safe.txt
```
**CRITICAL: COMMIT ALL EXISTING WORK BEFORE ANY GIT OPERATIONS**

First, check git status and commit any uncommitted work:

```bash
cd /Users/aaronlax/Projects/A2
git status

# If there are uncommitted changes:
git add -A
git commit -m "WIP: Save all existing work before a2-agents git setup"

# Change to a2-agents directory
cd a2-agents
```

Then initialize git repository safely:

```bash
# Only init if not already a git repo
if [ ! -d .git ]; then
    git init
fi

# Add remote only if not already added
if ! git remote | grep -q origin; then
    git remote add origin https://github.com/War-Against-Work/thread-safe-agents
fi

# Update .gitignore (append, don't overwrite)
cat >> .gitignore << 'EOF'
# Environment
.env
.env.local
*.env

# Python
__pycache__/
*.py[cod]
venv/
env/

# Docker
docker-compose.override.yaml

# IDE
.vscode/
.idea/
*.swp
.DS_Store

# Logs
*.log
logs/

# Frontend (preserve frontend but ignore build artifacts)
frontend/node_modules/
frontend/build/
frontend/dist/
frontend/.env.local
EOF

# Only create files if they don't exist
[ ! -f README.md ] && cat > README.md << 'EOF'
# A2-Agents: Thread-Safe Multi-Agent Backend

Microservices backend for orchestrating Claude-powered agents working on the A2 robot project.

## Architecture

See [REFERENCE.md](REFERENCE.md) for complete system documentation.

## Quick Start

1. Copy environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. Start services:
   ```bash
   make setup
   make up
   ```

3. Check health:
   ```bash
   curl http://localhost:8080/health
   ```

## Services

- **API Gateway** (8080): REST/SSE interface
- **Orchestrator Logic**: Message routing and memory
- **Agent Manager**: Claude instance lifecycle
- **Repo Proxy** (7000): Git operations with ACL
- **CI Trigger**: GitHub Actions integration

## Development

```bash
make logs          # View all logs
make shell-api     # Shell into API container
make test          # Run tests
make down          # Stop everything
```

## License

MIT - See [LICENSE](LICENSE)
EOF

[ ! -f LICENSE ] && cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 War Against Work

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

[ ! -f CONTRIBUTING.md ] && cat > CONTRIBUTING.md << 'EOF'
# Contributing to A2-Agents

## Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Code Style

- Python: Follow PEP 8
- Use type hints where possible
- Add docstrings to all functions
- Keep functions focused and small

## Testing

All new features must include tests. Run the test suite with:

```bash
make test
```

## Commit Messages

Use conventional commits format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
EOF

[ ! -f CODEOWNERS ] && cat > CODEOWNERS << 'EOF'
# Default owners for everything
* @War-Against-Work/core-team

# Service-specific owners
/services/api_gateway/ @War-Against-Work/api-team
/services/orchestrator_logic/ @War-Against-Work/orchestration-team
/services/agent_manager/ @War-Against-Work/ai-team
/services/repo_proxy/ @War-Against-Work/security-team
/services/ci_trigger/ @War-Against-Work/devops-team

# Documentation
/docs/ @War-Against-Work/docs-team
*.md @War-Against-Work/docs-team
EOF

# Stage and commit everything
git add -A
git commit -m "feat: Complete A2-agents backend with frontend integration

- Docker Compose setup for all backend services
- Frontend directory preserved at frontend/
- NATS message bus with SSE streaming
- Redis hot cache + Postgres cold storage
- Agent ACL enforcement via repo-proxy
- Comprehensive test suite
- Full documentation in REFERENCE.md
- Run from parent A2 directory with claude code assistant"

echo "Repository ready. Next steps:"
echo "1. Review commit with: git log --oneline"
echo "2. Create repo on GitHub if needed"
echo "3. Push with: git push -u origin main"
echo ""
echo "Frontend is at: frontend/"
echo "Backend services are in: services/"
echo ""
echo "To run claude code assistant from parent A2 directory:"
echo "cd /Users/aaronlax/Projects/A2"
echo "# Then reference files as a2-agents/services/..."
```
```
