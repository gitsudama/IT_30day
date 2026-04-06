# Day 05 — PUT, PATCH & Full CRUD API

> **IT Consultant Journey** | Week 1 — FastAPI Backend Development
> **Session:** Day 05 | **Folder:** `~/IT_30day/day05/`

---

## Table of Contents

1. [What We Built Today](#what-we-built-today)
2. [CRUD — The Four Pillars](#crud--the-four-pillars)
3. [Core Concepts](#core-concepts)
   - [PUT vs PATCH](#put-vs-patch)
   - [The Three-Model Pattern](#the-three-model-pattern)
   - [The DRY Principle](#the-dry-principle)
   - [Safe PATCH Logic](#safe-patch-logic)
4. [Project Structure](#project-structure)
5. [Setup & Installation](#setup--installation)
6. [API Endpoints](#api-endpoints)
7. [Pydantic Models](#pydantic-models)
8. [Request & Response Examples](#request--response-examples)
9. [Validation Rules](#validation-rules)
10. [Testing the API](#testing-the-api)
11. [Full Code Reference](#full-code-reference)
12. [Common Errors & Fixes](#common-errors--fixes)
13. [Key Patterns Learned](#key-patterns-learned)
14. [What's Next](#whats-next)

---

## What We Built Today

A **complete, fully RESTful Users API** implementing all four CRUD operations:

- `POST /users` — Create a new user
- `GET /users` — Read all users
- `GET /users/{id}` — Read one user
- `GET /users/search` — Search and filter users
- `PUT /users/{id}` — Full update (replace entire resource)
- `PATCH /users/{id}` — Partial update (change specific fields only)
- `DELETE /users/{id}` — Delete a user

This is the foundation every backend system in the world is built on — inventory systems, HR software, hospital records, e-commerce platforms. All of them are CRUD at the core.

---

## CRUD — The Four Pillars

| Operation | HTTP Method | SQL Equivalent | Example |
|-----------|-------------|----------------|---------|
| **Create** | `POST` | `INSERT` | Add new user |
| **Read** | `GET` | `SELECT` | Get user list |
| **Update** | `PUT` / `PATCH` | `UPDATE` | Edit user info |
| **Delete** | `DELETE` | `DELETE` | Remove user |

By the end of Day 05, all four pillars are fully implemented and tested.

---

## Core Concepts

### PUT vs PATCH

This is one of the most misunderstood distinctions in REST API design.

| | PUT | PATCH |
|---|---|---|
| **Meaning** | Replace the **entire** resource | Update **specific fields** only |
| **Fields required** | All fields must be sent | Only send what you want to change |
| **Missing fields** | Reset to `null` or default | Left completely unchanged |
| **Typical use case** | Full "edit profile" form submission | "Change city" button click |
| **Risk** | Accidentally wipes fields you forgot to send | Safe — untouched fields never change |

#### PUT Example

User 1 currently has:
```json
{"id": 1, "name": "Alice", "email": "alice@example.com", "age": 25, "city": "Pokhara"}
```

You send a PUT with only name and email:
```json
{"name": "Alice Rai", "email": "alice.rai@example.com", "age": 25, "city": null}
```

Result — city is wiped because you did not send it:
```json
{"id": 1, "name": "Alice Rai", "email": "alice.rai@example.com", "age": 25, "city": null}
```

#### PATCH Example

Same user. You send PATCH with only city:
```json
{"city": "Kathmandu"}
```

Result — only city changed, everything else is untouched:
```json
{"id": 1, "name": "Alice", "email": "alice@example.com", "age": 25, "city": "Kathmandu"}
```

#### When to use which?

| Situation | Use |
|-----------|-----|
| User submits a full edit profile form | `PUT` |
| User clicks a single "change city" button | `PATCH` |
| Updating only a status field | `PATCH` |
| Replacing an entire document or resource | `PUT` |
| Mobile app saving partial form progress | `PATCH` |

> **Consulting insight:** Most junior developers only implement PUT and skip PATCH entirely. When auditing a company's API, missing PATCH endpoints is a design gap you can identify, explain, and fix — adding real value as a consultant.

---

### The Three-Model Pattern

A professional best practice — each HTTP method that deals with a request body gets its own dedicated Pydantic model:

```python
# For POST — required fields only (no id, server generates it)
class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    city: Optional[str] = None


# For PUT — all fields required (full replacement, everything must be sent)
class UserUpdate(BaseModel):
    name: str
    email: str
    age: int
    city: Optional[str] = None


# For PATCH — all fields optional (only send what you want to change)
class UserPatch(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
```

**Why not reuse one model for everything?**

- `UserCreate` and `UserUpdate` look similar but serve different purposes — separating them makes the intent explicit and allows them to diverge later
- `UserPatch` has completely different rules — all fields optional — which cannot be expressed by reusing `UserCreate`
- Swagger UI generates clearer documentation when each method has its own model
- Future changes (e.g. adding a `role` field only admins can set on create) are much easier to manage

---

### The DRY Principle

**DRY = Don't Repeat Yourself**

Without DRY — user lookup repeated in every endpoint:
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    for user in users_db:          # repeated
        if user["id"] == user_id:  # repeated
            return user            # repeated
    raise HTTPException(status_code=404, ...)

@app.put("/users/{user_id}")
def update_user(user_id: int, ...):
    for user in users_db:          # repeated again
        if user["id"] == user_id:  # repeated again
            ...
```

With DRY — extracted into a helper function:
```python
def find_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    return None

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = find_user(user_id)   # one clean line
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}")
def update_user(user_id: int, ...):
    user = find_user(user_id)   # same clean line
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    ...
```

Benefits of DRY:
- Fix a bug in one place, fixed everywhere
- Easier to read and understand
- Easier to test
- Scales cleanly as your API grows

---

### Safe PATCH Logic

In PATCH, we need to update only the fields that were actually sent. The key is using `is not None` instead of a plain `if` check:

```python
# WRONG — skips empty strings
if user_data.city:
    user["city"] = user_data.city
# Problem: if someone sends city="" to clear it, this ignores it

# CORRECT — only skips fields that were not sent at all
if user_data.city is not None:
    user["city"] = user_data.city
# Works correctly: updates to "", updates to "Kathmandu", skips if not sent
```

Full PATCH implementation:
```python
@app.patch("/users/{user_id}")
def patch_user(user_id: int, user_data: UserPatch):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    if user_data.name is not None:
        user["name"] = user_data.name

    if user_data.email is not None:
        for existing in users_db:
            if existing["email"] == user_data.email and existing["id"] != user_id:
                raise HTTPException(status_code=400, detail="Email already in use")
        user["email"] = user_data.email

    if user_data.age is not None:
        if user_data.age < 0 or user_data.age > 120:
            raise HTTPException(status_code=400, detail="Age must be between 0 and 120")
        user["age"] = user_data.age

    if user_data.city is not None:
        user["city"] = user_data.city

    return {"message": "User patched successfully", "user": user}
```

---

## Project Structure

```
~/IT_30day/
├── venv/                    # virtual environment (never commit this)
├── .gitignore               # excludes venv, __pycache__, .env
├── day01/
│   └── main.py              # Day 01 — basic GET endpoints
├── day04/
│   ├── main.py              # Day 04 — POST, Pydantic, validation
│   └── README.md
├── day05/
│   ├── main.py              # Day 05 — full CRUD with PUT and PATCH
│   └── README.md            # this file
└── README.md                # project root readme
```

---

## Setup & Installation

### 1. Navigate to project folder
```bash
cd ~/IT_30day/day05
```

### 2. Activate virtual environment
```bash
source ../venv/bin/activate
```

You will see `(venv)` at the start of your prompt. Always activate before running the server.

### 3. Install dependencies (first time only)
```bash
pip install fastapi uvicorn
```

### 4. Run the server
```bash
uvicorn main:app --reload
```

`--reload` automatically restarts the server whenever you save a change to your code.

### 5. Verify it is running

Visit in browser:
```
http://127.0.0.1:8000
```

Expected response:
```json
{"message": "Users API is running!"}
```

### 6. Open interactive documentation
```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| `GET` | `/` | None | API health check |
| `GET` | `/users` | None | List all users |
| `GET` | `/users/search` | None | Search and filter users |
| `GET` | `/users/{id}` | None | Get a specific user |
| `POST` | `/users` | None | Create a new user |
| `PUT` | `/users/{id}` | None | Full update — replace user |
| `PATCH` | `/users/{id}` | None | Partial update — specific fields |
| `DELETE` | `/users/{id}` | None | Delete a user |

> Authentication will be added on Day 08 with JWT tokens.

---

## Pydantic Models

### UserCreate — used for POST
```python
class UserCreate(BaseModel):
    name: str                    # required
    email: str                   # required, must be unique
    age: int                     # required, must be 0–120
    city: Optional[str] = None   # optional
```

### UserUpdate — used for PUT
```python
class UserUpdate(BaseModel):
    name: str                    # required — must send all fields
    email: str                   # required
    age: int                     # required
    city: Optional[str] = None   # optional — can be null
```

### UserPatch — used for PATCH
```python
class UserPatch(BaseModel):
    name: Optional[str] = None   # optional — only send what changes
    email: Optional[str] = None  # optional
    age: Optional[int] = None    # optional
    city: Optional[str] = None   # optional
```

---

## Request & Response Examples

### POST /users — Create user

**Request:**
```bash
http POST http://127.0.0.1:8000/users \
  name="Alice Tamang" \
  email="alice@example.com" \
  age:=25 \
  city="Pokhara"
```

**Response (201 Created):**
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "name": "Alice Tamang",
    "email": "alice@example.com",
    "age": 25,
    "city": "Pokhara"
  }
}
```

---

### GET /users — List all

**Request:**
```bash
http GET http://127.0.0.1:8000/users
```

**Response (200 OK):**
```json
{
  "total": 3,
  "users": [
    {"id": 1, "name": "Alice Tamang", "email": "alice@example.com", "age": 25, "city": "Pokhara"},
    {"id": 2, "name": "Bob Gurung", "email": "bob@example.com", "age": 30, "city": "Kathmandu"},
    {"id": 3, "name": "Carol Shrestha", "email": "carol@example.com", "age": 22, "city": "Lalitpur"}
  ]
}
```

---

### GET /users/search — Filter users

**By city:**
```bash
http GET http://127.0.0.1:8000/users/search city==Kathmandu
```

**By age range:**
```bash
http GET http://127.0.0.1:8000/users/search min_age==22 max_age==28
```

**By name (partial match):**
```bash
http GET http://127.0.0.1:8000/users/search name==Alice
```

**Combined filters:**
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

### PUT /users/{id} — Full update

**Request — all fields required:**
```bash
http PUT http://127.0.0.1:8000/users/1 \
  name="Alice Tamang Rai" \
  email="alice.rai@example.com" \
  age:=26 \
  city="Kathmandu"
```

**Response (200 OK):**
```json
{
  "message": "User updated successfully",
  "user": {
    "id": 1,
    "name": "Alice Tamang Rai",
    "email": "alice.rai@example.com",
    "age": 26,
    "city": "Kathmandu"
  }
}
```

**Response (404 Not Found):**
```json
{"detail": "User with id 99 not found"}
```

**Response (400 Bad Request — email taken):**
```json
{"detail": "Email alice.rai@example.com is already used by another user"}
```

---

### PATCH /users/{id} — Partial update

**Update city only — other fields unchanged:**
```bash
http PATCH http://127.0.0.1:8000/users/2 \
  city="Pokhara"
```

**Response (200 OK):**
```json
{
  "message": "User patched successfully",
  "user": {
    "id": 2,
    "name": "Bob Gurung",
    "email": "bob@example.com",
    "age": 30,
    "city": "Pokhara"
  }
}
```

**Update age only:**
```bash
http PATCH http://127.0.0.1:8000/users/3 \
  age:=23
```

**Update multiple fields but not all:**
```bash
http PATCH http://127.0.0.1:8000/users/1 \
  name="Alice Rai" \
  age:=27
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
{"detail": "User with id 1 not found"}
```

---

## Validation Rules

| Field | Rule | Error if violated |
|-------|------|-------------------|
| `name` | Required string on POST and PUT | 422 Unprocessable Entity |
| `email` | Required, must be unique across all users | 400 Bad Request |
| `age` | Required integer, must be 0–120 | 400 Bad Request |
| `city` | Optional in all methods | — |
| Any field | Wrong type (e.g. `age: "hello"`) | 422 Unprocessable Entity |
| PUT body | Missing required field | 422 Unprocessable Entity |

---

## Testing the API

### Option 1 — Swagger UI (best for visual testing)
```
http://127.0.0.1:8000/docs
```
- Click any endpoint to expand
- Click **Try it out**
- Fill in the body or parameters
- Click **Execute**
- Observe the response code and body

Pay special attention when comparing PUT and PATCH in Swagger:
- PUT shows all fields as required
- PATCH shows all fields as optional
This difference is driven entirely by the Pydantic models.

---

### Option 2 — HTTPie full test sequence

Run these in order in a new terminal tab with venv active:

```bash
# Activate environment
source ~/IT_30day/venv/bin/activate

# Step 1 — create three users
http POST http://127.0.0.1:8000/users \
  name="Alice Tamang" email="alice@example.com" age:=25 city="Pokhara"

http POST http://127.0.0.1:8000/users \
  name="Bob Gurung" email="bob@example.com" age:=30 city="Kathmandu"

http POST http://127.0.0.1:8000/users \
  name="Carol Shrestha" email="carol@example.com" age:=22 city="Lalitpur"

# Step 2 — verify all created
http GET http://127.0.0.1:8000/users

# Step 3 — full update with PUT
http PUT http://127.0.0.1:8000/users/1 \
  name="Alice Tamang Rai" email="alice.rai@example.com" age:=26 city="Kathmandu"

# Step 4 — verify full update
http GET http://127.0.0.1:8000/users/1

# Step 5 — partial update with PATCH (city only)
http PATCH http://127.0.0.1:8000/users/2 \
  city="Pokhara"

# Step 6 — verify only city changed, rest unchanged
http GET http://127.0.0.1:8000/users/2

# Step 7 — patch age only
http PATCH http://127.0.0.1:8000/users/3 \
  age:=23

# Step 8 — search by name
http GET http://127.0.0.1:8000/users/search name==Alice

# Step 9 — search by age range
http GET http://127.0.0.1:8000/users/search min_age==22 max_age==27

# Step 10 — search combined filters
http GET http://127.0.0.1:8000/users/search city==Pokhara min_age==22

# Step 11 — PUT with duplicate email (should return 400)
http PUT http://127.0.0.1:8000/users/2 \
  name="Bob" email="alice.rai@example.com" age:=30 city="Kathmandu"

# Step 12 — PATCH on non-existent user (should return 404)
http PATCH http://127.0.0.1:8000/users/99 \
  city="Nowhere"

# Step 13 — PATCH with invalid age (should return 400)
http PATCH http://127.0.0.1:8000/users/3 \
  age:=200

# Step 14 — delete user 3
http DELETE http://127.0.0.1:8000/users/3

# Step 15 — confirm deletion — should show 2 users
http GET http://127.0.0.1:8000/users

# Step 16 — try to get deleted user (should return 404)
http GET http://127.0.0.1:8000/users/3
```

---

### Option 3 — Browser (GET only)

```
http://127.0.0.1:8000/users
http://127.0.0.1:8000/users/1
http://127.0.0.1:8000/users/search?city=Kathmandu
http://127.0.0.1:8000/users/search?min_age=25&max_age=30
http://127.0.0.1:8000/users/search?name=Alice
```

---

## Full Code Reference

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Users CRUD API",
    description="A complete REST API with full CRUD operations",
    version="2.0"
)

# In-memory storage
users_db = []
next_id = 1


# Pydantic models
class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    city: Optional[str] = None


class UserUpdate(BaseModel):
    name: str
    email: str
    age: int
    city: Optional[str] = None


class UserPatch(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None


# Helper function — DRY principle
def find_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    return None


# CREATE
@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    global next_id
    for existing in users_db:
        if existing["email"] == user.email:
            raise HTTPException(status_code=400, detail=f"Email {user.email} is already registered")
    if user.age < 0 or user.age > 120:
        raise HTTPException(status_code=400, detail="Age must be between 0 and 120")
    new_user = {"id": next_id, "name": user.name, "email": user.email, "age": user.age, "city": user.city}
    users_db.append(new_user)
    next_id += 1
    return {"message": "User created successfully", "user": new_user}


# READ ALL
@app.get("/users")
def get_users():
    return {"total": len(users_db), "users": users_db}


# SEARCH — must come before /{user_id}
@app.get("/users/search")
def search_users(
    city: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    name: Optional[str] = None
):
    results = users_db
    if city:
        results = [u for u in results if u.get("city", "").lower() == city.lower()]
    if min_age is not None:
        results = [u for u in results if u["age"] >= min_age]
    if max_age is not None:
        results = [u for u in results if u["age"] <= max_age]
    if name:
        results = [u for u in results if name.lower() in u["name"].lower()]
    return {"total": len(results), "users": results}


# READ ONE
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user


# UPDATE — full replacement
@app.put("/users/{user_id}")
def update_user(user_id: int, user_data: UserUpdate):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    for existing in users_db:
        if existing["email"] == user_data.email and existing["id"] != user_id:
            raise HTTPException(status_code=400, detail=f"Email {user_data.email} is already used by another user")
    if user_data.age < 0 or user_data.age > 120:
        raise HTTPException(status_code=400, detail="Age must be between 0 and 120")
    user["name"] = user_data.name
    user["email"] = user_data.email
    user["age"] = user_data.age
    user["city"] = user_data.city
    return {"message": "User updated successfully", "user": user}


# PARTIAL UPDATE
@app.patch("/users/{user_id}")
def patch_user(user_id: int, user_data: UserPatch):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    if user_data.name is not None:
        user["name"] = user_data.name
    if user_data.email is not None:
        for existing in users_db:
            if existing["email"] == user_data.email and existing["id"] != user_id:
                raise HTTPException(status_code=400, detail="Email already in use by another user")
        user["email"] = user_data.email
    if user_data.age is not None:
        if user_data.age < 0 or user_data.age > 120:
            raise HTTPException(status_code=400, detail="Age must be between 0 and 120")
        user["age"] = user_data.age
    if user_data.city is not None:
        user["city"] = user_data.city
    return {"message": "User patched successfully", "user": user}


# DELETE
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    for index, user in enumerate(users_db):
        if user["id"] == user_id:
            users_db.pop(index)
            return {"message": f"User {user_id} deleted successfully"}
    raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `422 Unprocessable Entity` on PUT | Forgot to send a required field | Send all fields — name, email, age are required |
| `400 Bad Request — email in use` | Email already registered to another user | Use a different email or check existing users first |
| `404 Not Found` | Wrong user ID | Run `GET /users` to see valid IDs |
| PATCH not changing anything | Sent `null` explicitly instead of omitting field | Omit the field entirely if you do not want to change it |
| `search` endpoint returning 404 | Route order wrong — `/{user_id}` placed before `/search` | Move `/search` route above `/{user_id}` in your file |
| `ModuleNotFoundError` | Virtual environment not active | Run `source ../venv/bin/activate` |
| `Address already in use` | Port 8000 busy from previous session | Run `lsof -i :8000` then `kill <PID>` |
| Smart quote error in terminal | Copied commands from chat or document | Type quotes manually in terminal — never copy/paste |

---

## Key Patterns Learned

### 1. Three-model pattern
```python
UserCreate  →  POST   (required fields, no id)
UserUpdate  →  PUT    (all fields required)
UserPatch   →  PATCH  (all fields optional)
```

### 2. Helper function for DRY code
```python
def find_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    return None
```

### 3. Safe PATCH with is not None
```python
if user_data.city is not None:    # correct — handles empty string
    user["city"] = user_data.city

if user_data.city:                # wrong — skips empty string ""
    user["city"] = user_data.city
```

### 4. Route ordering rule
```python
@app.get("/users/search")    # specific — always first
@app.get("/users/{user_id}") # dynamic — always after
```

### 5. Email uniqueness check excluding self
```python
# On update — skip the current user when checking duplicates
for existing in users_db:
    if existing["email"] == new_email and existing["id"] != user_id:
        raise HTTPException(status_code=400, detail="Email taken")
```

---

## What's Next

**Day 06 — SQLite + SQLAlchemy**

Today's API loses all data when the server restarts because we store everything in a Python list. Day 06 connects the API to a real SQLite database so data persists permanently.

| Day | Topic | Goal |
|-----|-------|------|
| **Day 06** | SQLite + SQLAlchemy | Real database — data survives restarts |
| **Day 07** | Relationships + queries | Link users to posts, orders, or tasks |
| **Day 08** | JWT Authentication | Secure endpoints with login tokens |
| **Day 09** | Mini project | Full Task Manager API — production ready |

---

## Quick Reference Card

```bash
# Activate environment
source ~/IT_30day/venv/bin/activate

# Start server
cd ~/IT_30day/day05
uvicorn main:app --reload

# Interactive docs
open http://127.0.0.1:8000/docs

# Save your work
git add .
git commit -m "Day 05 - PUT PATCH full CRUD complete"
git push origin main
```

---

*IT Consultant Journey — Building real skills, one day at a time.*
