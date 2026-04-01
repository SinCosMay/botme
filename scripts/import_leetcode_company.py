import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_ROOT = os.path.join(ROOT, "backend")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.leetcode_service import import_leetcode_problems


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import LeetCode company-wise problems from JSON")
    parser.add_argument("--input", required=True, help="Path to JSON file containing 'problems' array")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        payload = json.load(f)

    problems = payload.get("problems", payload if isinstance(payload, list) else [])

    db: Session = SessionLocal()
    try:
        inserted, updated = import_leetcode_problems(db, problems)
    finally:
        db.close()

    print(f"Inserted={inserted}, Updated={updated}")
