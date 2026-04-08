from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserUpdate, UserPatch


# READ — get one user by ID
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


# READ — get one user by email (for duplicate checking)
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# READ — get all users with pagination
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


# READ — search/filter users
def search_users(
    db: Session,
    city: str = None,
    min_age: int = None,
    max_age: int = None,
    name: str = None,
):
    query = db.query(User)

    if city:
        query = query.filter(User.city.ilike(f"%{city}%"))
    if min_age is not None:
        query = query.filter(User.age >= min_age)
    if max_age is not None:
        query = query.filter(User.age <= max_age)
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))

    return query.all()


# CREATE — add a new user
def create_user(db: Session, user: UserCreate):
    db_user = User(
        name=user.name,
        email=user.email,
        age=user.age,
        city=user.city,
    )
    db.add(db_user)       # Stage the new object
    db.commit()           # Save to disk
    db.refresh(db_user)   # Reload to get the auto-generated id
    return db_user


# UPDATE — full replacement (PUT)
def update_user(db: Session, user_id: int, user_data: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None

    db_user.name = user_data.name
    db_user.email = user_data.email
    db_user.age = user_data.age
    db_user.city = user_data.city

    db.commit()
    db.refresh(db_user)
    return db_user


# UPDATE — partial update (PATCH)
def patch_user(db: Session, user_id: int, user_data: UserPatch):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None

    # Only update fields that were actually sent
    if user_data.name is not None:
        db_user.name = user_data.name
    if user_data.email is not None:
        db_user.email = user_data.email
    if user_data.age is not None:
        db_user.age = user_data.age
    if user_data.city is not None:
        db_user.city = user_data.city

    db.commit()
    db.refresh(db_user)
    return db_user


# DELETE — remove a user
def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user