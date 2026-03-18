# NesPrep - AI-Powered Shift Planning System

## What is NesPrep?

An AI-powered shift planning system for Israeli businesses. Managers chat in Hebrew to define employee constraints, and Claude AI agents automatically generate optimized shift schedules as Excel files.

## Tech Stack

- **Backend**: Python 3.13+, FastAPI, Uvicorn, WebSocket, SQLAlchemy (SQLite)
- **Frontend**: React 18, TypeScript, Vite, TailwindCSS, Zustand
- **AI**: Anthropic Claude via AWS Bedrock, LangChain
- **Package Managers**: `uv` (Python), npm (Frontend)

## Running the Project

```bash
make install          # Install all dependencies
make run              # Start backend (port 8000) + frontend (port 5173)
make run-backend      # Backend only
make run-frontend     # Frontend only
make test             # Run pytest
```

Environment variables: copy `.env.example` to `.env` and fill in AWS credentials, JWT secret, etc.

## Project Structure

```
app/
├── agents/                    # AI agent implementations
│   ├── base_agent.py          # BaseAgent + BaseToolCallingAgent
│   ├── planning_chat_agent.py # Conversational chat agent
│   ├── constraint_analyzer.py # Parses Hebrew constraints
│   ├── shift_planner.py       # CSV-based shift assignments
│   ├── json_shift_planner.py  # JSON-based shift planning
│   ├── validator.py           # Validates shift plans
│   └── json_validator.py      # Validates JSON shift plans
├── tools/                     # LangChain tools (get_tools() pattern)
│   ├── log_tools.py           # log_message
│   ├── planning_chat_tools.py # Chat constraint collection
│   ├── constraint_tools.py    # CRUD for constraints
│   ├── csv_tools.py           # CSV/Excel generation
│   └── excel_tools.py         # Excel manipulation
├── prompts/                   # System prompts as constants
├── dal/                       # Data Access Layer (SQLAlchemy)
│   ├── base.py                # Engine, SessionLocal, get_session()
│   └── models/                # Manager, Employee, ShiftPlan, PlanningMessage, EmployeeConstraint
├── api/                       # REST API (FastAPI)
│   ├── main.py                # App entry, CORS, lifespan
│   └── routers/
│       ├── auth.py            # signup, signin, me
│       └── sessions.py        # Shift plan CRUD
├── agent_websocket/           # WebSocket server
│   ├── main.py                # WebSocket FastAPI app
│   ├── routers/websocket.py   # /ws endpoint
│   ├── handlers/
│   │   ├── chat_handler.py    # Handles chat.send
│   │   └── planning_handler.py # Orchestrates planning agents
│   ├── events/event_emitter.py # WebSocket event emission
│   └── consts/                # Event/message type constants
├── auth/                      # JWT + bcrypt auth module
├── utils/                     # CSV template generator, Excel helpers
└── consts/models.py           # Claude model IDs

frontend/src/
├── App.tsx                    # Main app (HomePage or AppContent)
├── components/
│   ├── Home/                  # Landing/auth page
│   ├── Auth/, Login/          # Authentication UI
│   ├── Chat/                  # Chat message display
│   ├── PromptBox/             # Chat input
│   └── SessionPanel/          # Session sidebar
└── shared/
    ├── auth/                  # Zustand auth store + useAuth hook
    ├── websocket/             # WebSocketService singleton
    ├── api/                   # REST client (auth, sessions)
    ├── hooks/                 # useSessions, useChatState
    ├── constants/             # WebSocket constants
    └── utils/                 # cn() utility
```

## Architecture Rules

### Agent Pattern

- Agents extend `BaseAgent` (no tools) or `BaseToolCallingAgent` (with tools)
- Tools are classes with a `get_tools()` method returning `@tool`-decorated functions
- Use closure pattern: `tools_self = self` to capture instance state in tools
- Prompts are string constants in `app/prompts/`
- Model IDs live in `app/consts/models.py`

