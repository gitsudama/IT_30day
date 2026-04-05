# Day 04 — POST Requests, Request Body & Pydantic Models

> **IT Consultant Journey** | Week 1 — FastAPI Backend Development  
> **Session:** Day 04 | **Folder:** `~/IT_30day/day04/`

---

## Table of Contents

1. [What We Built Today](#what-we-built-today)
2. [Core Concepts](#core-concepts)
   - [What is Pydantic?](#what-is-pydantic)
   - [POST Requests](#post-requests)
   - [HTTPException](#httpexception)
   - [Query Parameters](#query-parameters)
3. [Project Structure](#project-structure)
4. [Setup & Installation](#setup--installation)
5. [API Endpoints](#api-endpoints)
6. [Request & Response Examples](#request--response-examples)
7. [Validation Rules](#validation-rules)
8. [Testing the API](#testing-the-api)
9. [Key Patterns Learned](#key-patterns-learned)
10. [Common Errors & Fixes](#common-errors--fixes)
11. [What's Next](#whats-next)

---

## What We Built Today

A fully functional **Users REST API** with:

- Pydantic models for automatic data validation
- POST endpoint to create new users
- GET endpoints to list, search, and retrieve users
- DELETE endpoint to remove users
- Proper error handling with meaningful HTTP status codes
- In-memory storage (temporary — replaced with real database on Day 06)

---

## Core Concepts

### What is Pydantic?

Pydantic is a Python library that **validates data automatically** using type hints. FastAPI uses it under the hood for every request body.

**Without Pydantic — unsafe:**
```python
@app.post("/users")
def create_user(data: dict):
    name = data["name"]   # crashes if "name" is missing
    age = data["age"]     # no type check — "hello" would be accepted as age
    return {"name": name}
```

**With Pydantic — safe and professional:**
```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    city: Optional[str] = None

@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    # FastAPI automatically:
    # 1. Reads the JSON body
    # 2. Validates every field type
    # 3. Returns 422 with clear error if something is wrong
    # 4. Converts types where possible (e.g. "25" → 25)
    return {"user": user}
```

---

### Pydantic Field Types

| Type | Example Value | Notes |
|------|--------------|-------|
| `str` | `"Binod"` | Any text |
| `int` | `25` | Whole numbers only |
| `float` | `9.99` | Decimal numbers |
| `bool` | `true` / `false` | Boolean |
| `Optional[str]` | `"Kathmandu"` or not sent | Field can be missing |
| `Optional[str] = None` | Defaults to null if not sent | Optional with default |

---

### The Two-Model Pattern

A professional best practice — always use **separate models** for input and output:

```python
# Input model — what we ACCEPT (no ID, server generates it)
class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    city: Optional[str] = None

# Output model — what we RETURN (always includes ID)
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
    city: Optional[str] = None
```

**Why two models?**
- The client should never be able to set their own `id`
- Output may include computed fields the input doesn't have
- Clean separation of concerns — input validation vs output shape

---

### POST Requests

POST is used to **create new resources**. Key rules:

- Always returns `201 Created` on success (not `200 OK`)
- Data is sent in the **request body** as JSON (not in the URL)
- The server generates the `id` — client never sends it

```python
@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    global next_id

    new_user = {
        "id": next_id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "city": user.city
    }

    users_db.append(new_user)
    next_id += 1

    return {"message": "User created successfully!", "user": new_user}
```

---

### HTTPException

Used to return error responses with a specific status code and message:

```python
from fastapi import HTTPException

# Raise a 404 error
raise HTTPException(status_code=404, detail="User not found")

# Raise a 400 error
raise HTTPException(status_code=400, detail="Email already registered")
```

The client receives:
```json
{
  "detail": "User not found"
}
```

With HTTP status code `404` in the response headers.

---

### Query Parameters

Query parameters are passed in the URL after `?` and are used for **filtering and searching**:

```
GET /users/search?city=Kathmandu
GET /users/search?min_age=25
GET /users/search?city=Kathmandu&min_age=25
```

In FastAPI, query parameters are defined as **function arguments with defaults**:

```python
@app.get("/users/search")
def search_users(city: Optional[str] = None, min_age: Optional[int] = None):
    results = users_db

    if city:
        results = [u for u in results if u.get("city", "").lower() == city.lower()]

    if min_age:
        results = [u for u in results if u["age"] >= min_age]

    return {"total": len(results), "users": results}
```

**Path parameters vs Query parameters:**

| Type | Example | Used for |
|------|---------|---------|
| Path parameter | `/users/42` | Identifying a specific resource |
| Query parameter | `/users?city=Kathmandu` | Filtering, searching, sorting |

---

### Route Order Matters

FastAPI matches routes **top to bottom**. Always place specific routes before dynamic ones:

```python
# CORRECT ORDER
@app.get("/users/search")     # specific — placed first
def search_users(): ...

@app.get("/users/{user_id}")  # dynamic — placed after
def get_user(): ...

# WRONG ORDER — "search" would be treated as a user_id
@app.get("/users/{user_id}")  # dynamic — placed first (bug!)
def get_user(): ...

@app.get("/users/search")     # never reached!
def search_users(): ...
```

---

## Project Structure

```
~/IT_30day/
├── venv/                    # virtual environment (never commit this)
├── day01/
│   └── main.py              # Day 01 — basic GET endpoints
├── day04/
│   ├── main.py              # Day 04 — POST, validation, search, delete
│   └── README.md            # this file
├── .gitignore
└── README.md                # project root readme
```

---

## Setup & Installation

### 1. Navigate to project folder
```bash
cd ~/IT_30day/day04
```

### 2. Activate virtual environment
```bash
source ../venv/bin/activate
```

You will see `(venv)` appear at the start of your terminal prompt. Always activate before running the server.

### 3. Install dependencies (first time only)
```bash
pip install fastapi uvicorn
```

### 4. Run the server
```bash
uvicorn main:app --reload
```

The `--reload` flag automatically restarts the server when you save changes to your code.

### 5. Verify it is running
Open your browser and visit:
```
http://127.0.0.1:8000
```
You should see:
```json
{"message": "Users API is running!"}
```

---

## API Endpoints

| Method | URL | Status Code | Description |
|--------|-----|-------------|-------------|
| `GET` | `/` | 200 | API health check |
| `GET` | `/users` | 200 | List all users |
| `GET` | `/users/{id}` | 200 / 404 | Get a specific user by ID |
| `GET` | `/users/search` | 200 | Search/filter users |
| `POST` | `/users` | 201 / 400 | Create a new user |
| `DELETE` | `/users/{id}` | 200 / 404 | Delete a user by ID |

---

## Request & Response Examples

### GET /users
**Request:**
```bash
http GET http://127.0.0.1:8000/users
```
**Response (200 OK):**
```json
{
  "total": 2,
  "users": [
    {"id": 1, "name": "Alice Tamang", "email": "alice@example.com", "age": 25, "city": "Pokhara"},
    {"id": 2, "name": "Bob Gurung", "email": "bob@example.com", "age": 30, "city": "Kathmandu"}
  ]
}
```

---

### GET /users/{id}
**Request:**
```bash
http GET http://127.0.0.1:8000/users/1
```
**Response (200 OK):**
```json
{"id": 1, "name": "Alice Tamang", "email": "alice@example.com", "age": 25, "city": "Pokhara"}
```

**Response (404 Not Found):**
```json
{"detail": "User with id 99 not found"}
```

---

### GET /users/search
**Filter by city:**
```bash
http GET http://127.0.0.1:8000/users/search city==Kathmandu
```

**Filter by minimum age:**
```bash
http GET http://127.0.0.1:8000/users/search min_age==25
```

**Filter by both:**
```bash
http GET http://127.0.0.1:8000/users/search city==Kathmandu min_age==25
```

**Response (200 OK):**
```json
{
  "total": 1,
  "users": [
    {"id": 2, "name": "Bob Gurung", "email": "bob@example.com", "age": 30, "city": "Kathmandu"}
  ]
}
```

---

### POST /users
**Request body (JSON):**
```json
{
  "name": "Binod Sharma",
  "email": "binod@example.com",
  "age": 28,
  "city": "Kathmandu"
}
```

**HTTPie command:**
```bash
http POST http://127.0.0.1:8000/users \
  name="Binod Sharma" \
  email="binod@example.com" \
  age:=28 \
  city="Kathmandu"
```

> Note: Use `:=` for numbers in HTTPie. `=` sends as string, `:=` sends as integer.

**Response (201 Created):**
```json
{
  "message": "User created successfully!",
  "user": {
    "id": 1,
    "name": "Binod Sharma",
    "email": "binod@example.com",
    "age": 28,
    "city": "Kathmandu"
  }
}
```

**Response (400 Bad Request — duplicate email):**
```json
{"detail": "Email binod@example.com already registered"}
```

**Response (400 Bad Request — invalid age):**
```json
{"detail": "Age must be between 0 and 120"}
```

**Response (422 Unprocessable Entity — wrong type sent by Pydantic):**
```json
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

---

### DELETE /users/{id}
**Request:**
```bash
http DELETE http://127.0.0.1:8000/users/1
```

**Response (200 OK):**
```json
{"message": "User 1 deleted successfully"}
```

**Response (404 Not Found):**
```json
{"detail": "User 1 not found"}
```

---

## Validation Rules

All validation is applied automatically on every POST request:

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `name` | string | Yes | Any non-empty string |
| `email` | string | Yes | Must be unique — no duplicates allowed |
| `age` | integer | Yes | Must be between 0 and 120 |
| `city` | string | No | Optional — defaults to null if not sent |

---

## Testing the API

### Option 1 — Swagger UI (Recommended for beginners)
Open in browser:
```
http://127.0.0.1:8000/docs
```
- Click any endpoint to expand it
- Click **Try it out**
- Fill in the parameters or request body
- Click **Execute**
- See the live response

### Option 2 — ReDoc (Clean documentation view)
```
http://127.0.0.1:8000/redoc
```
Best for sharing with clients or non-technical stakeholders.

### Option 3 — HTTPie (Terminal — professional workflow)

Install:
```bash
brew install httpie
```

Full test sequence:
```bash
# 1. Check API is running
http GET http://127.0.0.1:8000/

# 2. Create first user
http POST http://127.0.0.1:8000/users \
  name="Alice Tamang" \
  email="alice@example.com" \
  age:=25 \
  city="Pokhara"

# 3. Create second user
http POST http://127.0.0.1:8000/users \
  name="Bob Gurung" \
  email="bob@example.com" \
  age:=30 \
  city="Kathmandu"

# 4. List all users
http GET http://127.0.0.1:8000/users

# 5. Get specific user
http GET http://127.0.0.1:8000/users/1

# 6. Search by city
http GET http://127.0.0.1:8000/users/search city==Kathmandu

# 7. Search by age
http GET http://127.0.0.1:8000/users/search min_age==28

# 8. Test duplicate email (should return 400)
http POST http://127.0.0.1:8000/users \
  name="Fake Alice" \
  email="alice@example.com" \
  age:=22

# 9. Test invalid age (should return 400)
http POST http://127.0.0.1:8000/users \
  name="Test" \
  email="test@example.com" \
  age:=999

# 10. Delete a user
http DELETE http://127.0.0.1:8000/users/1

# 11. Confirm deletion
http GET http://127.0.0.1:8000/users

# 12. Try to get deleted user (should return 404)
http GET http://127.0.0.1:8000/users/1
```

### Option 4 — Browser (GET requests only)
For GET requests, you can simply paste the URL in your browser:
```
http://127.0.0.1:8000/users
http://127.0.0.1:8000/users/1
http://127.0.0.1:8000/users/search?city=Kathmandu
http://127.0.0.1:8000/users/search?min_age=25
```

---

## Key Patterns Learned

### 1. Always use `status_code=201` for POST
```python
@app.post("/users", status_code=201)   # correct
@app.post("/users")                    # wrong — returns 200 by default
```

### 2. Use `global` for in-memory counter
```python
next_id = 1

def create_user(user: UserCreate):
    global next_id        # required to modify a module-level variable
    next_id += 1
```

### 3. Raise HTTPException to stop execution immediately
```python
if user_not_found:
    raise HTTPException(status_code=404, detail="User not found")
    # code below this line never runs
```

### 4. Use `enumerate` when you need both index and value
```python
for index, user in enumerate(users_db):
    if user["id"] == user_id:
        users_db.pop(index)   # remove by index position
```

### 5. Case-insensitive search
```python
if u.get("city", "").lower() == city.lower():
    # "kathmandu" == "Kathmandu" == "KATHMANDU"
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `422 Unprocessable Entity` | Wrong data type sent | Check your request body matches the Pydantic model |
| `404 Not Found` | Wrong URL or ID doesn't exist | Check the endpoint URL and verify the ID exists |
| `400 Bad Request` | Validation failed (duplicate email, bad age) | Read the `detail` field in the response |
| `Permission denied: ../day02/` | Wrong file permissions | Run `chmod -R 755 ~/IT_30day/` |
| `Address already in use` | Port 8000 is busy | Run `lsof -i :8000` then `kill <PID>` |
| Smart quote error in terminal | Copied quotes from chat/document | Type quotes manually or use no quotes |
| `ModuleNotFoundError: fastapi` | Virtual environment not active | Run `source ../venv/bin/activate` |

---

## What's Next

**Day 05 — PUT Requests & Full CRUD**
- Update existing users with PUT
- Complete the four pillars: Create, Read, Update, Delete
- Understand the difference between PUT (full update) and PATCH (partial update)
- Build a fully RESTful API that any frontend can connect to

**Day 06 — SQLite + SQLAlchemy**
- Replace the in-memory list with a real database
- Data persists even after the server restarts
- Introduction to ORM (Object Relational Mapper)

**Day 07 — Table Relationships**
- Link users to posts or orders
- Database joins and foreign keys
- Complex queries and filters

---

## Quick Reference Card

```bash
# Activate environment
source ~/IT_30day/venv/bin/activate

# Start server
cd ~/IT_30day/day04
uvicorn main:app --reload

# Swagger docs
open http://127.0.0.1:8000/docs

# Git — save your work
git add .
git commit -m "Day 04 - POST requests and Pydantic models"
git push origin main
```

---

*IT Consultant Journey — Building real skills, one day at a time.*
