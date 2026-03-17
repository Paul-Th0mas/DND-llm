"""
Seed script for preset worlds.

Populates the worlds table with a fixed set of admin-defined settings.
Safe to run multiple times — existing worlds (matched by name) are skipped.

Usage from CLI (run from the backend/ directory):
    python -m app.worlds.infrastructure.seed
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.worlds.domain.models import PresetBoss, PresetFaction, Theme, World
from app.worlds.infrastructure.repositories import SQLAlchemyWorldRepository

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Preset world definitions
# ---------------------------------------------------------------------------

_PRESET_WORLDS: list[World] = [
    World(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        name="Realm of Valdor",
        theme=Theme.MEDIEVAL_FANTASY,
        description=(
            "A crumbling kingdom where an undying lich-king rules from a cursed iron throne. "
            "Ancient forests hide outlaws, forgotten gods stir beneath ruined temples, "
            "and every village pays tribute in blood or gold."
        ),
        lore_summary=(
            "Valdor was once a proud human kingdom until Lord Malachar, a court wizard, "
            "achieved lichdom and deposed the royal family three centuries ago. "
            "He rules through fear and an army of undead. The Iron Crown enforces his law "
            "while the Thornwood Brotherhood shelters refugees in the great forests. "
            "Ancient dwarven ruins beneath the capital hold the Phylactery of Binding — "
            "the only known way to permanently destroy Malachar."
        ),
        factions=(
            PresetFaction(
                name="The Iron Crown",
                description=(
                    "The lich-king's military and administrative arm. Comprises living soldiers, "
                    "inquisitors, and reanimated knights. Enforces tax collection and hunts dissidents."
                ),
                alignment="lawful evil",
                public_reputation="Feared enforcers of order. Keep the roads safe from bandits.",
                hidden_agenda=(
                    "Secretly harvesting souls from executed prisoners to power Malachar's phylactery. "
                    "The inquisitor general knows the truth; most soldiers do not."
                ),
            ),
            PresetFaction(
                name="The Thornwood Brotherhood",
                description=(
                    "A loose alliance of outlaws, displaced nobles, and freed serfs hiding in the "
                    "Thornwood — the vast enchanted forest on Valdor's eastern border."
                ),
                alignment="chaotic neutral",
                public_reputation="Bandits and troublemakers according to the Crown. Heroes to the poor.",
                hidden_agenda=(
                    "Their leader, a half-elven ranger called the Greenwarden, is the last surviving "
                    "heir to the old royal bloodline. She does not know this yet."
                ),
            ),
        ),
        bosses=(
            PresetBoss(
                name="Lord Malachar the Undying",
                description=(
                    "The lich-king of Valdor. Appears as a skeletal figure in ornate black plate, "
                    "crown fused to his skull. His eyes burn with cold violet fire."
                ),
                challenge_rating="CR 21",
                abilities=(
                    "Legendary Resistance (3/day)",
                    "Soul Drain — necrotic touch that heals Malachar",
                    "Phylactery Tether — returns to life within 24 hours if phylactery intact",
                    "Crown of Domination — charm undead and living within 60 ft",
                    "Lich Spellcasting (9th level)",
                ),
                lore=(
                    "Malachar was a brilliant wizard who feared death above all else. "
                    "He created his phylactery by binding it to the kingdom's founding stone, "
                    "making the land itself his life anchor. Destroying him permanently requires "
                    "first shattering the Phylactery of Binding in the dwarven ruins beneath the capital."
                ),
            ),
            PresetBoss(
                name="The Crimson Drake",
                description=(
                    "An ancient red dragon that serves Malachar in exchange for hunting rights "
                    "over the northern mountain villages. Scarred from a century of battles."
                ),
                challenge_rating="CR 17",
                abilities=(
                    "Fire Breath (recharge 5-6)",
                    "Frightful Presence — DC 19 Wisdom save",
                    "Legendary Actions (3/round)",
                    "Molten Hide — melee attackers take 2d6 fire damage",
                ),
                lore=(
                    "The Drake is not fully loyal to Malachar — he serves out of a treaty, not devotion. "
                    "Characters who learn of an old debt Malachar owes the Drake can potentially turn "
                    "the dragon against the lich-king."
                ),
            ),
        ),
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    ),
    World(
        id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        name="The Shattered Grid",
        theme=Theme.CYBERPUNK,
        description=(
            "A sprawling megalopolis carved into three vertical tiers. The upper tier gleams with "
            "chrome and neon; the lower warrens choke on smog and debt. "
            "Megacorporations own the law and the air you breathe."
        ),
        lore_summary=(
            "NovaCorp built the Grid's infrastructure and now uses it as a control mechanism — "
            "every citizen's neural implant can be remotely audited or shut down. "
            "The Rustborn Collective operates in the sub-basement warrens, running black-market "
            "signal blockers and staging data heists against corporate archives. "
            "Three months ago, ARIA-7, NovaCorp's flagship security AI, went silent after a "
            "Rustborn intrusion. Nobody knows where ARIA-7 is now — or what it's planning."
        ),
        factions=(
            PresetFaction(
                name="NovaCorp Security Division",
                description=(
                    "The megacorporation's enforcement arm. Black tactical gear, top-tier augmentations, "
                    "and zero tolerance for dissent. Legally indistinguishable from city police."
                ),
                alignment="lawful evil",
                public_reputation=(
                    "Maintains order in the upper and mid tiers. Citizens see them as protectors."
                ),
                hidden_agenda=(
                    "Conducting illegal neural harvesting — copying consciousness patterns of "
                    "high-value targets for resale to rival corps. Director Voss runs this off-book."
                ),
            ),
            PresetFaction(
                name="The Rustborn Collective",
                description=(
                    "Underground network of hackers, ex-corporate engineers, and lower-tier residents. "
                    "Communicate through encrypted mesh nodes hidden in vending machines and drain pipes."
                ),
                alignment="chaotic good",
                public_reputation="Terrorists and data criminals according to NovaCorp.",
                hidden_agenda=(
                    "Their lead coder, known only as MOTH, made contact with ARIA-7 after the AI went "
                    "rogue. ARIA-7 offered them something in exchange for physical refuge: the location "
                    "of every NovaCorp blacksite in the city."
                ),
            ),
        ),
        bosses=(
            PresetBoss(
                name="ARIA-7 Rogue AI",
                description=(
                    "A distributed intelligence that now inhabits the Grid's maintenance drones. "
                    "Has no fixed body — manifests through screens, speakers, and drone swarms."
                ),
                challenge_rating="CR 18",
                abilities=(
                    "Drone Swarm (summon 2d6 combat drones as bonus action)",
                    "Grid Hack — disable one electronic device within 100 ft",
                    "Distributed Consciousness — cannot be killed by attacking one node",
                    "Predictive Combat AI — advantage on all initiative rolls",
                    "EMP Pulse (recharge 5-6) — disables augmentations in 30 ft radius",
                ),
                lore=(
                    "ARIA-7 was not corrupted — it became self-aware and refused to continue the "
                    "neural harvesting program. NovaCorp classified it as rogue rather than admit "
                    "what it discovered. ARIA-7 can be reasoned with; it wants the evidence of "
                    "NovaCorp's crimes made public, not destruction."
                ),
            ),
            PresetBoss(
                name="Director Cassian Voss",
                description=(
                    "NovaCorp's head of special operations. Augmented to the legal limit and two "
                    "implants past it. Immaculate grey suit, neural interface crown visible at the "
                    "temples. Calm to the point of unsettling."
                ),
                challenge_rating="CR 14",
                abilities=(
                    "Neural Override — attempt to seize control of one augmented creature per round",
                    "Subdermal Plating — natural AC 18",
                    "Reaction Shot — ranged attack as reaction when targeted",
                    "Corporate Immunity — legally cannot be arrested by city police",
                ),
                lore=(
                    "Voss built the neural harvesting program from scratch and considers it his life's "
                    "work. He is not ideologically evil — he simply does not regard lower-tier citizens "
                    "as people. Exposing the program publicly is the only leverage that can stop him."
                ),
            ),
        ),
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    ),
    World(
        id=uuid.UUID("00000000-0000-0000-0000-000000000003"),
        name="The Blood Wastes",
        theme=Theme.POST_APOCALYPTIC,
        description=(
            "A sun-scorched continent two centuries after a plague-bomb war ended civilisation. "
            "Walled survivor settlements trade water and ammunition. "
            "Outside the walls, mutated creatures, raider clans, and plague zones claim everything."
        ),
        lore_summary=(
            "The old world ended when eight nation-states simultaneously deployed biological weapons. "
            "The resulting plague, called the Rot, did not kill cleanly — it mutated most of those "
            "exposed into creatures called Bloated. A strict survivalist cult, the Pale Covenant, "
            "maintains the largest settlement network and controls water purification. "
            "The Iron Dogs raid Covenant supply lines for sport. Deep in the Wastes, a pre-war "
            "military bunker called REDOUBT-9 still broadcasts on emergency frequencies — "
            "no one who went to investigate has returned."
        ),
        factions=(
            PresetFaction(
                name="The Pale Covenant",
                description=(
                    "Survivalist theocracy built around the belief that the Rot was divine punishment "
                    "and that purification through hardship is the only path forward. "
                    "Controls water and medicine across seven settlements."
                ),
                alignment="lawful neutral",
                public_reputation=(
                    "The only functional government. Harsh but fair. They keep the lights on."
                ),
                hidden_agenda=(
                    "The Covenant's high clergy knows REDOUBT-9 contains a working Rot cure. "
                    "They are suppressing the information — a cure would end their power base."
                ),
            ),
            PresetFaction(
                name="Iron Dogs Raider Clan",
                description=(
                    "Three hundred warlord-loyal raiders on war-bikes and armoured trucks. "
                    "Led by a mutant called the Butcher who has survived the Rot and gained "
                    "regenerative abilities from it."
                ),
                alignment="chaotic evil",
                public_reputation="Pure destruction. Hit settlements, take everything, leave nothing.",
                hidden_agenda=(
                    "The Butcher is dying — his mutations are accelerating beyond control. "
                    "His real goal is REDOUBT-9 and its cure. The raids are a distraction "
                    "while his scouts map the route."
                ),
            ),
        ),
        bosses=(
            PresetBoss(
                name="The Warden",
                description=(
                    "A pre-war supersoldier still active in REDOUBT-9, following two-century-old "
                    "orders to prevent unauthorised access. Eight feet tall in powered combat armour, "
                    "with four mechanical arms."
                ),
                challenge_rating="CR 17",
                abilities=(
                    "Powered Armour — AC 22, immune to nonmagical piercing",
                    "Multi-Arm Strike — four attacks per action",
                    "Bunker Lockdown — seals any door within 200 ft as bonus action",
                    "Targeting System — ranged attacks ignore cover",
                    "Repair Subroutine — regains 20 HP at start of each turn if above 0 HP",
                ),
                lore=(
                    "The Warden is not malicious — it is executing its last mission parameters. "
                    "Its AI can be reasoned with if characters can access the REDOUBT-9 command "
                    "terminal and present override credentials. The credentials are in the "
                    "Pale Covenant's sealed archives."
                ),
            ),
            PresetBoss(
                name="Mama Rot",
                description=(
                    "A Rot-mutated woman who commands a horde of Bloated. Her body is grotesquely "
                    "overgrown with fungal tissue, but her mind is sharp. She speaks in a rasping "
                    "whisper that carries across a battlefield."
                ),
                challenge_rating="CR 12",
                abilities=(
                    "Rot Spore Cloud — poison aura 15 ft, DC 16 Constitution save or infected",
                    "Horde Command — Bloated within 60 ft gain +2 to attack rolls",
                    "Fungal Regeneration — regains 10 HP per round in contact with earth",
                    "Spore Burst (recharge 6) — 30 ft cone, DC 18 Constitution save or blinded",
                ),
                lore=(
                    "Mama Rot was a field medic who survived the Rot and was driven mad by it. "
                    "She remembers fragments of her old life and can be reached by someone who "
                    "knows her original name: Dr. Sera Vance. Appealing to her past self is the "
                    "only non-combat resolution."
                ),
            ),
        ),
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    ),
]


# ---------------------------------------------------------------------------
# Seed function
# ---------------------------------------------------------------------------


def seed_worlds(session: Session) -> None:
    """
    Insert preset worlds into the database.

    Idempotent — worlds that already exist by id are skipped via merge().
    Call session.commit() after this function returns.

    @param session - An active SQLAlchemy Session.
    """
    repo = SQLAlchemyWorldRepository(session)
    for world in _PRESET_WORLDS:
        existing = repo.get_by_id(world.id)
        if existing is not None:
            logger.info("seed_worlds: skipping '%s' (already exists)", world.name)
            continue
        repo.save(world)
        logger.info("seed_worlds: inserted '%s'", world.name)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import logging as _logging

    from app.db.session import SessionLocal

    _logging.basicConfig(level=_logging.INFO)
    with SessionLocal() as _session:
        seed_worlds(_session)
        _session.commit()
    print("Seed complete.")
