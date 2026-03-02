"""
Seed runner.

Usage:
    cd DND-Backend
    python -m seeds.run_seeds

Runs all three theme seeds in order.  Each seed is idempotent (uses merge),
so this script is safe to re-run after wiping and recreating the database.
"""

import sys
import os

# Ensure the DND-Backend package root is on sys.path when run as a script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from seeds.medieval_fantasy import seed as seed_medieval_fantasy
from seeds.cyberpunk import seed as seed_cyberpunk
from seeds.manhwa import seed as seed_manhwa


def main() -> None:
    session = SessionLocal()
    try:
        print("Running medieval_fantasy seed...")
        seed_medieval_fantasy(session)

        print("Running cyberpunk seed...")
        seed_cyberpunk(session)

        print("Running manhwa seed...")
        seed_manhwa(session)

        print("All seeds complete.")
    except Exception as exc:
        session.rollback()
        print(f"Seed failed: {exc}", file=sys.stderr)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
