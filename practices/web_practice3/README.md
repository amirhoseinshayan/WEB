# Web Practice 3 - ChatGPT Backend

This project is a Django REST Framework backend for a ChatGPT-like application.

The goal of this project is to implement the backend of a simplified ChatGPT-style system using Django, Django REST Framework, JWT authentication, SQLite database, Swagger documentation, and proper RESTful API design.

---

## Tech Stack

- Python
- Django
- Django REST Framework
- SQLite
- JWT Authentication
- djangorestframework-simplejwt
- drf-spectacular
- django-filter
- Pillow

---

## Implemented Phases

### Phase 0 - Initial Project Setup

Implemented:

- Django project structure
- Django REST Framework setup
- JWT settings
- Swagger settings
- SQLite database configuration
- Health check endpoint

### Phase 1 - Database Models and Relationships

Implemented:

- Custom User
- LinkedAccount
- SubscriptionPlan
- Project
- AIModel
- Assistant
- Conversation
- Message
- Attachment

### Phase 2 - Authentication and User Profile

Implemented:

- User registration
- Login with username or email
- JWT access and refresh tokens
- Token refresh endpoint
- Authenticated user profile endpoint
- Profile update endpoint

### Phase 3 - Permissions and Data Isolation

Implemented:

- Reusable permission classes
- Owner-based access checks
- QuerySet mixins
- Soft delete helpers
- Data isolation tests

### Phase 4 - CRUD APIs for Main Resources

Implemented:

- Project CRUD API
- AI Model CRUD API with admin-only write access
- Assistant CRUD API
- Conversation CRUD API
- Project conversations endpoint

### Phase 5 - AI Models and Initial Data Seeding

Implemented:

- `seed_initial_data` command
- Default AI models
- Default public assistants
- Default subscription plans
- AI model availability flag

### Phase 6 - Assistant Improvements and Conversation Assistant Selection

Implemented:

- Public assistants endpoint
- Current user's private assistants endpoint
- Assistant availability flags
- Conversation assistant selection endpoint

### Phase 7 - Conversation Messages and Mock AI Responses

Implemented:

- Conversation message history endpoint
- Send message endpoint
- Mock assistant response generation
- User message storage
- Assistant message storage
- Message list/retrieve API
- User message edit API
- Message soft delete API
- Message access isolation tests

### Phase 8 - Subscription System and Free User Limits

Implemented:

- Subscription status endpoint
- Subscription plans endpoint
- Simulated subscription purchase endpoint
- Free and Premium subscription behavior
- Daily message limit for Free users
- Unlimited messages for Premium users
- Premium model restriction for Free users
- Premium model access for Premium users
- Subscription tests

---

## Setup on Windows

```powershell
cd practices\web_practice3
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

For CMD:

```cmd
.\.venv\Scripts\activate.bat
```

---

## Run Project

```powershell
python manage.py check
python manage.py migrate
python manage.py seed_initial_data
python manage.py runserver
```

Project URL:

```text
http://127.0.0.1:8000/
```

---

## Swagger Documentation

```text
http://127.0.0.1:8000/api/docs/
```

OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

ReDoc:

```text
http://127.0.0.1:8000/api/redoc/
```

---

## Authentication APIs

```http
POST  /api/auth/register/
POST  /api/auth/login/
POST  /api/auth/token/refresh/
GET   /api/auth/profile/
PATCH /api/auth/profile/
```

Protected endpoints require:

```text
Authorization: Bearer <access_token>
```

---

## Subscription APIs

### Get Subscription Status

```http
GET /api/subscription/status/
```

Example response for Free user:

```json
{
  "subscription_type": "free",
  "plan_name": "Free Plan",
  "is_premium": false,
  "premium_until": null,
  "daily_message_limit": 50,
  "daily_messages_used": 0,
  "daily_messages_remaining": 50,
  "can_use_premium_models": false,
  "can_upload_files": false
}
```

Example response for Premium user:

```json
{
  "subscription_type": "premium",
  "plan_name": "Premium Monthly",
  "is_premium": true,
  "premium_until": "2026-08-16T10:00:00Z",
  "daily_message_limit": null,
  "daily_messages_used": 12,
  "daily_messages_remaining": null,
  "can_use_premium_models": true,
  "can_upload_files": true
}
```

### List Subscription Plans

```http
GET /api/subscription/plans/
```

### Purchase or Switch Plan

```http
POST /api/subscription/purchase/
```

Request:

```json
{
  "plan_id": 2
}
```

---

## Main CRUD APIs

### Projects

```http
GET     /api/projects/
POST    /api/projects/
GET     /api/projects/<id>/
PATCH   /api/projects/<id>/
DELETE  /api/projects/<id>/
```

### AI Models

```http
GET     /api/models/
POST    /api/models/          admin only
GET     /api/models/<id>/
PATCH   /api/models/<id>/     admin only
DELETE  /api/models/<id>/     admin only
```

Free users can only use non-premium models.

Premium users can use both free and premium models.

### Assistants

```http
GET     /api/assistants/
POST    /api/assistants/
GET     /api/assistants/<id>/
PATCH   /api/assistants/<id>/
DELETE  /api/assistants/<id>/
GET     /api/assistants/public/
GET     /api/assistants/mine/
```

### Conversations

```http
GET     /api/conversations/
POST    /api/conversations/
GET     /api/conversations/<id>/
PATCH   /api/conversations/<id>/
DELETE  /api/conversations/<id>/
PATCH   /api/conversations/<id>/assistant/
```

### Conversation Messages

```http
GET  /api/conversations/<conversation_id>/messages/
POST /api/conversations/<conversation_id>/messages/
```

Send message request:

```json
{
  "content": "Hello, explain Django REST Framework shortly."
}
```

Free users have a daily message limit.

Premium users have unlimited daily messages.

### Messages

```http
GET     /api/messages/
GET     /api/messages/<message_id>/
PATCH   /api/messages/<message_id>/
DELETE  /api/messages/<message_id>/
```

---

## Initial Data Seeding

```powershell
python manage.py seed_initial_data
```

Creates:

```text
GPT-3.5
GPT-4
Claude-3
Llama-3
General Assistant
Coding Assistant
Translator Assistant
Academic Writing Assistant
Literary Critic
Free Plan
Premium Monthly
Premium Yearly
```

---

## Useful Commands

### Check project

```powershell
python manage.py check
```

### Check migrations

```powershell
python manage.py makemigrations --check --dry-run
```

### Run all tests

```powershell
python manage.py test
```

### Run Phase 8 tests

```powershell
python manage.py test subscriptions
```

### Run chats tests

```powershell
python manage.py test chats
```

---

## Phase 8 Checklist

- [ ] `subscriptions/services.py` is created
- [ ] `subscriptions/serializers.py` is created
- [ ] `subscriptions/views.py` is implemented
- [ ] `subscriptions/urls.py` is created
- [ ] `config/urls.py` includes subscription routes
- [ ] `GET /api/subscription/status/` works
- [ ] `GET /api/subscription/plans/` works
- [ ] `POST /api/subscription/purchase/` works
- [ ] Free users have daily message limits
- [ ] Premium users have unlimited messages
- [ ] Free users cannot use premium models
- [ ] Premium users can use premium models
- [ ] Swagger shows Subscription endpoints
- [ ] `python manage.py test subscriptions` passes

---

## Next Phase

```text
Phase 9 - Linked Accounts and Account Switching
```