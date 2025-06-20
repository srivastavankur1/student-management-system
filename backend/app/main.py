from fastapi import FastAPI
from app.routes import student, auth
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
def serve_login():
    return "static/login.html"

@app.get("/summarizer", response_class=FileResponse)
def serve_summarizer():
    return "static/summarizer.html"

app.include_router(student.router)
app.include_router(auth.router)
