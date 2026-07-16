# Web Practice 3 - ChatGPT Backend

This project is a Django REST Framework backend for a ChatGPT-like application.

The goal of this project is to implement the backend of a simplified ChatGPT-style system using Django, Django REST Framework, JWT authentication, SQLite database, Swagger documentation, proper RESTful API design, tests, and clean project delivery.

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

### Phase 9 - Linked Accounts and Account Switching

Implemented:

- Linked account list endpoint
- Linked account creation endpoint
- Linked account retrieve endpoint
- Linked account delete endpoint
- Account switching endpoint
- JWT token generation for switched account
- Linked account tests

### Phase 10 - File Attachments for Messages

Implemented:

- Attachment upload endpoint for user messages
- Attachment list endpoint for a specific message
- Global attachment list endpoint for current user
- Attachment retrieve endpoint
- Attachment delete endpoint
- Premium-only file upload permission
- File extension validation
- File size validation
- Attachment access isolation tests

### Phase 11 - Final Tests, Cleanup, and Delivery Preparation

Implemented:

- Final validation management command
- Final integration tests
- Delivery guide
- Final README cleanup
- Final test commands
- Final zip creation command
- Delivery checklist

---

## Setup on Windows

Go to the project directory:

```powershell
cd practices\web_practice3
```

Create virtual environment:

```powershell
py -m venv .venv
```

Activate virtual environment in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate virtual environment in CMD:

```cmd
.\.venv\Scripts\activate.bat
```

Install dependencies:

```powershell
pip install -r requirements.txt
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

Swagger UI:

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
POST  /api/auth/switch-account/
```

Protected endpoints require:

```text
Authorization: Bearer <access_token>
```

---

## Linked Account APIs

```http
GET    /api/linked-accounts/
POST   /api/linked-accounts/
GET    /api/linked-accounts/<id>/
DELETE /api/linked-accounts/<id>/
POST   /api/auth/switch-account/
```

---

## Subscription APIs

```http
GET  /api/subscription/status/
GET  /api/subscription/plans/
POST /api/subscription/purchase/
```

Free users have daily message limits.

Premium users have:

- unlimited daily messages
- premium model access
- file upload access

---

## Projects

```http
GET     /api/projects/
POST    /api/projects/
GET     /api/projects/<id>/
PATCH   /api/projects/<id>/
DELETE  /api/projects/<id>/
GET     /api/projects/<project_id>/conversations/
```

---

## AI Models

```http
GET     /api/models/
POST    /api/models/          admin only
GET     /api/models/<id>/
PATCH   /api/models/<id>/     admin only
DELETE  /api/models/<id>/     admin only
```

Free users can only use non-premium models.

Premium users can use both free and premium models.

---

## Assistants

```http
GET     /api/assistants/
POST    /api/assistants/
GET     /api/assistants/<id>/
PATCH   /api/assistants/<id>/
DELETE  /api/assistants/<id>/
GET     /api/assistants/public/
GET     /api/assistants/mine/
```

---

## Conversations

```http
GET     /api/conversations/
POST    /api/conversations/
GET     /api/conversations/<id>/
PATCH   /api/conversations/<id>/
DELETE  /api/conversations/<id>/
PATCH   /api/conversations/<id>/assistant/
```

---

## Conversation Messages

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

Send message response:

```json
{
  "message": "Message sent successfully.",
  "user_message": {
    "id": 1,
    "role": "user",
    "content": "Hello, explain Django REST Framework shortly."
  },
  "assistant_message": {
    "id": 2,
    "role": "assistant",
    "content": "[Mock response from OpenAI GPT-3.5] ..."
  }
}
```

---

## Messages

```http
GET     /api/messages/
GET     /api/messages/<message_id>/
PATCH   /api/messages/<message_id>/
DELETE  /api/messages/<message_id>/
```

Only user messages can be edited.

Deleted messages are soft-deleted.

---

## Attachment APIs

### List attachments of a message

```http
GET /api/messages/<message_id>/attachments/
```

### Upload attachment to a user message

```http
POST /api/messages/<message_id>/attachments/
```

This endpoint requires `multipart/form-data`.

Request field:

```text
file
```

Allowed formats:

```text
txt, pdf, png, jpg, jpeg, webp, csv, md, json, docx
```

Maximum file size:

```text
5 MB
```

Rules:

- Only Premium users can upload files.
- Files can only be attached to user messages.
- Users can only upload files to messages inside their own conversations.
- Files cannot be attached to deleted messages.

### List current user's attachments

```http
GET /api/attachments/
```

### Retrieve attachment

```http
GET /api/attachments/<id>/
```

### Delete attachment

```http
DELETE /api/attachments/<id>/
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

## Final Validation

Run:

```powershell
python manage.py validate_project
```

This command checks:

- Django system check
- pending migrations
- required installed apps
- important settings
- required API routes

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

### Run migrations

```powershell
python manage.py migrate
```

### Seed initial data

```powershell
python manage.py seed_initial_data
```

### Run server

```powershell
python manage.py runserver
```

### Run all tests

```powershell
python manage.py test
```

### Run final integration tests

```powershell
python manage.py test core.test_final_project
```

### Run important app tests

```powershell
python manage.py test accounts chats subscriptions core
```

---

## Final Delivery Checklist

Before delivery:

- [ ] `python manage.py check` passes
- [ ] `python manage.py makemigrations --check --dry-run` shows no changes
- [ ] `python manage.py validate_project` passes
- [ ] `python manage.py test` passes
- [ ] Swagger opens correctly
- [ ] `.venv/` is not included
- [ ] `db.sqlite3` is not included
- [ ] `media/` is not included
- [ ] `__pycache__/` is not included
- [ ] `.env` is not included
- [ ] `.env.example` is included
- [ ] `requirements.txt` is included
- [ ] `README.md` is included
- [ ] `DELIVERY.md` is included

---

## Create Final Zip

Run from repository root:

```cmd
cd C:\Users\SARIR\Desktop\WEB
git archive --format=zip --prefix=web_practice3/ --output=WP-HW3-402170981.zip HEAD:practices/web_practice3
```

This creates a clean zip from tracked files only.

It excludes:

- `.venv/`
- `db.sqlite3`
- `media/`
- cache files
- untracked local files

---

## Final Git Commit

```cmd
git add practices/web_practice3/core/management/commands/validate_project.py practices/web_practice3/core/test_final_project.py practices/web_practice3/DELIVERY.md practices/web_practice3/README.md
git commit -m "chore(web-practice3): finalize project delivery"
git push
```