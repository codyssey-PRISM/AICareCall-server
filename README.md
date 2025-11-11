# AI Care Call Server

FastAPI server for managing AI care calls with VoIP push notifications and callee management.

## Features

- 📞 VoIP push notifications via Apple Push Notification Service (APNs)
- 👥 Callee registration and management
- 🗄️ PostgreSQL database integration
- 🔔 Push notification endpoints
- 📱 iOS device token management

## Project Structure

```
.
├── main.py                      # FastAPI application entry point
├── database.py                  # Database configuration and session management
├── models.py                    # SQLAlchemy database models
├── schemas.py                   # Pydantic schemas for validation
├── init_db.py                   # Database initialization script
├── requirements.txt             # Python dependencies
├── routers/
│   ├── push.py                 # Push notification endpoints
│   └── register_callee.py      # Callee management endpoints
└── AuthKey_5XFZZ6ZD2H.p8       # Apple APNs authentication key
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL

Install PostgreSQL if you haven't already:

```bash
# macOS
brew install postgresql
brew services start postgresql

# Create database
createdb aicarecall
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/aicarecall
ENVIRONMENT=development
APPLE_TEAM_ID=U77SWC9NZT
APPLE_KEY_ID=5XFZZ6ZD2H
BUNDLE_ID=com.stevenkim.CallClient
```

### 4. Initialize Database

Run the database initialization script to create tables:

```bash
python init_db.py
```

### 5. Run the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - Health check endpoint

### Callee Management
- `POST /register-callee` - Register a new callee
- `GET /register-callee/{callee_id}` - Get callee by ID
- `GET /register-callee/token/{voip_token}` - Get callee by VoIP token
- `PUT /register-callee/{callee_id}` - Update callee information
- `DELETE /register-callee/{callee_id}` - Delete a callee

### Push Notifications
- `POST /push` - Send regular push notification
- `POST /push/voip` - Send VoIP push notification

## Example API Usage

### Register a Callee

```bash
curl -X POST "http://localhost:8000/register-callee" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "김철수",
    "age": 75,
    "gender": "male",
    "custom_info": "요통이 있음, 매일 아침 산책",
    "weekday_preferences": [0, 2, 4],
    "time_preferences": ["09:00:00", "14:00:00"],
    "voip_device_token": "693e9a147dfb8ebbb5ed31eff419313d4af80607f63255dd673c61b33be1c1d7"
  }'
```

### Send VoIP Push

```bash
curl -X POST "http://localhost:8000/push/voip" \
  -H "Content-Type: application/json" \
  -d '{
    "ai_call_id": "call_123456"
  }'
```

## Database Schema

### Callees Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | String | Callee's name |
| age | Integer | Callee's age |
| gender | String | Callee's gender |
| custom_info | String | Additional information |
| weekday_preferences | Array[Integer] | Preferred weekdays (0=Mon, 6=Sun) |
| time_preferences | Array[String] | Preferred call times (HH:MM:SS) |
| voip_device_token | String | Unique VoIP device token |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Record update timestamp |

## Notes

- VoIP device tokens are unique per device and obtained from iOS app using PushKit
- Device tokens must be registered before sending push notifications
- APNs authentication key (`.p8` file) is required for push notifications
- Weekday preferences: 0=Monday, 1=Tuesday, ..., 6=Sunday

## Development

To run with auto-reload during development:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

