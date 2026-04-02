#my first api
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to my first API!", "status": "running"}

@app.get("/hello/{name}")
def say_hello(name: str):
    return  {"message" : f"Hello, {name}!", "from":"FastAPI"}

@app.get("/add/{a}/{b}")
def add_numbers(a: int, b: int):
    result = a + b
    return {"number_a": a, "number_b": b, "sum": result}

@app.get("/about")
def about():
    return{
        "api_name": "My First API",
        "version": "1.0",
        "developer": "Sudarshan",
        "built_with": "FastAPI+Python"
    }

@app.get("/users")
def get_users():
    users = [
        {"id": 1, "name": "Alice", "city": "Kathmandu"},
        {"id": 2, "name": "Bob", "city": "Pokhara"},
        {"id": 3, "name": "Carol", "city": "Lalitpur"}
    ]
    return{"Total Users ": len(users), "users:": users}

@app.get("/users/{UID}")
def get_user_ID_any(UID: int):
    users = {
        1: {"id": 1, "name": "Alice", "city": "Kathmandu"},
        2: {"id": 2, "name": "Bob", "city": "Pokhara"},
        3: {"id": 3, "name": "Carol", "city": "Lalitpur"}
    }
    if UID in users:
        return users[UID]
    return {"Error": f"User {UID} not found"}


