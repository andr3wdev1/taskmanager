from fastapi import APIRouter, HTTPException, Depends

from app.schemas.tasks import TaskUpdate, TaskCreate, TaskResponse, MessageResponse

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_session
from app.models import Task

router = APIRouter()

@router.get("/tasks", response_model=list[TaskResponse])
def get_tasks(session: Session = Depends(get_session)):
    statement = select(Task)
    result = session.execute(statement)
    tasks = result.scalars().all()
    return tasks

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found...")

    return task

@router.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    new_task = Task(
        title=task.title,
        is_completed = task.is_completed,
        )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return new_task


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, changes: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if changes.title is not None:
        task.title = changes.title
    if changes.is_completed is not None:
        task.is_completed = changes.is_completed
    session.commit()
    session.refresh(task)
    return task
 

        

@router.delete("/tasks/{task_id}", response_model=MessageResponse)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found...")
    session.delete(task)
    session.commit()
    return {"message": "succesfull"}
    








