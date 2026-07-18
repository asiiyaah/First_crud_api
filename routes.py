from fastapi import APIRouter, HTTPException,status,Body
from schemas import TaskCreate , TaskUpdate , TaskResponse
from typing import Any

router=APIRouter()

sample=[
    {"id":1 ,"title":"Buy groceries", "done":False},
    {"id":2 ,"title":"Do homework", "done":True},
    {"id":3 ,"title":"Do the dishes", "done":False},
    {"id":4 ,"title":"Swimming practise", "done":False},
    {"id":5 ,"title":"Work out", "done":True}
]

task_db=sample.copy()

@router.post("/reset")
def reset_tasks():
    global task_db
    task_db = sample.copy()

    return {
    "message": "Tasks reset successfully"
           }

@router.get("/stats")
def get_stats():
    total=len(task_db)
    done=sum([1 for task in task_db if task["done"]==True])
    return {
        "total":total,
        "done":done,
        "open":total-done
    }


@router.get("/tasks")
def get_tasks(done: bool | None = None, search: str | None = None):
    tasks = task_db

    # Filter by completion status
    if done is not None:
        tasks = [task for task in tasks if task["done"] == done]

    # Filter by title
    if search is not None:
        tasks = [
            task
            for task in tasks
            if search.lower() in task["title"].lower()
        ]

    return tasks

@router.get("/tasks/{field}")
def path_nd_query(field : str , id :int) -> dict[str , Any]:

    task=next((item for item in sample if item["id"]==id),None)

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id {id} not found!")
    
    if field not in task:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Field {field} doesnt exist for this task!")

    return {
            field : task[field]
    }


@router.get("/tasks/{task_id}",response_model=TaskResponse)
def get_task_byid(task_id : int):
    for task in task_db:
        if task["id"]==task_id:
            return task
        
    raise HTTPException(status_code=404 , detail=f"error : Task {task_id} not found")

@router.post("/tasks",status_code=status.HTTP_201_CREATED,response_model=TaskResponse)
def post_task(task_input : TaskCreate):

    next_id=max([task["id"] for task in task_db],default=0) + 1

    new_task={
        "id":next_id,
        "title":task_input.title,
        "done":False
    }    

    task_db.append(new_task)
    return new_task

@router.put("/tasks/{task_id}",response_model=TaskResponse)
def update_task(task_id : int , task_update_input : TaskUpdate):

    if task_update_input.title is None and task_update_input.done is None:
        raise HTTPException(status_code=400, detail="Empty body not allowed")

    for task in task_db:
        if task["id"] == task_id:
            if task_update_input.title is not None:
                task["title"]=task_update_input.title

            if task_update_input.done is not None:
                task["done"]=task_update_input.done

            return task
    
    raise HTTPException(status_code=404,detail="Task not found")
        
@router.delete("/tasks/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id : int):
    for index , task in enumerate(task_db):
        if task["id"]==task_id:
            task_db.pop(index)
            return
            
    raise HTTPException(status_code=404 , detail="Task not found")