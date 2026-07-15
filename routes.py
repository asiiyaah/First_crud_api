from fastapi import APIRouter, HTTPException,status,Body
from schemas import TaskCreate

router=APIRouter()

task_db=[
    {"id":1 ,"title":"Buy groceries", "done":False},
    {"id":2 ,"title":"Do homework", "done":True},
    {"id":3 ,"title":"Do the dishes", "done":False},
    {"id":4 ,"title":"Swimming practise", "done":False},
    {"id":5 ,"title":"Work out", "done":True}
]


@router.get("/tasks")
def get_tasks():
    return task_db

@router.get("/tasks/{task_id}")
def get_task_byid(task_id : int):
    for task in task_db:
        if task["id"]==task_id:
            return task
        
    raise HTTPException(status_code=404 , detail=f"error : Task {task_id} not found")

@router.post("/tasks",status_code=status.HTTP_201_CREATED)
def post_task(task_input : TaskCreate):

    next_id=max([task["id"] for task in task_db],default=0) + 1

    new_task={
        "id":next_id,
        "title":task_input.title,
        "done":False
    }    

    task_db.append(new_task)
    return new_task

