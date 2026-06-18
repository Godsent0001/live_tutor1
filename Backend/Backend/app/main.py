# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings

from app.routes.router import router

from app.middleware.error_handler import (
    ErrorHandler
)

# Optional
# from app.middleware.auth_middleware import (
#     AuthMiddleware
# )


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# AUTH
# ----------------------------
# Uncomment later when ready
#
# app.add_middleware(
#     AuthMiddleware
# )

# ----------------------------
# ERROR HANDLERS
# ----------------------------
app.add_exception_handler(
    RequestValidationError,
    ErrorHandler.validation_exception_handler
)

app.add_exception_handler(
    Exception,
    ErrorHandler.general_exception_handler
)

# ----------------------------
# ROUTES
# ----------------------------
app.include_router(router)

# ----------------------------
# HEALTH CHECK
# ----------------------------
@app.get("/")
def root():

    return {
        "success": True,
        "message": "Live Tutor API Running",
        "version": settings.APP_VERSION
    }


@app.get("/health")
def health():

    return {
        "success": True,
        "status": "healthy"
    }