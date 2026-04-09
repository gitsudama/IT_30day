# Day 06 — SQLite + SQLAlchemy: From Memory to Real Database

## 🔗 Connection to Day 05

On Day 05, you built a complete CRUD API with all 7 endpoints.
But everything lived inside a Python list:

```python
users_db = []  # Dies when server stops
```

### What Day 05 Gave Us (and what it couldn't)

| What Day 05 Achieved | What Day 05 Could NOT Do |
|----------------------|--------------------------|
| ✅ POST — create users | ❌ Data vanishes on server restart |
| ✅ GET — list, search, filter | ❌ No real search performance (loops through list) |
| ✅ PUT — full update | ❌ No protection at storage level (only Pydantic) |
| ✅ PATCH — partial update | ❌ Cannot handle thousands of users |
| ✅ DELETE — remove user | ❌ No uniqueness enforced at data level |
| ✅ 3 Pydantic models | ❌ ID managed manually with counter |
| ✅ DRY code with find_user() | ❌ No pagination — returns ALL users always |

### Day 05 → Day 06 Transition Summary

| Concept | Day 05 (In-Memory) | Day 06 (Database) |
|---------|--------------------|--------------------|
| Storage | `users_db = []` | `users.db` file (SQLite) |
| Persistence | ❌ Lost on restart | ✅ Permanent |
| ID generation | Manual counter `next_id` | Auto-increment by database |
| Find user | Loop through list | `db.query(User).filter(...)` |
| Duplicate check | Loop + compare emails | `unique=True` constraint + query |
| Data validation | Pydantic only (1 layer) | Pydantic + DB constraints (2 layers) |
| Search | Python `if` conditions on list | SQL `ilike()` queries with indexes |
| Pagination | Not implemented | `skip` and `limit` parameters |
| Project structure | Single `main.py` | 5 separate files (separation of concerns) |

---

## 📚 Core Concepts Learned

### 1. What Is a Database?

A permanent storage system for your application's data.

| Concept | Analogy | Example |
|---------|---------|---------|
| Database | A notebook | `users.db` file |
| Table | A page in the notebook | `users` table |
| Row | One line/entry on the page | Ram Sharma's record |
| Column | One field of information | `name`, `email`, `age` |
| Primary Key | Unique line number — never repeats | `id = 1` |
| Index | Bookmark for fast lookups | Index on `email` column |

### 2. SQLite — Why We Use It

SQLite is a **file-based database**. No installation, no server, no configuration.

```text
Your entire database = one file called users.db
```

| Feature | SQLite | PostgreSQL / MySQL |
|---------|--------|--------------------|
| Installation | None — built into Python | Separate server required |
| Storage | Single `.db` file | Background service |
| Setup | Zero configuration | Dozens of settings |
| Best for | Learning, small apps, prototypes | Production, large-scale apps |
| Users at once | Handles ~10-50 well | Handles thousands+ |

> **When to recommend SQLite as a consultant:**
> Small internal tools (billing, attendance, inventory) for offices with 5–20 users.
> Recommending PostgreSQL for a 10-person office tool is over-engineering.

### 3. ORM — Object Relational Mapper

Instead of writing raw SQL, you write Python. SQLAlchemy translates it to SQL for you.

| Task | Raw SQL | SQLAlchemy ORM (Python) |
|------|---------|------------------------|
| Get all users | `SELECT * FROM users;` | `db.query(User).all()` |
| Find by ID | `SELECT * FROM users WHERE id = 5;` | `db.query(User).filter(User.id == 5).first()` |
| Find by email | `SELECT * FROM users WHERE email = 'x';` | `db.query(User).filter(User.email == "x").first()` |
| Add user | `INSERT INTO users (name) VALUES ('Ram');` | `db.add(User(name="Ram"))` |
| Delete user | `DELETE FROM users WHERE id = 5;` | `db.delete(user_obj)` |
| Filter | `SELECT * FROM users WHERE age > 25;` | `db.query(User).filter(User.age > 25).all()` |
| Case-insensitive | `WHERE city ILIKE '%kath%';` | `.filter(User.city.ilike("%kath%"))` |
| Paginate | `SELECT * FROM users LIMIT 10 OFFSET 20;` | `.offset(20).limit(10).all()` |

