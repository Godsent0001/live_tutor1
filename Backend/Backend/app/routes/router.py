# app/routes/router.py

from fastapi import APIRouter

from app.routes.lesson import router as lesson_router
from app.routes.response import router as response_router
from app.routes.session import router as session_router
from app.routes.user import router as user_router
from app.routes.module_qa import router as module_qa_router

router = APIRouter()

router.include_router(user_router, prefix="/users", tags=["Users"])
router.include_router(lesson_router, prefix="/lessons", tags=["Lessons"])
router.include_router(session_router, prefix="/sessions", tags=["Sessions"])
router.include_router(response_router, prefix="/responses", tags=["Responses"])
router.include_router(module_qa_router, prefix="/modules", tags=["Module Q&A"])
