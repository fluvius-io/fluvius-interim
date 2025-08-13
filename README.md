# Fluvius Interim

Fluvius Interim is a workflow management library.

## Overview

This package contains workflow management functionality originally from the riparius package, adapted to work as an independent Python package called `fluvius_interim`.

## Features

- **Workflow Management**: Create, update, and manage workflow instances
- **Step Processing**: Handle workflow steps and their execution
- **Participant Management**: Add and remove workflow participants with roles
- **Event Injection**: Inject external events into running workflows
- **Trigger System**: Send triggers to workflows for external event handling
- **Query System**: Query workflows, steps, participants, and stages
- **FastAPI Integration**: REST API endpoints for workflow operations
- **Domain-Driven Design**: CQRS pattern implementation for workflow commands and queries

## Installation

```bash
pip install fluvius-interim
```

For development:

```bash
pip install fluvius-interim[dev]
```

For testing:

```bash
pip install fluvius-interim[test]
```

## Quick Start

### Basic Workflow Usage

```python
from fluvius_interim import Workflow, WorkflowManager, WorkflowDomain
from fluvius_interim.domain import WorkflowQueryManager

# Create a workflow manager
manager = WorkflowManager()

# Set up domain for CQRS operations
domain = WorkflowDomain()
query_manager = WorkflowQueryManager()
```

### FastAPI Integration

```python
from fastapi import FastAPI
from fluvius.fastapi import (
    create_app,
    configure_authentication,
    configure_domain_manager,
    configure_query_manager
)
from fluvius_interim.domain import WorkflowDomain, WorkflowQueryManager

# Create FastAPI app with workflow domain
app = create_app() \
    | configure_authentication() \
    | configure_domain_manager(WorkflowDomain) \
    | configure_query_manager(WorkflowQueryManager)
```

## API Endpoints

When integrated with FastAPI, the package provides REST endpoints:

### Commands
- `POST /riparius-workflow:create-workflow/workflows/:new` - Create new workflow
- `POST /riparius-workflow:update-workflow/workflows/{id}` - Update workflow
- `POST /riparius-workflow:add-participant/workflows/{id}` - Add participant
- `POST /riparius-workflow:remove-participant/workflows/{id}` - Remove participant
- `POST /riparius-workflow:inject-event/workflows/{id}` - Inject event
- `POST /riparius-workflow:send-trigger/workflows/{id}` - Send trigger
- And more...

### Queries
- `GET /riparius-workflow.workflow/` - List workflows
- `GET /riparius-workflow.workflow-step/~workflow_id={id}/` - List workflow steps
- `GET /riparius-workflow.workflow-participant/~workflow_id={id}/` - List participants
- `GET /riparius-workflow.workflow-stage/~workflow_id={id}/` - List stages

## Development

### Setting up for Development

```bash
git clone https://github.com/adaptive-bits/fluvius-interim.git
cd fluvius-interim
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src tests
ruff check src tests
```

## Architecture

This package follows Domain-Driven Design principles with CQRS (Command Query Responsibility Segregation):

- **Domain Layer**: Core business logic and entities
- **Commands**: Write operations (create, update, delete)
- **Queries**: Read operations with filtering and pagination
- **Aggregates**: Consistency boundaries for workflow operations
- **Events**: Domain events for workflow state changes

## Migration from Riparius

If you're migrating from the original riparius package:

1. Update imports from `riparius` to `fluvius_interim`
2. Update any configuration references
3. Test your workflow definitions and operations

## Requirements

- Python 3.12+
- FastAPI (for web API features)
- SQLAlchemy (for data persistence)
- Pydantic (for data validation)
- And other dependencies listed in pyproject.toml

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker.
