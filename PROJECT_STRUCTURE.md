# Project Structure Documentation

## Overview

This document explains the structure and organization of the AI Care Call Server project.

## Directory Structure

```
AICareCall-server/
├── main.py                      # FastAPI application entry point
├── database.py                  # Database configuration and session management
├── models.py                    # SQLAlchemy ORM models
├── schemas.py                   # Pydantic schemas for request/response validation
├── init_db.py                   # Database initialization script
├── requirements.txt             # Python package dependencies
├── README.md                    # Project documentation
├── SETUP.md                     # Quick setup guide
├── PROJECT_STRUCTURE.md         # This file
├── AuthKey_5XFZZ6ZD2H.p8       # Apple APNs authentication key (private)
└── routers/                     # API route handlers
    ├── __init__.py             # Package initialization
    ├── push.py                 # Push notification endpoints
    └── register_callee.py      # Callee management endpoints
```

## File Purposes

### Core Application Files

#### `main.py`
- FastAPI application initialization
- Router registration
- Health check endpoint

#### `database.py`
- SQLAlchemy engine configuration
- Database connection string management
- SessionLocal factory for database sessions
- Base class for ORM models
- `get_db()` dependency function for route handlers

#### `models.py`
- SQLAlchemy ORM models
- Database table definitions
- Currently defines:
  - `Callee`: Stores callee information and preferences

#### `schemas.py`
- Pydantic models for request/response validation
- Type validation and serialization
- API documentation examples
- Currently defines:
  - `RegisterCalleeRequest`: Input validation for callee registration
  - `CalleeResponse`: Response format for callee data

#### `init_db.py`
- Database initialization script
- Creates all tables defined in models.py
- Run once during initial setup

### Router Files

#### `routers/push.py`
Push notification functionality:
- `POST /push` - Send regular push notifications
- `POST /push/voip` - Send VoIP push notifications
- Handles Apple APNs JWT authentication

#### `routers/register_callee.py`
Callee management CRUD operations:
- `POST /register-callee` - Register new callee
- `GET /register-callee/{callee_id}` - Get callee by ID
- `GET /register-callee/token/{voip_token}` - Get callee by device token
- `PUT /register-callee/{callee_id}` - Update callee information
- `DELETE /register-callee/{callee_id}` - Delete callee

## Design Patterns and Conventions

### 1. Router Organization
- Each router file represents a logical grouping of endpoints
- Routers are imported in `main.py`
- File naming: Use lowercase with underscores (e.g., `register_callee.py`)
- Avoid `_router` suffix in filenames

### 2. Database Access Pattern
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db

@router.get("/example")
async def example_endpoint(db: Session = Depends(get_db)):
    # Use db to query database
    result = db.query(Model).filter(...).first()
    return result
```

### 3. Request/Response Models
- Define request models in `schemas.py`
- Use Pydantic for validation
- Define response models with `response_model` parameter
- Use `from_attributes = True` for ORM compatibility

### 4. Error Handling
```python
from fastapi import HTTPException, status

if not found:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Resource not found"
    )
```

### 5. Configuration Management
- Use environment variables for configuration
- Provide defaults for development
- Use `os.getenv()` for reading environment variables
- Example:
```python
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/db")
```

## API Route Structure

### Current Endpoints

```
GET  /                              # Health check
POST /register-callee               # Register callee
GET  /register-callee/{callee_id}  # Get callee by ID
GET  /register-callee/token/{token} # Get callee by token
PUT  /register-callee/{callee_id}  # Update callee
DELETE /register-callee/{callee_id} # Delete callee
POST /push                          # Send push notification
POST /push/voip                     # Send VoIP push
```

### API Documentation
Automatically generated at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Schema

### Callees Table
```sql
CREATE TABLE callees (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR NOT NULL,
    custom_info VARCHAR,
    weekday_preferences INTEGER[],
    time_preferences VARCHAR[],
    voip_device_token VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## Environment Variables

Required:
- `DATABASE_URL`: PostgreSQL connection string

Optional:
- `ENVIRONMENT`: `development` or `production` (default: development)
- `APPLE_TEAM_ID`: Apple developer team ID
- `APPLE_KEY_ID`: APNs authentication key ID
- `BUNDLE_ID`: iOS app bundle identifier
- `P8_KEY_PATH`: Path to APNs .p8 key file

## Dependencies

Core:
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `sqlalchemy`: ORM
- `psycopg2-binary`: PostgreSQL adapter
- `pydantic`: Data validation

Features:
- `pyjwt`: JWT token generation for APNs
- `httpx`: HTTP client for APNs requests
- `python-dotenv`: Environment variable management

## Development Workflow

1. **Make changes** to routers or models
2. **Update database** if models changed:
   ```bash
   python init_db.py
   ```
3. **Test locally** with auto-reload:
   ```bash
   uvicorn main:app --reload
   ```
4. **Check API docs** at http://localhost:8000/docs
5. **Test endpoints** using curl or Swagger UI

## Best Practices

### ✅ Do:
- Use dependency injection for database sessions
- Validate input with Pydantic models
- Use proper HTTP status codes
- Add docstrings to endpoints
- Use environment variables for configuration
- Follow snake_case for Python files and variables
- Use kebab-case for URL paths

### ❌ Don't:
- Hardcode credentials or tokens
- Use hyphens in Python file names
- Skip error handling
- Leave database connections open
- Commit sensitive files (.env, .p8 keys)

## Future Enhancements

Potential additions:
- [ ] Authentication and authorization (JWT tokens)
- [ ] Database migrations (Alembic)
- [ ] Logging and monitoring
- [ ] Rate limiting
- [ ] Caching layer (Redis)
- [ ] API versioning
- [ ] Call scheduling system
- [ ] Analytics and reporting endpoints

## Deployment Considerations

### Database
- Use connection pooling in production
- Set up regular backups
- Configure appropriate indexes
- Use database migrations for schema changes

### Application
- Use Gunicorn with Uvicorn workers
- Set appropriate worker count (CPU cores × 2 + 1)
- Configure logging
- Use environment-specific settings
- Set up health check monitoring

### Security
- Keep .p8 keys secure and never commit
- Use secrets manager for production credentials
- Enable HTTPS
- Implement rate limiting
- Add authentication/authorization as needed

