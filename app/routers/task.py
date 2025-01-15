from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
async def all_task(db: Annotated[Session, Depends(get_db)]):
    task = db.scalars(select(User)).all()
    return task


@router.get('/task_id')
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalars(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task was not found')
    return task



@router.post('/create')
async def update_task(db: Annotated[Session, Depends(get_db)], create_task: CreateTask, user_id: int):
    user = db.scalars(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')
    db.execute(insert(Task).values(title=create_task.title,
                                   content=create_task.content,
                                   priority=create_task.priority,
                                   user_id=user_id,
                                   slug=slugify(create_task.title)))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED,'transaction': 'Successful'}


@router.put('/update')
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int, updated_user: UpdateTask):
    query = select(Task).where(Task.id == task_id)
    task = db.scalars(query)
    if task:
        db.execute(update(Task).where(Task.id == task_id).values(
            title=update_task.title,
            content=update_task.content,
            priority=update_task.priority,
            user_id=updated_user.user_id,))
        db.commit()
        return {'status_code': status.HTTP_200_OK}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task was not found')



@router.delete('/delete')
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    query = select(Task).where(Task.id == task_id)
    task = db.scalars(query)
    if task:
        db.execute(delete(Task).where(Task.id == task_id))
        db.commit()
        return {'status_code': status.HTTP_200_OK}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task was not found')