### Database Rules

- Each tool that accesses the DB **must** create its own session via `get_session()` and close it in a `finally` block
- Never share sessions across async boundaries or tools (LangChain runs tools in a thread pool)
- Dependency direction: `handlers → agents → tools → dal`

### Clean Code Rules

- **Fail fast**: No silent fallbacks with `||` or `??`. Validate and raise errors for missing config
- **No circular dependencies**: Lower-level modules must not import from higher-level ones
- **Single responsibility**: Files under 200-300 lines
- **Explicit error handling**: Log errors, return error strings from tools (don't raise)
- **Only export what's needed** via `__init__.py` and `__all__`
- **Comments explain WHY, not WHAT**

### Naming Conventions

- Classes: `PascalCase` (e.g., `ShiftPlannerAgent`)
- Functions/methods: `snake_case` (e.g., `get_employee_list`)
- Constants: `SCREAMING_SNAKE_CASE` (e.g., `HEBREW_DAYS`)
- Private: underscore prefix (e.g., `_load_constraints`)

### Frontend Rules

- **RTL support is mandatory**: Use logical CSS properties (`ms-`, `me-`, `ps-`, `pe-`, `start-`, `end-`) — never physical (`ml-`, `mr-`, `pl-`, `pr-`, `left-`, `right-`)
- Use `cn()` from `@/shared/utils` for conditional class merging
- Use `useCallback` for handlers passed to children
- Flip directional icons in RTL with `rtl:scale-x-[-1]`
- Path aliases: `@/shared/...`, `@/components/...`
- Auth module exports only `useAuth` hook (internal Zustand store)
- WebSocket is a singleton: `wsService` from `@/shared/websocket`

## Domain Knowledge

### Israeli Work Week

Sunday (ראשון) through Saturday (שבת). Hebrew day abbreviations: א, ב, ג, ד, ה, ו.

### Shift Types

| Hebrew | English | Times | Slots |
|--------|---------|-------|-------|
| בוקר | Morning | 09:00-18:00 | 5 |
| צהריים | Afternoon | 10:00-19:00, 11:00-20:00, 12:00-21:00 | 3 |
| ערב | Evening | 13:00-22:00 | 6 |

### Constraint Types

**Hard** (must satisfy): availability, unavailability, max shifts/hours, rest period (11h default)
**Soft** (preferences): preferred shift types, minimum coverage

### CSV Template

- 27 rows per week block
- Rows 6-10: morning, 11-13: afternoon, 15-20: evening
- Columns 1-7: Sunday through Saturday
- Date format: `D.M` (e.g., "2.3" for March 2nd)

## Agent Workflow

1. Manager chats with PlanningChatAgent to define employees and constraints
2. ConstraintAnalyzerAgent parses Hebrew constraints into structured data
3. ShiftPlannerAgent (or JsonShiftPlannerAgent) generates the schedule
4. ValidatorAgent checks for constraint violations
5. Planner and Validator iterate until plan is valid
6. Final output: formatted Excel file

## WebSocket Events

- `auth.set_token` — authenticate connection
- `session.join` — join/create a planning session
- `chat.send` — send a message to the planning chat
- Server emits: `CHAT_STARTED`, `CHAT_COMPLETED`, `STATUS_UPDATE`, `SESSION_JOINED`, `PLAN_COMPLETED`, `ERROR`

## Adding New Agents

1. Create prompt in `prompts/new_agent_prompts.py`
2. Create tools class in `tools/new_agent_tools.py` (if needed)
3. Create agent in `agents/new_agent.py` extending `BaseToolCallingAgent` or `BaseAgent`
4. Export from `agents/__init__.py`
5. Integrate into planning handler if needed

## Adding New Tools

1. Create tool class in `tools/new_tools.py` with `get_tools()` method
2. Export from `tools/__init__.py`
3. Add to agent: `tools = log_tools.get_tools() + NewTools().get_tools()`
4. Document in the agent's system prompt
