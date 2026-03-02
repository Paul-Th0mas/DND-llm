"""
SQLAlchemy implementation of CombatRepository.

Maps between ORM rows and domain objects in both directions.
All domain logic stays in the domain layer — this file only handles
persistence translation.
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.combat.domain.models import (
    ClassType,
    CombatEncounter,
    CombatStatus,
    Combatant,
    CombatantType,
    DieType,
    Equipment,
    HandType,
    StatusEffect,
    StatusEffectType,
)
from app.combat.domain.repositories import CombatRepository
from app.combat.infrastructure.orm_models import CombatantORM, CombatEncounterORM

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Typed helpers for reading JSON dict values stored as `dict[str, object]`.
# isinstance narrowing is used so mypy can verify the return types.
# ---------------------------------------------------------------------------


def _ts_int(d: dict[str, object], key: str, default: int = 0) -> int:
    """Read an int from a JSON turn-state dict, falling back to `default`."""
    v = d.get(key, default)
    return v if isinstance(v, int) else default


def _ts_list(d: dict[str, object], key: str) -> list[int]:
    """Read a list[int] from a JSON turn-state dict, falling back to []."""
    v = d.get(key, [])
    if isinstance(v, list):
        return [x for x in v if isinstance(x, int)]
    return []


class SqlAlchemyCombatRepository(CombatRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, encounter_id: uuid.UUID) -> CombatEncounter | None:
        logger.debug("get_by_id: encounter_id=%s", encounter_id)
        enc_stmt = select(CombatEncounterORM).where(
            CombatEncounterORM.id == encounter_id
        )
        enc_row = self._session.execute(enc_stmt).scalar_one_or_none()
        if enc_row is None:
            return None

        comb_stmt = select(CombatantORM).where(
            CombatantORM.encounter_id == encounter_id
        )
        comb_rows = self._session.execute(comb_stmt).scalars().all()
        combatants = [self._combatant_to_domain(row) for row in comb_rows]

        return self._encounter_to_domain(enc_row, combatants)

    def save(self, encounter: CombatEncounter) -> None:
        logger.debug("save: encounter_id=%s", encounter.id)
        enc_orm = CombatEncounterORM(
            id=encounter.id,
            room_id=encounter.room_id,
            status_id=encounter.status.name,
            round=encounter.round,
            current_turn_index=encounter.current_turn_index,
            turn_order=[str(uid) for uid in encounter.turn_order],
            created_at=datetime.now(tz=timezone.utc),
        )
        self._session.merge(enc_orm)

        # Delete existing combatant rows and re-insert so merge handles
        # the JSON columns cleanly (avoids partial-update edge cases).
        del_stmt = delete(CombatantORM).where(CombatantORM.encounter_id == encounter.id)
        self._session.execute(del_stmt)

        for combatant in encounter.combatants:
            comb_orm = self._combatant_to_orm(combatant, encounter.id)
            self._session.add(comb_orm)

        self._session.flush()
        logger.debug("save: flushed encounter_id=%s", encounter.id)

    def delete(self, encounter_id: uuid.UUID) -> None:
        logger.debug("delete: encounter_id=%s", encounter_id)
        stmt = delete(CombatEncounterORM).where(CombatEncounterORM.id == encounter_id)
        self._session.execute(stmt)
        self._session.flush()

    # ------------------------------------------------------------------
    # Mapping helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _encounter_to_domain(
        row: CombatEncounterORM, combatants: list[Combatant]
    ) -> CombatEncounter:
        turn_order = [uuid.UUID(uid_str) for uid_str in row.turn_order]
        return CombatEncounter(
            id=row.id,
            room_id=row.room_id,
            combatants=combatants,
            round=row.round,
            turn_order=turn_order,
            current_turn_index=row.current_turn_index,
            status=CombatStatus[row.status_id],
        )

    @staticmethod
    def _combatant_to_domain(row: CombatantORM) -> Combatant:
        status_effects = [
            StatusEffect(
                effect_type=StatusEffectType[str(se["type_id"])],
                duration=_ts_int(se, "duration"),
            )
            for se in row.status_effects
        ]
        ts: dict[str, object] = row.turn_state if row.turn_state else {}
        equipment = Equipment(
            weapon=row.equipment.get("weapon"),
            armor=row.equipment.get("armor"),
            accessory=row.equipment.get("accessory"),
        )
        last_hand_raw = ts.get("last_hand_type")
        last_hand = HandType[str(last_hand_raw)] if last_hand_raw else None

        return Combatant(
            id=row.id,
            name=row.name,
            combatant_type=CombatantType[row.combatant_type_id],
            class_type=ClassType[row.class_type_id] if row.class_type_id else None,
            die_type=DieType[row.die_type_id],
            max_pool_size=row.max_pool_size,
            hp=row.hp,
            max_hp=row.max_hp,
            temp_hp=row.temp_hp,
            pool=list(row.pool),
            discard=list(row.discard),
            status_effects=status_effects,
            initiative=row.initiative,
            equipment=equipment,
            wild_tokens=row.wild_tokens,
            relics=list(row.relics),
            free_reroll_used=bool(ts.get("free_reroll_used", False)),
            second_wind_used=bool(ts.get("second_wind_used", False)),
            case_joint_used=bool(ts.get("case_joint_used", False)),
            sanctuary_used=bool(ts.get("sanctuary_used", False)),
            discordant_used=bool(ts.get("discordant_used", False)),
            fury_bonus_active=bool(ts.get("fury_bonus_active", False)),
            fury_chips_bonus=_ts_int(ts, "fury_chips_bonus"),
            fury_mult_bonus=_ts_int(ts, "fury_mult_bonus"),
            escalation_count=_ts_int(ts, "escalation_count"),
            last_hand_type=last_hand,
            trap_dice=_ts_list(ts, "trap_dice"),
            trap_trigger=str(ts.get("trap_trigger", "")),
            inspire_given=bool(ts.get("inspire_given", False)),
        )

    @staticmethod
    def _combatant_to_orm(
        combatant: Combatant, encounter_id: uuid.UUID
    ) -> CombatantORM:
        status_effects_json = [
            {"type_id": e.effect_type.name, "duration": e.duration}
            for e in combatant.status_effects
        ]
        equipment_json: dict[str, str | None] = {
            "weapon": combatant.equipment.weapon,
            "armor": combatant.equipment.armor,
            "accessory": combatant.equipment.accessory,
        }
        turn_state: dict[str, object] = {
            "free_reroll_used": combatant.free_reroll_used,
            "second_wind_used": combatant.second_wind_used,
            "case_joint_used": combatant.case_joint_used,
            "sanctuary_used": combatant.sanctuary_used,
            "discordant_used": combatant.discordant_used,
            "fury_bonus_active": combatant.fury_bonus_active,
            "fury_chips_bonus": combatant.fury_chips_bonus,
            "fury_mult_bonus": combatant.fury_mult_bonus,
            "escalation_count": combatant.escalation_count,
            "last_hand_type": (
                combatant.last_hand_type.name if combatant.last_hand_type else None
            ),
            "trap_dice": combatant.trap_dice,
            "trap_trigger": combatant.trap_trigger,
            "inspire_given": combatant.inspire_given,
        }
        return CombatantORM(
            id=combatant.id,
            encounter_id=encounter_id,
            name=combatant.name,
            combatant_type_id=combatant.combatant_type.name,
            class_type_id=combatant.class_type.name if combatant.class_type else None,
            die_type_id=combatant.die_type.name,
            max_pool_size=combatant.max_pool_size,
            hp=combatant.hp,
            max_hp=combatant.max_hp,
            temp_hp=combatant.temp_hp,
            pool=list(combatant.pool),
            discard=list(combatant.discard),
            status_effects=status_effects_json,
            initiative=combatant.initiative,
            wild_tokens=combatant.wild_tokens,
            equipment=equipment_json,
            relics=list(combatant.relics),
            turn_state=turn_state,
        )
