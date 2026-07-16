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

## Project Structure

```text
web_practice3/
├── accounts/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
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

## Installed Packages

The main packages used in this project are:

```text
django
djangorestframework
djangorestframework-simplejwt
drf-spectacular
django-filter
pillow
```

---

## Run Project

Before running the server, make sure the virtual environment is activated.

First, check the Django project:

```powershell
python manage.py check
```

If there are no errors, run the development server:

```powershell
python manage.py runserver
```

The project will be available at:

```text
http://127.0.0.1:8000/
```

---

## API Health Check

A simple health check endpoint is available to make sure Django and DRF are configured correctly.

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

## Current Phase

The project is currently in:

```text
Phase 0 - Initial Django/DRF Project Setup
```

In this phase, the following items are configured:

- Django project structure
- Django REST Framework
- JWT authentication settings
- Swagger documentation settings
- SQLite database setting
- Basic health check endpoint
- Initial project README
- Initial `.gitignore` rules for this practice

---

## Important Note About Migrations

Migrations are intentionally not executed in Phase 0.

Reason:

A custom user model will be added in Phase 1. It is better to define the custom user model before running the first migration, because changing the user model after migrations can cause unnecessary problems.

So in Phase 0, do not run:

```powershell
python manage.py migrate
```

Migration commands will be executed after the custom user model is created in Phase 1.

---

## Database

This project uses SQLite as required by the assignment.

The default database file will be:

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

### Run development server

```powershell
python manage.py runserver
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

## Phase 0 Checklist

Before moving to Phase 1, the following items must be completed:

- [ ] `web_practice3` folder is created
- [ ] virtual environment is created
- [ ] virtual environment is ignored by git
- [ ] Django is installed
- [ ] Django REST Framework is installed
- [ ] SimpleJWT is installed
- [ ] drf-spectacular is installed
- [ ] django-filter is installed
- [ ] Pillow is installed
- [ ] Django project `config` is created
- [ ] apps `core`, `accounts`, `chats`, and `subscriptions` are created
- [ ] `settings.py` is configured
- [ ] `urls.py` is configured
- [ ] health check endpoint is added
- [ ] Swagger endpoints are added
- [ ] `requirements.txt` is created
- [ ] `.env.example` is created
- [ ] `README.md` is created
- [ ] `python manage.py check` runs successfully
- [ ] `python manage.py runserver` runs successfully
- [ ] `/api/health/` works correctly
- [ ] `/api/docs/` opens Swagger correctly
- [ ] no unnecessary files are tracked by git
- [ ] Phase 0 is committed and pushed to git

---

## Next Phase

The next phase is:

```text
Phase 1 - Database Models and Relationships
```

In Phase 1, the main database models will be implemented:

- Custom User
- Project
- AIModel
- Assistant
- Conversation
- Message
- Attachment
- SubscriptionPlan
- LinkedAccount

After the custom user model is created, migrations will be generated and applied.