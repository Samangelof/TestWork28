from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.tasks import crud, schemas


def create_new_task(db: Session, task_data: schemas.TaskCreate, owner_id: int) -> schemas.Task:
    return crud.create_task(db=db, task=task_data, owner_id=owner_id)


def get_task_by_id(db: Session, task_id: int, current_user_id: int) -> schemas.Task:
    task = crud.get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if task.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой задаче")
    return task


def get_user_tasks(
    db: Session,
    current_user_id: int,
    status: str = None,
    priority: int = None,
    created_after: datetime = None,
    skip: int = 0,
    limit: int = 100) -> List[schemas.Task]:
    return crud.get_tasks(
        db=db,
        owner_id=current_user_id,
        status=status,
        priority=priority,
        created_after=created_after,
        skip=skip,
        limit=limit
    )


def search_user_tasks(
    db: Session,
    current_user_id: int,
    query_str: str,
    skip: int = 0,
    limit: int = 100) -> schemas.TaskSearchResults:
    tasks = crud.search_tasks(
        db=db,
        owner_id=current_user_id,
        query_str=query_str,
        skip=skip,
        limit=limit
    )
    return schemas.TaskSearchResults(
        results=tasks,
        count=len(tasks)
    )


def update_user_task(
    db: Session,
    task_id: int,
    task_update: schemas.TaskUpdate,
    current_user_id: int) -> schemas.Task:
    task = get_task_by_id(db=db, task_id=task_id, current_user_id=current_user_id)
    return crud.update_task(db=db, db_task=task, task_update=task_update)


def delete_user_task(db: Session, task_id: int, current_user_id: int) -> None:
    task = get_task_by_id(db=db, task_id=task_id, current_user_id=current_user_id)
    return crud.delete_task(db=db, db_task=task)