**Benefits of ORM over raw SQL:**
- Your editor gives autocomplete and type checking
- No SQL syntax errors from string typos
- Protection against SQL injection attacks
- One language (Python) instead of two (Python + SQL)

### 4. SQLAlchemy's Four Key Components

```text
Engine ──→ SessionLocal ──→ Session ──→ Your Code
  │              │              │
  │              │              └── The active conversation
  │              └── Factory that creates sessions
  └── The connection to the database file
```

| Component | What It Does | Analogy |
|-----------|-------------|---------|
| **Engine** | Connects Python to the `.db` file | Phone line to the notebook |
| **SessionLocal** | Template/factory for creating sessions | Phone dialer |
| **Session** | One active conversation with the database | One phone call |
| **Base** | Parent class for all table models | Notebook template |

### 5. The Three Sacred Database Write Operations

Every time you change data, follow this sequence:

```text
db.add(object)      →  Stage it (like git add)
db.commit()         →  Save to disk permanently (like git commit)
db.refresh(object)  →  Reload from database to get auto-generated values (like git pull)
```

| Operation | What Happens | What If You Skip It |
|-----------|-------------|---------------------|
| `db.add()` | Object is staged in memory | Nothing to commit |
| `db.commit()` | All staged changes written to disk | **Data is lost** when session closes |
| `db.refresh()` | Object reloaded with DB-generated values (like `id`) | You won't have the auto-generated `id` |

**Critical rule:** `db.add()` without `db.commit()` = nothing saved.
Like typing a document and never pressing Ctrl+S.

### 6. Two Types of Models — THE Most Important Distinction

```text
┌─────────────────────────────────┐     ┌──────────────────────────────────┐
│       models.py                 │     │       schemas.py                 │
│       (SQLAlchemy Model)        │     │       (Pydantic Schema)          │
│                                 │     │                                  │
│  Defines DATABASE TABLE         │     │  Defines API REQUEST/RESPONSE    │
│  Inherits from Base             │     │  Inherits from BaseModel         │
│  Talks to: Database             │     │  Talks to: Client/User           │
│  Controls: How data is STORED   │     │  Controls: How data is SENT      │
│                                 │     │                                  │
│  class User(Base):              │     │  class UserCreate(BaseModel):    │
│      __tablename__ = "users"    │     │      name: str                   │
│      id = Column(Integer, ...)  │     │      email: str                  │
│      name = Column(String, ...) │     │      age: int                    │
│      email = Column(String, ..) │     │      city: Optional[str] = None  │
└─────────────────────────────────┘     └──────────────────────────────────┘
```

**Restaurant analogy:**
- SQLAlchemy model = **Recipe card** (how the dish is prepared and stored in the kitchen)
- Pydantic schema = **Menu** (what the customer sees and can order)

They describe the same data but serve different audiences.

**Why both?**
- You might have database columns you never want to expose (passwords, internal flags)
- The client sends fewer fields (no `id` on create) than what the database stores
- Different operations need different validation (POST vs PUT vs PATCH)

### 7. Dependency Injection — `get_db()`

Instead of manually creating a database session in every endpoint:

```python
# ❌ Bad — manual session management in every endpoint
@app.get("/users")
def get_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return users
    finally:
        db.close()
```

You use dependency injection:

```python
# ✅ Good — FastAPI handles session lifecycle automatically
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

**The `get_db()` function:**

```python
def get_db():
    db = SessionLocal()
    try:
        yield db        # Hand the session to the endpoint
    finally:
        db.close()      # Always close — even if the endpoint crashes
```

**Why `yield` not `return`?**
- `return` ends the function immediately — `finally` never runs
- `yield` pauses the function, gives the session to the endpoint, then resumes after the endpoint finishes — so `finally` always runs

**Why this matters:**
Forgetting to close sessions causes **connection pool exhaustion** —
the database runs out of available connections and the whole app freezes.
This pattern prevents that entirely.

### 8. `response_model` — Controlling API Output

```python
@app.get("/users/{user_id}", response_model=UserResponse)
```

This tells FastAPI: "Even if the database object has 20 fields,
only include the fields defined in `UserResponse` in the JSON output."

**Why it matters:**
- Prevents accidental data leakage (passwords, internal IDs, flags)
- Keeps API responses clean and predictable
- Auto-generates accurate Swagger documentation

### 9. Defense in Depth — Two Layers of Validation

```text
Layer 1: Pydantic (schemas.py)     →  Validates API input
         "Client must send a valid email string"

