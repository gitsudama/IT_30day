#Day 05 - Building a User Management API with FastAPI
from fastapi import FastAPI, HTTPException
#from day04.utils.functions import readFile
from pydantic import BaseModel , EmailStr
from typing import Optional


app = FastAPI(
    title = "Users CURD API",
    description = "A simple API to manage users with Create, Read, Update, and Delete operations.",
    version = "2.0",
)

# In-memory storage for today 
users_db = []
next_id = 1


# --- Pydantic Models ---

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

# --- Helper Functions ---

def find_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    return None

# --- create API Endpoints ---
@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    global next_id
    
    for existing_user in users_db:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail=f"Email {user.email} already registered.")
    if user.age < 0 or user.age > 120:
        raise HTTPException(status_code=400, detail=f"Age {user.age} is not valid. Must be between 0 and 120.")
        
    new_user = {
            "id": next_id,
            "name": user.name,
            "email": user.email,
            "age": user.age,
            "city": user.city
        }
    users_db.append(new_user)
    next_id += 1
    return {"message": "User created successfully", "user": new_user}
    
    #--- Get all users ---
@app.get("/users")
def get_all_users():
    return {"total": len(users_db), "users": users_db}

#--- search users ---
@app.get("/users/search")
def search_users(
    name: Optional[str] = None, 
    city: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    ):

    results = users_db

    if name:
        results = [user for user in results if name.lower() == user["name"].lower()]
    if city:
        results = [user for user in results if city.lower() == user["city"].lower()]
    if min_age is not None:
        results = [user for user in results if user["age"] >= min_age]
    if max_age is not None:
        results = [user for user in results if user["age"] <= max_age]

    return {"total": len(results), "users": results}

#--- Get user by ID ---
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = find_user(user_id)
    if not user:
        raise HTTPException(
            status_code = 404,
            detail = f"User with user ID {user_id} is not found"
        )
    return user

#--- Update user ID (PUT) ---
@app.put("/users/{user_id}")
def update_user(user_id: int, user_data: UserUpdate):
    user = find_user(user_id)
    if not user:
        raise HTTPException(
            status_code = 404,
            detail = f"User with ID {user_id} is not found"
        )
    for each_user in users_db:
        if each_user["email"] == user_data.email and each_user["id"] != user_id:
            raise HTTPException(
                status_code = 400,
                detail = f"Email {user_data.email} is already in use by another user"
            )
        
    if user_data.age < 0 or user_data.age > 120:
        raise HTTPException(
            status_code = 400,
            detail = f"human can not have {user_data.age}."
        )
    
    user["name"] = user_data.name
    user["email"] = user_data.email
    user["age"] = user_data.age
    user["city"] = user_data.city
    return {"message": "User updated successfully", "user": user}   

@app.patch("/users/{user_id}")
def patch_user(user_id : int, User_update_data: UserPatch):
    user_to_update = find_user(user_id)
    if not user_to_update:
        raise HTTPException(
            status_code = 404,
            detail = f"User with user ID {user_id} not found"
        )
    if User_update_data.name is not None:
        user_to_update["name"] = User_update_data.name 

    if User_update_data.email is not None:
        for user in users_db:
            if user["email"] == User_update_data.email and user["id"] != user_id:
                raise HTTPException(
                    status_code = 400,
                    detail = f"Email {User_update_data.email} is already used by another user"
                )
        user_to_update["email"] = User_update_data.email

    if User_update_data.age is not None:
        if User_update_data.age < 0 or User_update_data.age >120:
            raise HTTPException(
                status_code = 400,
                detail = f"Human age can not be {User_update_data.age}."
            )
        user_to_update["age"] = User_update_data.age

    if User_update_data.city is not None:
        user_to_update["city"]= User_update_data.city

    return {"message": "USer patched successfully", "User": user_to_update}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    for i, user in enumerate(users_db):
        if user["id"]== user_id:
            users_db.pop(i)
            return {"message":f"User {user_id} deleted successfully"}
    raise HTTPException(
        status_code = 404,
        detail = f"User with ID {user_id} not found"
    )
    