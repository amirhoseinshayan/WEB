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

## Main Features Planned

This project will include the following main features:

- User registration and login
- JWT-based authentication
- User profile management
- User subscription management
- Free and Premium user plans
- AI model selection
- Custom assistants with system prompts
- Conversation management
- Message management
- Mock AI responses
- File upload with chat messages
- Project/workspace management
- Linked accounts and account switching
- RESTful API permissions
- API pagination
- Swagger API documentation
- Backend tests

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
│   ├── tests.py
│   └── views.py
│
├── config/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── core/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
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

After activation, you should see something like this at the beginning of your terminal line:

```text
(.venv)
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## Run Project

Before running the server, make sure the virtual environment is activated.

```powershell
python manage.py check
```

Apply migrations:

```powershell
python manage.py migrate
```

Run the development server:

```powershell
python manage.py runserver
```

The project will be available at:

```text
http://127.0.0.1:8000/
```

---

## API Health Check

```http
GET /api/health/
```

Example URL:

```text
http://127.0.0.1:8000/api/health/
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

Example request:

```json
{
  "username": "amir",
  "email": "amir@example.com",
  "first_name": "Amir",
  "last_name": "Shayan",
  "password": "StrongPass123!",
  "password_confirm": "StrongPass123!"
}
```

### Login

```http
POST /api/auth/login/
```

Login can be done with either username or email.

Example request:

```json
{
  "identifier": "amir",
  "password": "StrongPass123!"
}
```

Example response:

```json
{
  "message": "Login successful.",
  "access": "jwt-access-token",
  "refresh": "jwt-refresh-token",
  "user": {
    "id": 1,
    "username": "amir",
    "email": "amir@example.com",
    "first_name": "Amir",
    "last_name": "Shayan",
    "subscription_type": "free",
    "premium_until": null,
    "is_premium": false,
    "created_at": "2026-01-01T10:00:00Z",
    "updated_at": "2026-01-01T10:00:00Z"
  }
}
```

### Refresh Token

```http
POST /api/auth/token/refresh/
```

Example request:

```json
{
  "refresh": "jwt-refresh-token"
}
```

### Get Profile

```http
GET /api/auth/profile/
```

Required header:

```text
Authorization: Bearer <access_token>
```

### Update Profile

```http
PATCH /api/auth/profile/
```

Required header:

```text
Authorization: Bearer <access_token>
```

Example request:

```json
{
  "first_name": "Amirhosein",
  "last_name": "Shayan",
  "email": "amirhosein@example.com"
}
```

---

## Swagger Documentation

Swagger documentation is available at:

```text
http://127.0.0.1:8000/api/docs/
```

OpenAPI schema is available at:

```text
http://127.0.0.1:8000/api/schema/
```

ReDoc documentation is available at:

```text
http://127.0.0.1:8000/api/redoc/
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

## Environment Variables

An example environment file is provided:

```text
.env.example
```

Example content:

```env
SECRET_KEY=change-this-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

The real `.env` file should not be committed to git.

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
- `requirements.txt`
- `README.md`
- `.env.example`

---

## Useful Commands

### Activate virtual environment in PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Activate virtual environment in CMD

```cmd
.\.venv\Scripts\activate.bat
```

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

### Run development server

```powershell
python manage.py runserver
```

### Create superuser

```powershell
python manage.py createsuperuser
```

### Create requirements file

```powershell
pip freeze > requirements.txt
```

### Install requirements

```powershell
pip install -r requirements.txt
```

---

## Phase 2 Checklist

Before moving to the next phase, the following items must be completed:

- [ ] Register endpoint works correctly
- [ ] Login endpoint works with username
- [ ] Login endpoint works with email
- [ ] JWT access token is returned after login
- [ ] JWT refresh token is returned after login
- [ ] Token refresh endpoint works
- [ ] Profile endpoint requires authentication
- [ ] Profile endpoint returns the current user
- [ ] Profile update endpoint works
- [ ] Duplicate username is rejected
- [ ] Duplicate email is rejected
- [ ] Swagger shows authentication endpoints
- [ ] `python manage.py check` runs successfully
- [ ] Phase 2 is committed and pushed to git

---

## Next Phase

The next phase is:

```text
Phase 3 - Permissions and Data Isolation
```

In Phase 3, object-level permissions and user data isolation will be implemented so users cannot access other users' projects, conversations, messages, or private assistants.