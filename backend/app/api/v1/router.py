from fastapi import APIRouter

from app.api.v1.endpoints import analytics, followup, health, leetcode, problems, submissions, users

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(problems.router, prefix="/problems", tags=["problems"])
router.include_router(submissions.router, prefix="/submissions", tags=["submissions"])
router.include_router(followup.router, prefix="/followup", tags=["followup"])
router.include_router(leetcode.router, prefix="/leetcode", tags=["leetcode"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
