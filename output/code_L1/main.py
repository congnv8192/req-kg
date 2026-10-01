from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

BASE_PATH = "/api/v1"


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"
    priority: str = "medium"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str


tasks: Dict[int, Task] = {}
next_task_id = 1


@app.post(f"{BASE_PATH}/tasks", response_model=Task)
def create_task(task: TaskCreate):
    global next_task_id

    created_task = Task(id=next_task_id, **task.model_dump())
    tasks[next_task_id] = created_task
    next_task_id += 1
    return created_task


@app.get(f"{BASE_PATH}/tasks", response_model=List[Task])
def list_tasks():
    return list(tasks.values())


@app.get(f"{BASE_PATH}/tasks/{{task_id}}", response_model=Task)
def get_task(task_id: int):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put(f"{BASE_PATH}/tasks/{{task_id}}", response_model=Task)
def replace_task(task_id: int, task: TaskCreate):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    updated_task = Task(id=task_id, **task.model_dump())
    tasks[task_id] = updated_task
    return updated_task


@app.patch(f"{BASE_PATH}/tasks/{{task_id}}", response_model=Task)
def update_task(task_id: int, task: TaskUpdate):
    existing_task = tasks.get(task_id)
    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    updated_data = existing_task.model_dump()
    updated_data.update(task.model_dump(exclude_unset=True))
    updated_task = Task(**updated_data)
    tasks[task_id] = updated_task
    return updated_task


@app.delete(f"{BASE_PATH}/tasks/{{task_id}}")
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    del tasks[task_id]
    return {"detail": "Task deleted"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)