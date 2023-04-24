from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from os import path
from .routers import device, monitor, summary, backup, restore

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

script_dir = path.dirname(__file__) 

app.include_router(device.router)
app.include_router(monitor.router)
app.include_router(summary.router)
app.include_router(backup.router)
app.include_router(restore.router)

@app.get("/")
async def read_root():
    return {"Status": "Ok"}

