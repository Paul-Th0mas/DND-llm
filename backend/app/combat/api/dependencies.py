"""
FastAPI dependency providers for the combat bounded context.

get_combat_repository — injects a request-scoped SQLAlchemy repository.
get_dice_roller       — injects the RandomDiceRoller singleton.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.combat.domain.repositories import CombatRepository
from app.combat.infrastructure.dice import RandomDiceRoller
from app.combat.infrastructure.repositories import SqlAlchemyCombatRepository
from app.db.session import get_db


def get_combat_repository(db: Session = Depends(get_db)) -> CombatRepository:
    """Provide a session-scoped combat repository."""
    return SqlAlchemyCombatRepository(db)


def get_dice_roller() -> RandomDiceRoller:
    """Provide the random dice roller (stateless — same instance is fine)."""
    return RandomDiceRoller()
