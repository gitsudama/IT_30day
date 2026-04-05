#my first api
from fastapi import FastAPI, HTTPException
#from day04.utils.functions import readFile
from pydantic import BaseModel , EmailStr
from typing import Optional


app = FastAPI()

# In-memory storage for today (we add a real database on Day 06)
users_db = []
next_id = 1


# --- Pydantic Models ---

class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    city: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
    city: Optional[str] = None



@app.get("/")
def home():
    return {"message": "Welcome to my first API!", "status": "running"}

"""@app.get("/hello/{name}")
def say_hello(name: str):
    return  {"message" : f"Hello, {name}!", "from":"FastAPI"}

@app.get("/add/{a}/{b}")
def add_numbers(a: int, b: int):
    result = a + b
    return {"number_a": a, "number_b": b, "sum": result}
"""

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
    #users = readFile("users.json")
    return{"Total Users ": len(users_db), "users:": users_db}

@app.get("/users/{UID}")
def get_user_ID_any(UID: str):
    #users = readFile("users.json")
    if UID in users_db:
        return users_db[UID]
    return {"Error": f"User {UID} not found"}


@app.get("/users/search")
def search_users(city: Optional[str] = None, min_age: Optional[int] = None):
    results = users_db

    if city:
        results = [u for u in results if u.get("city", "").lower() == city.lower()]

    if min_age:
        results = [u for u in results if u["age"] >= min_age]

    return {"total": len(results), "users": results}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    return {"error": f"User with id {user_id} not found"}



@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    global next_id

    # Check if email already exists
    for existing in users_db:
        if existing["email"] == user.email:
            raise HTTPException(
                status_code=400,
                detail=f"Email {user.email} already registered"
            )

    # Check age is reasonable
    if user.age < 0 or user.age > 120:
        raise HTTPException(
            status_code=400,
            detail="Age must be between 0 and 120"
        )

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

@app.delete("/users/{user_id}", status_code=200)
def delete_user(user_id: int):
    for index, user in enumerate(users_db):
        if user["id"] == user_id:
            users_db.pop(index)
            return {"message": f"User {user_id} deleted successfully"}

    raise HTTPException(status_code=404, detail=f"User {user_id} not found")