Layer 2: SQLAlchemy (models.py)    →  Validates at database level
         "Column email has unique=True — database rejects duplicates"
```

If someone bypasses your API (direct database access, a code bug),
the database constraints still protect your data.

| Protection | Pydantic Layer | Database Layer |
|-----------|---------------|----------------|
| Required field | `name: str` (no default) | `nullable=False` |
| Unique email | Manual check in endpoint | `unique=True` on column |
| Type safety | `age: int` rejects strings | `Column(Integer)` rejects strings |
| Optional field | `Optional[str] = None` | `nullable=True` |

### 10. Pagination — Why and How

Without pagination, `GET /users` on a table with 100,000 rows would:
- Load all 100,000 records into memory
- Serialize all of them to JSON
- Send a massive response that freezes the client

**Solution: `skip` and `limit`**

```python
@app.get("/users")
def read_users(skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()
```

| Request | What It Returns |
|---------|----------------|
| `GET /users` | First 100 users (defaults) |
| `GET /users?limit=10` | First 10 users |
| `GET /users?skip=10&limit=10` | Users 11–20 |
| `GET /users?skip=20&limit=10` | Users 21–30 |

### 11. `ilike()` — Case-Insensitive Search

```python
query.filter(User.city.ilike(f"%{city}%"))
```

| Search Term | `ilike` Matches | `like` Matches |
|-------------|-----------------|----------------|
| `kathmandu` | Kathmandu ✅ KATHMANDU ✅ kathmandu ✅ | kathmandu ✅ only |
| `Kath` | Kathmandu ✅ kathford ✅ | Kathford ✅ only |

The `%` symbols are wildcards — match any characters before/after.

---

## 📁 Project Structure

```text
~/IT_30day/day06/
├── main.py        — FastAPI app, all endpoints, ties everything together
├── database.py    — Engine, SessionLocal, Base, get_db() dependency
├── models.py      — SQLAlchemy User model (defines database table)
├── schemas.py     — Pydantic schemas (validates API input/output)
├── crud.py        — All database operations (create, read, update, delete)
└── users.db       — SQLite database file (auto-created, in .gitignore)
```

**How files connect:**

```text
Client Request
     │
     ▼
  main.py ──────── receives request
     │
     ├──→ schemas.py ──── validates input data (Pydantic)
     │
     ├──→ crud.py ──────── performs database operation
     │       │
     │       ├──→ models.py ──── knows the table structure
     │       │
     │       └──→ database.py ── provides the session
     │                │
     │                └──→ users.db ── the actual database file
     │
     └──→ schemas.py ──── filters output data (response_model)
              │
              ▼
       JSON Response to Client
```

**Why separate files instead of one big main.py?**

| Principle | Meaning | Benefit |
|-----------|---------|---------|
| Separation of Concerns | Each file has ONE job | Easier to find and fix bugs |
| Single Responsibility | `crud.py` only does DB ops, `schemas.py` only validates | Changes in one don't break others |
| Scalability | Adding a new table = new model + new schema + new crud | No need to touch existing code |
| Team Work | Two developers can work on `crud.py` and `schemas.py` simultaneously | No merge conflicts |

---

## 🔌 All Endpoints

| Method | Path | Description | Status Code | Request Body |
|--------|------|-------------|-------------|-------------|
| GET | `/` | Health check | 200 | None |
| POST | `/users` | Create a new user | **201** | UserCreate |
| GET | `/users` | List all users (paginated) | 200 | None |
| GET | `/users/search` | Filter/search users | 200 | None |
| GET | `/users/{user_id}` | Get one user by ID | 200 | None |
| PUT | `/users/{user_id}` | Full replacement update | 200 | UserUpdate |
| PATCH | `/users/{user_id}` | Partial update | 200 | UserPatch |
| DELETE | `/users/{user_id}` | Delete a user | 200 | None |

**Route ordering matters:**
`/users/search` MUST be defined before `/users/{user_id}` in `main.py`.
Otherwise FastAPI interprets `"search"` as a `user_id` and throws an error.

---

## 📊 All Four Pydantic Schemas

```text
UserCreate (POST)          UserUpdate (PUT)
├── name: str              ├── name: str
├── email: str             ├── email: str
├── age: int               ├── age: int
└── city: Optional[str]    └── city: Optional[str]

UserPatch (PATCH)          UserResponse (GET responses)
├── name: Optional[str]    ├── id: int          ← from database
├── email: Optional[str]   ├── name: str
├── age: Optional[int]     ├── email: str
└── city: Optional[str]    ├── age: int
    (all optional)         ├── city: Optional[str]
                           └── Config: from_attributes = True
```

**Why `from_attributes = True`?**
SQLAlchemy returns objects (`user.name`), not dictionaries (`user["name"]`).
This config tells Pydantic: "Read from object attributes."

---

## 📋 All 8 CRUD Functions

```text
crud.py Function          │ What It Does                      │ SQL Equivalent
──────────────────────────┼───────────────────────────────────┼──────────────────────────
get_user(db, user_id)     │ Find one user by ID               │ SELECT ... WHERE id = ?
get_user_by_email(db, e)  │ Find one user by email            │ SELECT ... WHERE email = ?
get_users(db, skip, limit)│ List users with pagination        │ SELECT ... OFFSET ? LIMIT ?
search_users(db, ...)     │ Filter by city/age/name           │ SELECT ... WHERE city ILIKE ?
create_user(db, user)     │ Add new user → commit → refresh   │ INSERT INTO users ...
update_user(db, id, data) │ Replace all fields → commit       │ UPDATE users SET ... WHERE id = ?
patch_user(db, id, data)  │ Update only sent fields → commit  │ UPDATE users SET ... WHERE id = ?
delete_user(db, id)       │ Remove user → commit              │ DELETE FROM users WHERE id = ?
```

---

## 🧪 Testing Commands Reference

### Setup (run once per terminal session)

```bash
source ~/IT_30day/venv/bin/activate
cd ~/IT_30day/day06
uvicorn main:app --reload
```

Open a second terminal tab for testing:

```bash
source ~/IT_30day/venv/bin/activate
```

### All Test Commands

```bash
# Health check
http GET http://127.0.0.1:8000/

# Create users (note: age uses := for integer)
http POST http://127.0.0.1:8000/users name="Ram Sharma" email="ram@test.com" age:=28 city="Kathmandu"
http POST http://127.0.0.1:8000/users name="Sita Thapa" email="sita@test.com" age:=24 city="Pokhara"
http POST http://127.0.0.1:8000/users name="Hari Khadka" email="hari@test.com" age:=35 city="Kathmandu"

# Duplicate email — should return 400
http POST http://127.0.0.1:8000/users name="Fake Ram" email="ram@test.com" age:=30

# Invalid age — should return 400
http POST http://127.0.0.1:8000/users name="Old" email="old@test.com" age:=150

# List all users
http GET http://127.0.0.1:8000/users

# Pagination
http GET "http://127.0.0.1:8000/users?skip=0&limit=2"

# Get one user
http GET http://127.0.0.1:8000/users/1

# User not found — should return 404
http GET http://127.0.0.1:8000/users/999

# Search by city
http GET "http://127.0.0.1:8000/users/search?city=Kathmandu"

# Search by age range
http GET "http://127.0.0.1:8000/users/search?min_age=25&max_age=30"

# Search by name (case-insensitive)
http GET "http://127.0.0.1:8000/users/search?name=sita"

# Full update (PUT) — all fields required
http PUT http://127.0.0.1:8000/users/1 name="Ram B. Sharma" email="ram@test.com" age:=29 city="Lalitpur"

# Partial update (PATCH) — only changed fields
http PATCH http://127.0.0.1:8000/users/2 city="Biratnagar"

# Delete
http DELETE http://127.0.0.1:8000/users/3

# Verify deletion
http GET http://127.0.0.1:8000/users
```

### The Persistence Test (Most Important)

```bash
# 1. Stop server (Ctrl+C in uvicorn tab)
# 2. Restart server
uvicorn main:app --reload
# 3. Check data — it should still be there!
http GET http://127.0.0.1:8000/users
```

If users are still there → database is working. This was impossible on Day 05.

### HTTPie Syntax Reminder

```text
=   → sends a string       name="Ram"       → {"name": "Ram"}
:=  → sends a number/bool  age:=28          → {"age": 28}
```

---

## ⚠️ Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `500 Internal Server Error` | Check uvicorn terminal for traceback | Read the last line of the traceback |
| `autocomit` typo → `TypeError` | Misspelled `autocommit` in database.py | Fix to `autocommit=False` |
| `value is not a valid dict` | Missing `from_attributes = True` in schema | Add `class Config: from_attributes = True` in UserResponse |
| `Table already exists` with wrong columns | Old `users.db` doesn't match current model | `rm -f users.db` and restart server |
| `422 Unprocessable Entity` | Wrong types in request (string instead of int) | Use `:=` for numbers in HTTPie |
| `ModuleNotFoundError: sqlalchemy` | SQLAlchemy not installed in venv | `pip install sqlalchemy` |
| Smart quotes breaking commands | Copied from a document/browser | Always type quotes manually in terminal |
| Permission denied on git | Files owned by root | `sudo chown -R $(whoami) ~/IT_30day/` |

---

## 🧠 Day 05 vs Day 06 — Code Comparison

### Finding a User

**Day 05 (in-memory list):**
```python
def find_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    return None
```

**Day 06 (database):**
```python
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
```

Day 05 loops through every user. Day 06 uses an indexed database query —
thousands of times faster on large datasets.

### Creating a User

**Day 05:**
```python
@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    global next_id
    new_user = user.dict()
    new_user["id"] = next_id
    next_id += 1
    users_db.append(new_user)
    return new_user
```

**Day 06:**
```python
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, email=user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)
```

Day 06 has: database persistence, automatic ID generation,
response filtering, dependency injection, and clean separation.

---

## 🔐 Security Practices Applied Today

| Practice | How We Applied It |
|----------|-------------------|
| `.gitignore` for `.db` files | Database with real data never goes to GitHub |
| `unique=True` on email column | Database-level duplicate prevention |
| `nullable=False` on required columns | Database rejects empty required fields |
| `response_model` filtering | Only expose intended fields to clients |
| `get_db()` with `try/finally` | Sessions always close — prevents resource leaks |
| Input validation at 2 layers | Pydantic (API) + SQLAlchemy constraints (DB) |

---

## 💼 Consultant Insights

### Insight #6 — Database Schema Quality
> Poorly designed database models are one of the most expensive
> technical debts a company can carry. Missing indexes = slow queries.
> Missing unique constraints = duplicate data. `nullable=True` on
> everything = no data integrity. A well-structured `models.py` signals
> professional engineering.

### Insight #7 — DRY with crud.py
> Separating database operations into `crud.py` follows the DRY principle.
> When you see a codebase where the same query is written in 5 different
> endpoints, that's a code quality red flag — and a consulting opportunity.

### Insight #8 — .gitignore as Security
> Not adding `.db` files to `.gitignore` exposes real data and reveals
> amateur practices. In an audit, checking `.gitignore` is one of the
> first things a security consultant does.

---

## ✅ End-of-Day Checklist

- [ ] Understand why in-memory lists fail for real apps
- [ ] Understand SQLite as a file-based database
- [ ] Understand ORM concept — Python instead of SQL
- [ ] Created `database.py` with engine, SessionLocal, get_db
- [ ] Created `models.py` with User table and constraints
- [ ] Created `schemas.py` with 4 Pydantic models
- [ ] Created `crud.py` with all 8 database functions
- [ ] Created `main.py` with all 8 endpoints
- [ ] Tested all CRUD operations with HTTPie
- [ ] Verified data persistence after server restart
- [ ] Tested case-insensitive search with ilike
- [ ] Tested duplicate email rejection
- [ ] Tested pagination with skip and limit
- [ ] Verified `.gitignore` excludes `.db` files
- [ ] Pushed to GitHub

---

## 🔮 What's Next — Day 07 Preview

Day 07 adds **table relationships**:

- A new `Task` model linked to `User` with a **foreign key**
- One-to-many: one user has many tasks
- `relationship()` and `back_populates` in SQLAlchemy
- Joined queries: get a user with all their tasks in one call
- Cascading deletes: deleting a user removes all their tasks
- Nested response schemas: tasks appear inside user responses

This is where your app starts to look like a real production system.
Every real application — e-commerce, banking, HR — is built on table relationships.