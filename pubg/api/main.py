from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from pubg.api.config import Config
from pubg.api.router import router


def get_app() -> FastAPI:
    fast_app = FastAPI(
        title=Config.APP_NAME,
        version=Config.APP_VERSION,
    )
    fast_app.include_router(router)
    return fast_app


app = get_app()

# Adds in ability to log prometheus
Instrumentator().instrument(app).expose(app)

# Middleware function to add CORS headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (replace with specific origins as needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)
