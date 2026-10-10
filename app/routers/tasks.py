from fastapi import APIRouter, HTTPException, Depends

from app.schemas.tasks import TaskUpdate, TaskCreate

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_session
from app.models import Task

router = APIRouter()

@router.get("/tasks")
def get_tasks(session: Session = Depends(get_session)):
    statement = select(Task)
    result = session.execute(statement)
    tasks = result.scalars().all()
    return tasks

@router.get("/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found...")

    return task

@router.post("/tasks")
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    new_task = Task(title=task.title)

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return new_task


@router.patch("/tasks/{task_id}")
def update_task(task_id: int, changes: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found...")
    if changes.title is not None:
        task.title = changes.title
    session.commit()
    return {"id": task.id, "title": task.title}
 

        

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found...")
    session.delete(task)
    session.commit()
    return {"message": "succesfull"}
    








