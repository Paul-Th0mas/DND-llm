"""
Static D&D 5e rules context block for world generation prompts.

This module contains one public function: get_dnd_rules_block(difficulty).

The returned string is a self-contained D&D 5e design ruleset that does not
change between requests (except for the difficulty-specific CR range and
treasure tier). It is kept separate from the per-run dynamic template so it
can be cached at the LLM layer independently.

To add a new rule category, append a new section below. Do not mix
per-run variable data into this file — that belongs in world_generation.py.
"""

from app.worlds.domain.models import Difficulty

# CR range and treasure guidance per difficulty tier.
# These map directly to D&D 5e's four tiers of play.
_CR_RANGES: dict[Difficulty, str] = {
    Difficulty.EASY: "CR 1/8 to CR 3 — Tier 1 party (levels 1–4)",
    Difficulty.NORMAL: "CR 1 to CR 8 — Tier 2 party (levels 5–10)",
    Difficulty.HARD: "CR 5 to CR 14 — Tier 3 party (levels 11–16)",
    Difficulty.NIGHTMARE: "CR 12 to CR 24 — Tier 4 party (levels 17–20)",
}

_TREASURE_TIERS: dict[Difficulty, str] = {
    Difficulty.EASY: (
        "common magic items — Potion of Healing, +1 ammunition, "
        "spell scroll of a cantrip or 1st-level spell"
    ),
    Difficulty.NORMAL: (
        "uncommon magic items — Bag of Holding, Cloak of Protection, "
        "Wand of Magic Missiles, Boots of Elvenkind"
    ),
    Difficulty.HARD: (
        "rare magic items — Flame Tongue, Staff of Fire, "
        "Robe of the Archmagi, Ring of Spell Storing"
    ),
    Difficulty.NIGHTMARE: (
        "very rare or legendary items — Vorpal Sword, Deck of Many Things, "
        "Talisman of Pure Good, Holy Avenger"
    ),
}


def get_dnd_rules_block(difficulty: Difficulty) -> str:
    """
    Return the full D&D 5e rules context block for the given difficulty.

    The block covers encounter balance, the three pillars of play, treasure,
    NPC design, and quest structure. All rules are positive reinforcement —
    they describe what good D&D design looks like, not just what to avoid.

    @param difficulty - The difficulty tier, used to inject the correct CR
                        range and treasure tier into the rules text.
    @returns A multi-line string ready to embed in a world generation prompt.
    """
    cr_range = _CR_RANGES[difficulty]
    treasure_tier = _TREASURE_TIERS[difficulty]

    return f"""D&D 5E DESIGN RULES — ENCOUNTER BALANCE:
- Enemy CR must match the difficulty setting: {cr_range}.
  Every named enemy in a COMBAT or BOSS room must have an implied CR that fits
  this range. If you reference a stat block, use the 2024 Monster Manual.
- COMBAT rooms must contain 2–4 enemies. Multiple enemies at lower CR create
  better action economy challenges than one overtuned solo creature.
- BOSS rooms must pair the named boss with 2–3 minions. A boss fought alone
  is trivial once the party focuses fire; minions force target priority decisions
  that make the encounter memorable.
- Vary enemy types across rooms: mix melee, ranged, and spellcasting enemies so
  each room demands a different tactical response from the party.

D&D 5E DESIGN RULES — THREE PILLARS OF PLAY:
Every dungeon must engage all three D&D pillars so every player type has moments
that matter to their character:
- COMBAT rooms: test fighting ability, spell slots, and action economy.
- EXPLORATION rooms (TREASURE, EVENT): test perception, investigation, problem-
  solving, and resource management. Include environmental details the party can
  interact with (levers, runes, locked containers, climbable terrain).
- SOCIAL rooms (SHOP, REST with an NPC): test roleplay, persuasion, and
  decision-making. Every NPC must have a visible goal and a hidden motive.

D&D 5E DESIGN RULES — TREASURE AND REWARDS:
- TREASURE rooms must specify loot using D&D categories: gold pieces (GP),
  consumable magic items (potions, spell scrolls), and one permanent magic item.
  Permanent item rarity must fit the difficulty tier: {treasure_tier}.
- Scale GP amounts with party size and dungeon depth. Early rooms yield 10–50 GP
  per party member; the final vault yields 5–10× that.
- Consumables should complement the party's expected challenges. A dungeon heavy
  in undead should include silvered weapons or Potions of Heroism, not random loot.

D&D 5E DESIGN RULES — NPC DESIGN:
- SHOP merchants are not vending machines. Give each one a name, a personality
  trait in one sentence, and a goal that is NOT purely financial. Merchants
  remember faces and can become recurring characters.
- REST room NPCs (if present) should offer a concrete mechanical benefit alongside
  their roleplay function: a short rest point, a healing font (restores 2d8+2 HP
  per character once per long rest), or a boon lasting until next long rest.
- Every named NPC must have a motivation that makes them take sides. Neutral NPCs
  with no stake in the outcome are forgettable. Even a merchant should want
  something from the party beyond gold.

D&D 5E DESIGN RULES — QUEST STRUCTURE:
- Quest stages must describe player actions, not story outcomes. Write each stage
  as an imperative: "Retrieve the warden's key from the guard captain" not
  "The party discovers the key exists."
- Each of the three quest stages should engage a different pillar: one combat
  challenge, one exploration challenge, one social or decision-point challenge.
  A quest that is three combat stages fails players who built social characters.
- The central quest conflict must have stakes the party can directly affect.
  The outcome must be contingent on what the players do — not something that
  resolves itself regardless of their choices."""
