from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime

from app.tasks import models, schemas


def create_task(db: Session, task: schemas.TaskCreate, owner_id: int) -> models.Task:
    db_task = models.Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        owner_id=owner_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks(
    db: Session, 
    owner_id: int, 
    skip: int = 0, 
    limit: int = 100,
    status: str = None,
    priority: int = None,
    created_after: datetime = None) -> List[models.Task]:
    query = db.query(models.Task).filter(models.Task.owner_id == owner_id)
    
    if status:
        query = query.filter(models.Task.status == status)
    
    if priority is not None:
        query = query.filter(models.Task.priority == priority)
    
    if created_after:
        query = query.filter(models.Task.created_at >= created_after)
    
    return query.offset(skip).limit(limit).all()


def search_tasks(
    db: Session, 
    owner_id: int, 
    query_str: str,
    skip: int = 0, 
    limit: int = 100) -> List[models.Task]:
    search = f"%{query_str}%"
    return db.query(models.Task).filter(
        models.Task.owner_id == owner_id,
        or_(
            models.Task.title.ilike(search),
            models.Task.description.ilike(search)
        )
    ).offset(skip).limit(limit).all()


def update_task(
    db: Session, 
    db_task: models.Task,
    task_update: schemas.TaskUpdate) -> models.Task:
    update_data = task_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, db_task: models.Task) -> None:
    db.delete(db_task)
    db.commit()


def count_tasks_by_status(db: Session, owner_id: int) -> dict:
    result = db.query(
        models.Task.status,
        func.count(models.Task.id)
    ).filter(
        models.Task.owner_id == owner_id
    ).group_by(models.Task.status).all()
    
    return {status: count for status, count in result}