from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .routes import chat, dashboard
from .data_loader import load_all_data
from .services.ml_forecast import ml_forecast  # this triggers model training
load_all_data()
app = FastAPI(title="Inventory Assistant with ML")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(chat.router, prefix="/api/chat")
app.include_router(dashboard.router, prefix="/api/dashboard")
frontend = os.path.join(os.path.dirname(__file__), "../../frontend")
if os.path.exists(frontend):
    app.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")
