from fastapi import FastAPI, HTTPException

app=FastAPI(title="Task API")

task_db=[
    {"id":1 ,"title":"Buy groceries", "done":False},
    {"id":2 ,"title":"Do homework", "done":True},
    {"id":3 ,"title":"Do the dishes", "done":False},
    {"id":4 ,"title":"Swimming practise", "done":False},
    {"id":5 ,"title":"Work out", "done":True}
]

@app.get("/")
def read_root():
    return {"name":"Task API" , "version":"1.0", "endpoints":["/tasks"]}

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/tasks")
def get_tasks():
    return task_db

@app.get("/tasks/{task_id}")
def get_task_byid(task_id : int):
    for task in task_db:
        if task["id"]==task_id:
            return task
        
    raise HTTPException(status_code=404 , detail=f"error : Task {task_id} not found")
    

