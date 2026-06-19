import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._fields")

from pydantic import BaseModel
BaseModel.model_config = {'protected_namespaces': ()}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import auth, detect, history, uploads

app = FastAPI(
    title="Vehicle Detector",
    version="1.0.0",
    description="API для детекции транспортных средств с использованием YOLO"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(auth.router)
app.include_router(detect.router)
app.include_router(history.router)
app.include_router(uploads.router)   # для получения изображений из истории

@app.get("/")
async def root():
    return {"message": "Vehicle Detector API is running"}