# NesPrep - Shift Planning System

An AI-powered shift planning system for Israeli businesses. Managers chat in Hebrew to set employee constraints, and the system automatically generates optimized shift schedules in Excel format.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) (Python package manager)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd nesprep

# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend && npm install && cd ..

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys (ANTHROPIC_API_KEY, etc.)
```

### Running the Application

```bash
# Start both backend and frontend
make run
```

This starts:
- **Backend**: http://localhost:8000 (FastAPI)
- **Frontend**: http://localhost:5173 (Vite/React)

Open the frontend URL in your browser to start chatting with the shift planning assistant.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend API    │────▶│   AI Agents     │
│   (React)       │◀────│   (FastAPI)      │◀────│   (LangChain)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
                                                 ┌───────────────┐
                                                 │  CSV Tools    │
                                                 │  Excel Output │
                                                 └───────────────┘
```

### Key Components

| Component | Location | Description |
|-----------|----------|-------------|
| Planning Chat Agent | `app/agents/planning_chat.py` | Conversational agent for collecting constraints |
| Shift Planner Agent | `app/agents/shift_planner.py` | Creates shift assignments |
| CSV Tools | `app/tools/csv_tools.py` | Template generation and Excel conversion |
| CSV Generator | `app/utils/csv_template_generator.py` | Date calculation and CSV structure |

## Testing

### Test CSV Template Generation

```bash
# Run the template generator tests
uv run python scripts/test_csv_generator.py
```

This tests:
- Week calculation for different months
- Date alignment (Sunday-Saturday weeks)
- CSV structure generation

### Test CSV Tools Manually

```python
# In Python REPL or script
uv run python -c "
from app.tools.csv_tools import CSVTools

# Create tools instance
tools = CSVTools(shift_plan_id=1, output_dir='output')
tool_list = tools.get_tools()

# Get tools by name
generate_template = next(t for t in tool_list if t.name == 'generate_template')
assign_shift = next(t for t in tool_list if t.name == 'assign_shift')
convert_to_excel = next(t for t in tool_list if t.name == 'convert_to_excel')

# Generate template for a specific month
print(generate_template.invoke({'year': 2026, 'month': 4}))

# Add test assignments
print(assign_shift.invoke({
    'employee_name': 'דניאל',
    'day_date': '1.4',
    'shift_type': 'בוקר'
}))

# Convert to Excel
print(convert_to_excel.invoke({}))
"
```

### Test Full Planning Flow

```bash
# Start the application
make run

# Open browser to http://localhost:5173
# Chat with the assistant in Hebrew, e.g.:
# "תכין לי סידור לאפריל 2026"
# "העובדים שלי: דניאל, שני, תהל"
# "דניאל לא יכול בימי שני וחמישי"
# "תייצר את הסידור"
```

## CSV Template Structure

Each month's template contains week blocks (27 rows each):

```
Row 0:  Week date range title (e.g., "29/3-4/4/2026")
Row 1:  אירועי השבוע (weekly events)
Row 2:  משימות שבועיות (weekly tasks)
Row 3:  הטבות (benefits)
Row 4:  Day headers (ראשון, שני, שלישי, רביעי, חמישי, שישי, שבת)
Row 5:  תאריך row with dates (e.g., 29.3, 30.3, 31.3, 1.4, 2.4, 3.4, 4.4)
Row 6:  Empty
Rows 7-11:  Morning shifts (בוקר) - 09:00-18:00
Rows 12-14: Afternoon shifts (צהריים) - 10:00-19:00, 11:00-20:00, 12:00-21:00
Row 15: Empty
Rows 16-21: Evening shifts (ערב) - 13:00-22:00
Rows 22-27: Notes, training, padding
```

### Date Format

Dates use "D.M" format (e.g., "1.4" for April 1st).

### Shift Types

| Hebrew | English | Time |
|--------|---------|------|
| בוקר | Morning | 09:00-18:00 |
| צהריים | Afternoon | 10:00-19:00, 11:00-20:00, 12:00-21:00 |
| ערב | Evening | 13:00-22:00 |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sessions` | GET | List chat sessions |
| `/api/sessions` | POST | Create new session |
| `/api/sessions/{id}/messages` | GET | Get session messages |
| `/ws` | WebSocket | Real-time chat |

## Configuration

Environment variables (`.env`):

```bash
ANTHROPIC_API_KEY=sk-ant-...     # Required for Claude AI
DATABASE_URL=sqlite:///data.db   # Database connection
TEMPLATE_PATH=templates/shift_template.xlsx  # Excel template
OUTPUT_DIR=output                # Generated files directory
```

## File Structure

```
nesprep/
├── app/
│   ├── agents/           # AI agents
│   │   ├── planning_chat.py
│   │   ├── shift_planner.py
│   │   └── validator.py
│   ├── api/              # FastAPI routes
│   ├── dal/              # Database models
│   ├── prompts/          # System prompts
│   ├── tools/            # Agent tools
│   │   ├── csv_tools.py
│   │   ├── planning_chat_tools.py
│   │   └── constraint_tools.py
│   └── utils/            # Utilities
│       └── csv_template_generator.py
├── frontend/             # React frontend
├── templates/            # Excel template
├── output/               # Generated shift plans
├── scripts/              # Test scripts
└── .cursor/rules/        # Cursor AI rules
```

## Development

### Adding New Tools

Tools follow the `get_tools()` pattern with closure capture:

```python
class MyTools:
    def __init__(self, some_id: int):
        self.some_id = some_id
    
    def get_tools(self) -> list:
        tools_self = self  # Closure capture
        
        @tool
        def my_tool(arg: str) -> str:
            """Tool description."""
            # Access instance via tools_self
            return f"Result for {tools_self.some_id}: {arg}"
        
        return [my_tool]
```

### Modifying the Excel Template

1. Edit `templates/shift_template.xlsx` in Excel
2. Keep the structure (27 rows per week block)
3. The system will copy this template and fill in dates/assignments

### Running Tests

```bash
# Template generation tests
uv run python scripts/test_csv_generator.py

# Linting
uv run ruff check .

# Type checking
uv run mypy app/
```

## Troubleshooting

### "Template not found" Error

Ensure `templates/shift_template.xlsx` exists:
```bash
ls -la templates/
```

### Dates Not Aligned

The system calculates weeks Sunday-Saturday (Israeli work week). Verify with:
```python
from datetime import date
d = date(2026, 4, 1)
print(f"April 1, 2026 is a {d.strftime('%A')}")
```

### Excel Formatting Issues

The system copies the template file exactly. If formatting is wrong, check the source template.

## License

[Your License]
