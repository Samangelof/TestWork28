from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_active_user
from app.users.models import User
from app.tasks import schemas, services


router = APIRouter(tags=["tasks"])


@router.post("", response_model=schemas.Task)
def create_task(
    task_in: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    """Создание новой задачи"""
    return services.create_new_task(db=db, task_data=task_in, owner_id=current_user.id)


@router.get("", response_model=List[schemas.Task])
def read_tasks(
    status: Optional[schemas.TaskStatus] = None,
    priority: Optional[int] = None,
    created_after: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    """Получение списка задач с фильтрацией"""
    return services.get_user_tasks(
        db=db,
        current_user_id=current_user.id,
        status=status.value if status else None,
        priority=priority,
        created_after=created_after,
        skip=skip,
        limit=limit
    )


@router.get("/search", response_model=schemas.TaskSearchResults)
def search_tasks(
    q: str = Query(..., min_length=1),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    """Поиск задач по названию или описанию"""
    return services.search_user_tasks(
        db=db,
        current_user_id=current_user.id,
        query_str=q,
        skip=skip,
        limit=limit
    )


@router.get("/{task_id}", response_model=schemas.Task)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    """Получение задачи по ID"""
    return services.get_task_by_id(db=db, task_id=task_id, current_user_id=current_user.id)


@router.put("/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    """Обновление задачи по ID"""
    return services.update_user_task(
        db=db,
        task_id=task_id,
        task_update=task_update,
        current_user_id=current_user.id
    )


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    """Удаление задачи по ID"""
    services.delete_user_task(db=db, task_id=task_id, current_user_id=current_user.id)
    return None