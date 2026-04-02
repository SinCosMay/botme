import argparse
import asyncio
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_ROOT = os.path.join(ROOT, "backend")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.codeforces_service import sync_problemset


async def run(limit: int | None) -> int:
    db: Session = SessionLocal()
    try:
        inserted = await sync_problemset(db, limit=limit)
        return inserted
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Codeforces problemset into DB")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    count = asyncio.run(run(args.limit))
    print(f"Inserted {count} Codeforces problems")
