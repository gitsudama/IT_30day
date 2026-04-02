Fast API learning

GET
POST
PUT
DELETE


REST — The rules APIs follow

REST is not a technology — it's a **set of rules** for how APIs should behave. The key rules:

1. **Use URLs to identify resources** — `/users`, `/products`, `/orders`
2. **Use HTTP methods correctly** — GET to read, POST to create
3. **Be stateless** — every request contains all info needed, server remembers nothing
4. **Return JSON** — standard data format

To install virtual environment in the working directory

-python3 -m venv venv
-source venv/bin/activate


After install fastapi and uvicorn
-pip install fastapi uvicorn 

to check the installation type following in comand promt 
python3 -c "import fastapi; print('FastApi version:', fastapi.__version__)"

# My FastAPI Backend

A REST API built with FastAPI and Python.

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn
```

## Run
```bash
uvicorn main:app --reload
```

## Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | / | Home - API status |
| GET | /about | API information |
| GET | /hello/{name} | Greet by name |
| GET | /add/{a}/{b} | Add two numbers |
| GET | /users | List all users |
| GET | /users/{id} | Get user by ID |

## Docs
Visit http://127.0.0.1:8000/docs for interactive documentation.
