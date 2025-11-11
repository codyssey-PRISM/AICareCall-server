# Quick Setup Guide

Follow these steps to get your AI Care Call server up and running.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)

## Step-by-Step Setup

### 1. Install PostgreSQL (if not already installed)

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create Database

```bash
# Create database
createdb aicarecall

# Or using psql
psql postgres
CREATE DATABASE aicarecall;
\q
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example if available
# cp .env.example .env

# Or create manually
nano .env
```

**Minimum required configuration:**
```env
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/aicarecall
ENVIRONMENT=development
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize Database Tables

```bash
python init_db.py
```

You should see:
```
Creating database tables...
Database tables created successfully!
```

### 6. Run the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Test the API

Open your browser and go to:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/

## Testing the Endpoints

### 1. Register a Callee

```bash
curl -X POST "http://localhost:8000/register-callee" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "김철수",
    "age": 75,
    "gender": "male",
    "custom_info": "요통이 있음",
    "weekday_preferences": [0, 2, 4],
    "time_preferences": ["09:00:00", "14:00:00"],
    "voip_device_token": "test_token_123456"
  }'
```

### 2. Get Callee Information

```bash
# By ID
curl http://localhost:8000/register-callee/1

# By token
curl http://localhost:8000/register-callee/token/test_token_123456
```

### 3. Send VoIP Push Notification

```bash
curl -X POST "http://localhost:8000/push/voip" \
  -H "Content-Type: application/json" \
  -d '{
    "ai_call_id": "call_12345"
  }'
```

## Common Issues

### Database Connection Error

**Error:** `could not connect to server`

**Solution:**
1. Make sure PostgreSQL is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Linux)
2. Check your DATABASE_URL in `.env`
3. Verify database exists: `psql -l`

### Import Errors

**Error:** `No module named 'sqlalchemy'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn main:app --reload --port 8001
```

## Database Management

### View Data

```bash
psql aicarecall

# List all callees
SELECT * FROM callees;

# Exit
\q
```

### Reset Database

```bash
# Drop and recreate database
dropdb aicarecall
createdb aicarecall

# Reinitialize tables
python init_db.py
```

### Backup Database

```bash
pg_dump aicarecall > backup.sql

# Restore
psql aicarecall < backup.sql
```

## Production Deployment

### Environment Variables for Production

```env
DATABASE_URL=postgresql://user:password@production-db-host:5432/aicarecall
ENVIRONMENT=production
APPLE_TEAM_ID=your_team_id
APPLE_KEY_ID=your_key_id
BUNDLE_ID=com.yourcompany.app
```

### Run with Gunicorn (recommended for production)

```bash
pip install gunicorn

gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Next Steps

1. ✅ Server is running
2. ✅ Database is set up
3. 📱 Integrate with iOS app to get real VoIP device tokens
4. 🔐 Add authentication/authorization if needed
5. 📊 Set up logging and monitoring
6. 🚀 Deploy to production (AWS, GCP, etc.)

## Support

For issues or questions, check the main README.md or contact the development team.

