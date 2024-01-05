from fastapi import FastAPI
from .api.v1.api import api_router
from starlette.middleware import Middleware

from starlette.middleware.cors import CORSMiddleware
from .middleware.requestvalidator import ValidateRequestMiddleware


from src.celery_utils import create_celery_app
from fastapi.staticfiles import StaticFiles

origins = [
    "http://localhost:4200",
    "http://localhost:8080",
    "https://dev.auragold.in",
    "https://auragold.in",
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
    Middleware(ValidateRequestMiddleware),
]
# from .db.session import engine

# from .db.base import Base
# Base.metadata.create_all(bind=engine)


app = FastAPI(title="Aura Gold APIs", version="0.7", middleware=middleware)
app.mount("/static", StaticFiles(directory="src/templates"), name="static")

app.include_router(api_router)
app.celery_app = create_celery_app()

celery = app.celery_app


@app.get("/knockknock")
def root():
    return {"message": "Hello from Aura Gold"}
