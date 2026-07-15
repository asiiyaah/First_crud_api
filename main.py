from fastapi import FastAPI
from routes import router

app=FastAPI(title="Task API")

@app.get("/")
def read_root():
    return {"name":"Task API" , "version":"1.0", "endpoints":["/tasks"]}

@app.get("/health")
def health():
    return {"status":"ok"}


app.include_router(router)
