from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(User)).all()
    return user


@router.get('/user_id')
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

@router.get('/user_id/tasks')
async def task_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    tasks = db.scalars(select(Task).where(Task.user_id == user_id))
    return tasks



@router.post('/create')
async def create_user(new_user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    slug = slugify(new_user.username)
    user_data = new_user.dict()
    user_data['slug'] = slug

    try:
        db.execute(insert(User).values(user_data))
        db.commit()
        return {'status_code': status.HTTP_201_CREATED}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put('/update')
async def update_user(user_id: int, updated_user: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    query = select(User).where(User.id == user_id)
    user = db.scalars(query)
    if user:
        db.execute(update(User).where(User.id == user_id).values(updated_user.dict()))
        db.commit()
        return {'status_code': status.HTTP_200_OK}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')


@router.delete('/delete')
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    query = select(User).where(User.id == user_id)
    user = db.scalars(query)
    if user:
        db.execute(delete(User).where(User.id == user_id))
        db.execute(delete(Task).where(Task.user_id == user_id))
        db.commit()
        return {'status_code': status.HTTP_200_OK}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
