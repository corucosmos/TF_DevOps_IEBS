# User Registration API with Python, FastAPI and MySQL
## Overview

### A simple yet powerful user registration API built with:
* Python and FastAPI for the backend
* MySQL for database storage
* Docker for containerization

### Features
* User registration with email, password, first name and last name
* Secure password hashing (bcrypt)
* Email format validation
* Ready for multi-frontend consumption (CORS enabled)
* Containerized architecture for easy deployment

### Quick Start
1. Clone the repository:
    ```bash
    git clone https://github.com/corucosmos/TF_DevOps_IEBS.git
    cd TF_DevOps_IEBS
    ```
2. Set up environment variables:
    ```bash
    cp .env.example .env
    ```

3. Build and start the containers:
    ```bash
    docker-compose up --build
    ```
### API Access
* The API will be available at http://localhost:8000
* The Admin Frontend will be available at http://localhost:8501

### API Documentation
* Swagger UI: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc

### Project Structure
```bash
TF_DevOps_IEBS/
 ├── docker-compose.yml           (Docker orchestration)
 ├── .env                         (Environment variables)
 ├── .gitignore                   (Git Ignore Files)
 ├── admin-frontend/
 │         ├── Dockerfile         (Admin Fronted container setup)
 │         ├── requirements.txt   (Python dependencies)
 │         └── app.py             (Application code)
 ├── backend/
 │         ├── Dockerfile         (Backend container setup)
 │         ├── requirements.txt   (Python dependencies)
 │         └── app/               (Application code)
 │                ├── tests/  
 │                │     ├── __init__.py
 │                │     ├── conftest.py     (Pytest application)
 │                │     └── test_models.py  (Test application)
 │                ├── __init__.py
 │                ├── main.py     (FastAPI application)
 │                ├── database.py (MySQL connection)
 │                ├── models.py   (User model)
 │                └── schemas.py  (Pydantic schemas)
 └── mysql/
          └── init.sql            (Database initialization script)
```



### Available Endpoints in TAG V1
Method|Endpoint|Description|Request Body Example
------|--------|-----------|--------------------
POST|/register/|Register a new user|{"email":"user@example.com","password":"securePass123","first_name":"John","last_name":"Doe"}
GET|/users/{email}|	Get user details by email|	-

### Available Endpoints in TAG V2
Method|Endpoint|Description|Request Body Example
------|--------|-----------|--------------------
POST|/login/|Login Admin|curl -X POST "http://localhost:8000/login/" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin@example.com&password=password"
GET|/admin/users/|Get list users|curl -X GET "http://localhost:8000/admin/users/" -H "Authorization: Bearer Token"
POST|/admin/users/|Register a new user| curl -X POST "http://locahost:8000/admin/users/" -H "Authorization: Bearer Token" -H "Content-Type: application/json" -d '{"email": "nuevo@example.com","password": "stringNuevo","first_name": "stringNuevo","last_name": "stringNuevo","is_admin": false}'

