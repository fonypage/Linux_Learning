import os
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src import models, schemas
from src.database import init_db, get_db

app = FastAPI()

APP_PREFIX = os.getenv("APP_PREFIX", "").strip().rstrip("/")
router = APIRouter(prefix=APP_PREFIX)

@app.on_event("startup")
async def startup():
    await init_db()

@router.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user_obj = models.User(name=user.name)
    db.add(user_obj)
    await db.commit()
    await db.refresh(user_obj)
    return user_obj

@router.get("/users/", response_model=list[schemas.User])
async def read_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User))
    return result.scalars().all()

@router.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user_obj = result.scalar_one_or_none()
    if user_obj is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_obj

@router.patch("/users/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    db_user = result.scalar_one_or_none()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.name = user.name
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(db_user)
    await db.commit()
    return {"detail": "User deleted"}

app.include_router(router)
