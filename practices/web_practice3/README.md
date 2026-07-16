# Web Practice 3 - ChatGPT Backend

This project is a Django REST Framework backend for a ChatGPT-like application.

The goal of this project is to implement the backend of a simplified ChatGPT-style system using Django, Django REST Framework, JWT authentication, SQLite database, Swagger documentation, and proper RESTful API design.

---

## Project Information

- Course: Web Programming
- Assignment: Web Practice 3
- Topic: ChatGPT-like Backend
- Framework: Django + Django REST Framework
- Database: SQLite
- Authentication: JWT
- API Documentation: Swagger using drf-spectacular

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
- Initial README
- Initial `.gitignore` rules

### Phase 1 - Database Models and Relationships

Implemented models:

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
- Swagger examples for authentication APIs

### Phase 3 - Permissions and Data Isolation

Implemented:

- Reusable object-level permission classes
- Owner-based permission helpers
- Admin-or-read-only permission for AI models
- Assistant permission rules for public and private assistants
- QuerySet mixins for user-owned resources
- QuerySet mixins for public-or-owned assistants
- Soft delete mixin for conversations and messages
- Nested conversation/project filtering helpers
- Ownership helper methods on models
- Data isolation tests

### Phase 4 - CRUD APIs for Main Resources

Implemented:

- Project CRUD API
- AI Model CRUD API with admin-only write access
- Assistant CRUD API with public/private access rules
- Conversation CRUD API with soft delete
- Project conversations endpoint
- Swagger documentation for main resources
- API tests for CRUD and data isolation

### Phase 5 - AI Models and Initial Data Seeding

Implemented:

- `seed_initial_data` management command
- Default AI models
- Default public assistants
- Default subscription plans
- Idempotent initial data creation
- AI model availability flag in API response
- Tests for initial data seeding

### Phase 6 - Assistant Improvements and Conversation Assistant Selection

Implemented:

- Assistant availability flag for current user
- Assistant modification permission flag for current user
- Public assistants endpoint
- Current user's private assistants endpoint
- Conversation assistant selection endpoint
- Conversation assistant clearing support
- Validation against selecting another user's private assistant
- Tests for assistant selection and access rules

---

## Project Structure

```text
web_practice3/
├── accounts/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── chats/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── config/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── core/
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── seed_initial_data.py
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── mixins.py
│   ├── models.py
│   ├── permissions.py
│   ├── test_seed_initial_data.py
│   ├── tests.py
│   └── views.py
│
├── subscriptions/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── media/
├── static/
├── templates/
├── .env.example
├── manage.py
├── README.md
└── requirements.txt
```

---

## Setup on Windows

### 1. Go to the project directory

```powershell
cd practices\web_practice3
```

### 2. Create a virtual environment

```powershell
py -m venv .venv
```

### 3. Activate the virtual environment

If you are using PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If you are using CMD:

```cmd
.\.venv\Scripts\activate.bat
```

### 4. Install dependencies

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

## Initial Data Seeding

To create default AI models, public assistants, and subscription plans, run:

```powershell
python manage.py seed_initial_data
```

This command is idempotent, so it can be executed multiple times without creating duplicate records.

It creates default AI models:

```text
GPT-3.5
GPT-4
Claude-3
Llama-3
```

It creates default public assistants:

```text
General Assistant
Coding Assistant
Translator Assistant
Academic Writing Assistant
Literary Critic
```

It creates default subscription plans:

```text
Free Plan
Premium Monthly
Premium Yearly
```

---

## Swagger Documentation

Swagger documentation:

```text
http://127.0.0.1:8000/api/docs/
```

OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

ReDoc documentation:

```text
http://127.0.0.1:8000/api/redoc/
```

---

## Health Check

```http
GET /api/health/
```

Expected response:

```json
{
  "status": "ok",
  "project": "web_practice3",
  "phase": "0",
  "message": "Django and DRF are configured successfully."
}
```

---

## Authentication APIs

### Register

```http
POST /api/auth/register/
```

### Login

```http
POST /api/auth/login/
```

### Refresh Token

```http
POST /api/auth/token/refresh/
```

### Get Profile

