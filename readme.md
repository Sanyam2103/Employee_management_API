# Employee Management API

A FastAPI-based employee management system with JWT authentication and MongoDB.

## Features

- **Employee CRUD operations** (Create, Read, Update, Delete)
- **JWT Authentication** with role-based access control
- **MongoDB** database integration
- **Interactive API documentation** (Swagger UI)

## Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup environment:**
   ```bash
   cp .env.example .env
   # Edit .env file with your MongoDB URL and generate a SECRET_KEY
   ```

3. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access API docs:** http://localhost:8000/docs

## Default Login

- **Username:** `admin`
- **Password:** `admin123`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Employees (Protected)
- `GET /employees` - List employees
- `POST /employees` - Create employee (admin only)
- `DELETE /employees/{id}` - Delete employee (admin only)

## Tech Stack

- FastAPI
- MongoDB
- JWT Authentication
- Pydantic validation
- Bcrypt password hashing

## Usage

1. Login to get access token
2. Use token in Authorization header: `Bearer <token>`
3. Access protected employee endpoints

Built with ❤️ using FastAPI" > README.md
