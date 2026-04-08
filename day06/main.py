from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

import models
from database import engine, get_db
from schemas import UserCreate, UserUpdate, UserPatch, UserResponse
import crud

# Create all database tables on startup
# This reads every class that inherits from Base and creates the table
# if it doesn't already exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Management API",
    description="A CRUD API with SQLite database — Day 06",
    version="1.0.0",
)


# Health check
@app.get("/")
def root():
    return {"status": "alive", "database": "SQLite", "day": "06"}


# CREATE — POST /users
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check for duplicate email
    existing = crud.get_user_by_email(db, email=user.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Email '{user.email}' is already registered",
        )

    # Validate age range
    if user.age < 0 or user.age > 120:
        raise HTTPException(
            status_code=400,
            detail="Age must be between 0 and 120",
        )

    return crud.create_user(db=db, user=user)


# READ — GET /users (with pagination)
@app.get("/users", response_model=list[UserResponse])
def read_users(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records"),
    db: Session = Depends(get_db),
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


# READ — GET /users/search (filtered search)
# IMPORTANT: This route MUST come before /users/{user_id}
# Otherwise FastAPI thinks "search" is a user_id
@app.get("/users/search", response_model=list[UserResponse])
def search_users(
    city: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    results = crud.search_users(
        db, city=city, min_age=min_age, max_age=max_age, name=name
    )
    return results


# READ — GET /users/{user_id}
@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# UPDATE — PUT /users/{user_id} (full replacement)
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, user: UserUpdate, db: Session = Depends(get_db)
):
    # Check if user exists
    existing = crud.get_user(db, user_id=user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")

    # Check email uniqueness (exclude current user)
    email_owner = crud.get_user_by_email(db, email=user.email)
    if email_owner and email_owner.id != user_id:
        raise HTTPException(
            status_code=400,
            detail=f"Email '{user.email}' is already taken by another user",
        )

    return crud.update_user(db=db, user_id=user_id, user_data=user)


# UPDATE — PATCH /users/{user_id} (partial update)
@app.patch("/users/{user_id}", response_model=UserResponse)
def patch_user(
    user_id: int, user: UserPatch, db: Session = Depends(get_db)
):
    existing = crud.get_user(db, user_id=user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")

    # Check email uniqueness if email is being updated
    if user.email is not None:
        email_owner = crud.get_user_by_email(db, email=user.email)
        if email_owner and email_owner.id != user_id:
            raise HTTPException(
                status_code=400,
                detail=f"Email '{user.email}' is already taken",
            )

    return crud.patch_user(db=db, user_id=user_id, user_data=user)


# DELETE — DELETE /users/{user_id}
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": f"User {user_id} deleted successfully"}