```http
GET /api/auth/profile/
```

### Update Profile

```http
PATCH /api/auth/profile/
```

Protected endpoints require this header:

```text
Authorization: Bearer <access_token>
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

### Assistants

```http
GET     /api/assistants/
POST    /api/assistants/
GET     /api/assistants/<id>/
PATCH   /api/assistants/<id>/
DELETE  /api/assistants/<id>/
```

### Assistant Helper Endpoints

```http
GET /api/assistants/public/
GET /api/assistants/mine/
```

### Conversations

```http
GET     /api/conversations/
POST    /api/conversations/
GET     /api/conversations/<id>/
PATCH   /api/conversations/<id>/
DELETE  /api/conversations/<id>/
```

### Conversation Assistant Selection

```http
PATCH /api/conversations/<conversation_id>/assistant/
```

Select assistant:

```json
{
  "assistant": 1
}
```

Clear assistant:

```json
{
  "assistant": null
}
```

### Project Conversations

```http
GET /api/projects/<project_id>/conversations/
```

---

## Permission and Data Isolation Design

Main rules:

- Users can only access their own projects.
- Users can only access their own conversations.
- Users can only access messages inside their own conversations.
- Users can only access attachments inside their own messages.
- Private assistants are only available to their owner.
- Public assistants are readable by authenticated users.
- Public assistants can only be modified by admin users.
- AI models are readable by authenticated users.
- AI models can only be modified by admin users.
- Conversations are soft-deleted by changing their status to `deleted`.
- Users cannot select another user's private assistant for a conversation.
- Users can select public assistants for their own conversations.
- Users can clear the assistant of their own conversations.

Main files:

```text
core/permissions.py
core/mixins.py
```

---

## Database

This project uses SQLite as required by the assignment.

The default database file is:

```text
db.sqlite3
```

This file is ignored by git and should not be pushed to the repository.

---

## Git Ignore Notes

The following files and folders should not be committed:

- `.venv/`
- `venv/`
- `env/`
- `__pycache__/`
- `.env`
- `.env.*`
- `db.sqlite3`
- `media/`
- `staticfiles/`
- cache files
- coverage files
- local IDE files

However, the following files should be committed:

- source code files
- app folders
- migration files
- management commands
- `requirements.txt`
- `README.md`
- `.env.example`

---

## Useful Commands

### Check Django project

```powershell
python manage.py check
```

### Create migrations

```powershell
python manage.py makemigrations
```

### Apply migrations

```powershell
python manage.py migrate
```

### Seed initial data

```powershell
python manage.py seed_initial_data
```

### Run development server

```powershell
python manage.py runserver
```

### Create superuser

```powershell
python manage.py createsuperuser
```

### Run all tests

```powershell
python manage.py test
```

### Run Phase 3 tests

```powershell
python manage.py test core
```

### Run Phase 4 tests

```powershell
python manage.py test chats
```

### Run Phase 5 seed tests

```powershell
python manage.py test core.test_seed_initial_data
```

### Run Phase 6 assistant tests

```powershell
python manage.py test chats.Phase6AssistantSelectionTests
```

---

## Phase 6 Checklist

Before moving to the next phase, the following items must be completed:

- [ ] `AssistantSerializer` includes `is_available_for_current_user`
- [ ] `AssistantSerializer` includes `can_modify_current_user`
- [ ] `GET /api/assistants/public/` works
- [ ] `GET /api/assistants/mine/` works
- [ ] `PATCH /api/conversations/<id>/assistant/` works
- [ ] users can select public assistants
- [ ] users can select their own private assistants
- [ ] users cannot select another user's private assistant
- [ ] users can clear assistant from their own conversation
- [ ] users cannot change assistant of another user's conversation
- [ ] Swagger shows new endpoints
- [ ] `python manage.py check` runs successfully
- [ ] `python manage.py test chats.Phase6AssistantSelectionTests` runs successfully
- [ ] Phase 6 is committed and pushed to git

---

## Next Phase

The next phase is:

```text
Phase 7 - Conversation Messages and Mock AI Responses
```

In Phase 7, message sending, conversation history, and mock AI responses will be implemented.