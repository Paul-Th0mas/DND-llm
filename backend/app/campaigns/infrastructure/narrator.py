"""
Campaign world narration infrastructure.

StubCampaignNarrator — deterministic D&D 5e-flavored world templates.
No LLM calls. Output is based on campaign tone and name so the same
campaign always produces the same world.

To add a real LLM narrator: implement CampaignNarratorPort in a new class
here (e.g. ClaudeCampaignNarrator), then swap it in api/dependencies.py.
"""

import logging
import uuid
from datetime import datetime, timezone

from app.campaigns.application.narrator_port import CampaignNarratorPort
from app.campaigns.domain.models import Campaign, CampaignTone
from app.campaigns.domain.world_models import (
    AdventureHook,
    CampaignNPC,
    CampaignWorld,
    Faction,
    Settlement,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Static templates keyed by CampaignTone
# ---------------------------------------------------------------------------

_WORLD_NAMES: dict[CampaignTone, list[str]] = {
    CampaignTone.DARK_FANTASY: [
        "The Ashenmere Reaches",
        "The Sunken Marches of Valdris",
        "Kingdom of the Shattered Crown",
        "The Grey Vale of Mournfeld",
    ],
    CampaignTone.HIGH_FANTASY: [
        "The Verdant Kingdoms of Aeloria",
        "The Shining Coast of Sunhaven",
        "The Golden Expanse of Talindra",
        "The Realm of Brightwater",
    ],
    CampaignTone.HORROR: [
        "The Bloodmist Moors",
        "The Hollow of Whispered Names",
        "The Darkveil Reaches",
        "The Ossuary Coast",
    ],
    CampaignTone.POLITICAL_INTRIGUE: [
        "The Free Cities of the Tiber Confluence",
        "The Imperial Marchlands",
        "The Grand Duchy of Elsinore",
        "The Merchants' Republic of Caledrus",
    ],
    CampaignTone.SWASHBUCKLING: [
        "The Shattered Isles of the Amber Sea",
        "The Wild Coast and the Corsair Reaches",
        "The Jeweled Ports of the Storm Gulf",
        "The Free Harbors of Saltmere",
    ],
}

_PREMISES: dict[CampaignTone, str] = {
    CampaignTone.DARK_FANTASY: (
        "A once-prosperous valley kingdom where the royal bloodline was shattered "
        "by a necromantic coup. The surviving heir hides among common folk while "
        "undead legions slowly encroach from the fallen capital."
    ),
    CampaignTone.HIGH_FANTASY: (
        "A golden age of peace is threatened by the reawakening of an ancient evil "
        "sealed away by the first heroes of legend. The party must recover the "
        "shards of the Sundering Seal before the darkness breaks free."
    ),
    CampaignTone.HORROR: (
        "Something has gone wrong in the village of Thornwall. People vanish without "
        "trace, the nights grow longer, and a growing dread whispers that whatever "
        "lurks in the moors is only getting closer."
    ),
    CampaignTone.POLITICAL_INTRIGUE: (
        "Three noble houses circle a vacant throne, each with a plausible claim and "
        "an army ready to march. The party holds a secret that could crown a monarch "
        "— or topple one — and every faction wants it."
    ),
    CampaignTone.SWASHBUCKLING: (
        "A legendary treasure map has surfaced at a portside auction, and every "
        "pirate lord, merchant prince, and naval commodore wants it. The party got "
        "there first — now they just have to survive long enough to spend the gold."
    ),
}

_SETTLEMENTS: dict[CampaignTone, Settlement] = {
    CampaignTone.DARK_FANTASY: Settlement(
        name="Thornwall",
        population=850,
        governance="Elected Reeve",
        description=(
            "A market town built around an ancient wall of thorned black stone "
            "that predates recorded history. The locals refuse to speak of what "
            "the wall was built to keep out."
        ),
    ),
    CampaignTone.HIGH_FANTASY: Settlement(
        name="Sunhaven",
        population=2400,
        governance="Council of Guilds",
        description=(
            "A prosperous trade town at the confluence of two rivers, known for "
            "its floating market and the gleaming Spire of Mages that watches "
            "over all from the central hill."
        ),
    ),
    CampaignTone.HORROR: Settlement(
        name="Morrowfen",
        population=520,
        governance="Elder Council",
        description=(
            "A fog-bound fishing village at the edge of the moors. The streets "
            "are narrow, the houses shuttered before dusk, and the locals speak "
            "in hushed tones about the sounds that come from the marsh at night."
        ),
    ),
    CampaignTone.POLITICAL_INTRIGUE: Settlement(
        name="Caer Arvon",
        population=12000,
        governance="Lord Mayor (appointed by the Duke)",
        description=(
            "A dense walled city of towers and plazas, famous for its labyrinthine "
            "legal code and the three great guild halls that dominate its skyline. "
            "Power shifts daily and everyone is for sale."
        ),
    ),
    CampaignTone.SWASHBUCKLING: Settlement(
        name="Port Seradis",
        population=6000,
        governance="Harbormaster's Compact",
        description=(
            "A sun-soaked port built on three connected islands, famous for its "
            "open-air markets, its legendary rum, and its total lack of extradition "
            "treaties with anyone."
        ),
    ),
}

_FACTIONS: dict[CampaignTone, list[Faction]] = {
    CampaignTone.DARK_FANTASY: [
        Faction(
            name="The Ashen Brotherhood",
            goals="Restore the fallen king by any means — including necromancy.",
            public_reputation="Loyal veterans who guard the old ways.",
            hidden_agenda="Their leader is already undead and serves the lich.",
        ),
        Faction(
            name="The Order of the Gilded Seal",
            goals="Find the rightful heir and place them on the throne.",
            public_reputation="Noble knights committed to justice.",
            hidden_agenda="They have already found the heir and are using them as a puppet.",
        ),
        Faction(
            name="The Thornwall Reeve's Council",
            goals="Keep Thornwall neutral and safe from both sides.",
            public_reputation="Pragmatic local governors.",
            hidden_agenda="Secretly negotiating with the lich for a peace deal.",
        ),
    ],
    CampaignTone.HIGH_FANTASY: [
        Faction(
            name="The Arcane Conclave",
            goals="Recover the Sundering Seal shards for study.",
            public_reputation="Learned mages who advise the council.",
            hidden_agenda="One member believes releasing the ancient evil is key to greater power.",
        ),
        Faction(
            name="The Sunguard",
            goals="Protect the realm at any cost.",
            public_reputation="Heroic paladins of the sun deity.",
            hidden_agenda="Their leader is dying and will do anything to buy more time.",
        ),
        Faction(
            name="The Merchant Consortium",
            goals="Maintain trade routes and stability.",
            public_reputation="Wealthy benefactors of the realm.",
            hidden_agenda="They have been profiting from the chaos and don't want it to end.",
        ),
    ],
    CampaignTone.HORROR: [
        Faction(
            name="The Elder Council",
            goals="Preserve Morrowfen and its traditions at any cost.",
            public_reputation="Wise community leaders.",
            hidden_agenda="They made a pact with what lives in the moors three generations ago.",
        ),
        Faction(
            name="The Moor Wardens",
            goals="Patrol the edges of the moors and report disappearances.",
            public_reputation="Brave hunters and scouts.",
            hidden_agenda="Two of their number have already been replaced by something else.",
        ),
        Faction(
            name="The Pilgrims of the Long Road",
            goals="Find a relic they believe is hidden in the moors.",
            public_reputation="Religious travellers seeking a holy site.",
            hidden_agenda="Their faith requires a sacrifice — and the village will do.",
        ),
    ],
    CampaignTone.POLITICAL_INTRIGUE: [
        Faction(
            name="House Valdris",
            goals="Claim the throne through legitimate succession.",
            public_reputation="Noble and law-abiding claimants.",
            hidden_agenda="Their claim is forged. They know it. The party can find out.",
        ),
        Faction(
            name="House Mourne",
            goals="Prevent any single house from taking power — maintain the balance.",
            public_reputation="Neutral power brokers.",
            hidden_agenda="They want the throne for themselves but lack the votes right now.",
        ),
        Faction(
            name="The Merchant Guilds",
            goals="Keep trade flowing regardless of who rules.",
            public_reputation="Apolitical economic interests.",
            hidden_agenda="They have funded all three claimants simultaneously.",
        ),
    ],
    CampaignTone.SWASHBUCKLING: [
        Faction(
            name="The Iron Corsairs",
            goals="Find the treasure before anyone else and keep it.",
            public_reputation="Ruthless but honourable pirates.",
            hidden_agenda="Their captain already has a piece of the map stolen from the party.",
        ),
        Faction(
            name="The Harbormaster's Compact",
            goals="Maintain Port Seradis as neutral ground.",
            public_reputation="Fair mediators between factions.",
            hidden_agenda="The Harbormaster wants the treasure to buy her city's independence.",
        ),
        Faction(
            name="The Royal Naval Expeditionary Force",
            goals="Recover the treasure for the Crown.",
            public_reputation="Legitimate legal authority.",
            hidden_agenda="The Admiral is selling information to the corsairs on the side.",
        ),
    ],
}

_NPCS: dict[CampaignTone, list[CampaignNPC]] = {
    CampaignTone.DARK_FANTASY: [
        CampaignNPC(
            name="Reeve Marta Ashfeld",
            species="Human",
            role="Town leader and primary quest giver",
            personality="Pragmatic and tired, carrying a burden she never asked for.",
            secret="She knows where the heir is hiding.",
            stat_block_ref="MM 2025 Noble (CR 1/8)",
        ),
        CampaignNPC(
            name="Brother Edric",
            species="Human",
            role="Local priest, information broker",
            personality="Genial, talks too much, knows everyone's sins.",
            secret="He is Ashen Brotherhood — and has been for twenty years.",
            stat_block_ref="MM 2025 Priest (CR 2)",
        ),
        CampaignNPC(
            name="Sera of the Wandering Road",
            species="Half-Elf",
            role="Travelling merchant, occasional spy",
            personality="Cheerful, never answers a direct question directly.",
            secret="She is the heir.",
            stat_block_ref="MM 2025 Spy (CR 1)",
        ),
    ],
    CampaignTone.HIGH_FANTASY: [
        CampaignNPC(
            name="Archmage Sylara Windmere",
            species="Elf",
            role="Head of the Arcane Conclave",
            personality="Sharp, impatient, brilliantly wrong about several things.",
            secret="She has already found one shard and is studying it against orders.",
            stat_block_ref="MM 2025 Archmage (CR 12)",
        ),
        CampaignNPC(
            name="Commander Davan Brightshield",
            species="Human",
            role="Leader of the Sunguard",
            personality="Honourable, inspiring, slowly losing his mind to a curse.",
            secret="A devil offered him ten more years if he lets one shard fall into darkness.",
            stat_block_ref="MM 2025 Knight (CR 3)",
        ),
        CampaignNPC(
            name="Lira Quickfingers",
            species="Halfling",
            role="Guild runner and street-level informant",
            personality="Fast-talking, always hungry, fiercely loyal to those who treat her well.",
            secret="She knows where the second shard is — and has been paid to stay quiet.",
            stat_block_ref=None,
        ),
    ],
    CampaignTone.HORROR: [
        CampaignNPC(
            name="Elder Grist",
            species="Human",
            role="Head of the Elder Council",
            personality="Grandfatherly and warm, with cold eyes.",
            secret="He feeds the moors' entity one villager per year to keep the rest safe.",
            stat_block_ref="MM 2025 Cultist (CR 1/8)",
        ),
        CampaignNPC(
            name="Warden Calla",
            species="Human",
            role="Leader of the Moor Wardens",
            personality="Precise, brave, increasingly frightened.",
            secret="She has seen what replaced two of her scouts. She has said nothing.",
            stat_block_ref="MM 2025 Scout (CR 1/2)",
        ),
        CampaignNPC(
            name="The Pilgrim Known as Ash",
            species="Unknown",
            role="Leader of the pilgrims",
            personality="Serene, speaks in riddles, smells faintly of rot.",
            secret="Not human. Has been waiting in this form for forty years.",
            stat_block_ref="MM 2025 Cult Fanatic (CR 2)",
        ),
    ],
    CampaignTone.POLITICAL_INTRIGUE: [
        CampaignNPC(
            name="Lord Edwyn Valdris",
            species="Human",
            role="Head of House Valdris",
            personality="Charming, eloquent, constitutionally incapable of a straight answer.",
            secret="His succession documents were forged by his mother — he never knew.",
            stat_block_ref="MM 2025 Noble (CR 1/8)",
        ),
        CampaignNPC(
            name="Chancellor Vassa Mourne",
            species="Human",
            role="Head of House Mourne",
            personality="Cold, calculating, never says anything she doesn't mean.",
            secret="She has a signed warrant for the throne that pre-dates all other claims.",
            stat_block_ref="MM 2025 Mage (CR 6)",
        ),
        CampaignNPC(
            name="Guildmaster Pell",
            species="Dwarf",
            role="Head of the Merchant Guilds",
            personality="Jovial, generous, keeps meticulous accounts of every favour.",
            secret="He is blackmailing two of the three house leaders.",
            stat_block_ref=None,
        ),
    ],
    CampaignTone.SWASHBUCKLING: [
        CampaignNPC(
            name="Captain Riven Seadark",
            species="Human",
            role="Leader of the Iron Corsairs",
            personality="Bold, honourable in his own way, never breaks a deal he made first.",
            secret="He has part of the treasure map already and has been shadowing the party.",
            stat_block_ref="MM 2025 Bandit Captain (CR 2)",
        ),
        CampaignNPC(
            name="Harbormaster Zada",
            species="Half-Orc",
            role="Ruler of Port Seradis",
            personality="Direct, fair, deeply calculating beneath the warmth.",
            secret="She wants to use the treasure to buy out the Crown's claim on her port.",
            stat_block_ref="MM 2025 Noble (CR 1/8)",
        ),
        CampaignNPC(
            name="Pip the Chart-Reader",
            species="Gnome",
            role="Map scholar and accidental expert on the treasure's location",
            personality="Scattered, brilliant, terrified he is in over his head (he is).",
            secret="He can read the full map — and has. He knows exactly where it leads.",
            stat_block_ref=None,
        ),
    ],
}

_CONFLICTS: dict[CampaignTone, str] = {
    CampaignTone.DARK_FANTASY: (
        "A lich-king has shattered the realm's ruling bloodline and now advances "
        "with an undead army. The last heir must be found and crowned before "
        "the capital falls — but powerful factions on both sides want that heir "
        "for their own ends."
    ),
    CampaignTone.HIGH_FANTASY: (
        "An ancient evil sealed by the first heroes is breaking free. Three shards "
        "of the Sundering Seal must be recovered and reunited before the seal "
        "fails entirely — but each shard has already been claimed by a different faction."
    ),
    CampaignTone.HORROR: (
        "Something in the moors has been feeding on Morrowfen for generations, "
        "protected by a pact the Elder Council struck in secret. Now the price "
        "is rising, and the entity's patience is nearly exhausted."
    ),
    CampaignTone.POLITICAL_INTRIGUE: (
        "Three noble houses contest a vacant throne, each with a plausible claim "
        "and an army waiting to march. The party holds a secret that could end the "
        "contest — but every faction is willing to kill to control that secret."
    ),
    CampaignTone.SWASHBUCKLING: (
        "A legendary treasure has been located for the first time in two centuries. "
        "Pirates, naval officers, merchants, and at least one sea monster stand "
        "between the party and the prize — and the map is already in four pieces."
    ),
}

_HOOKS: dict[CampaignTone, list[AdventureHook]] = {
    CampaignTone.DARK_FANTASY: [
        AdventureHook(
            pillar="combat",
            hook="A patrol of undead soldiers has been spotted one day's ride from Thornwall. The Reeve offers payment for anyone who drives them back and scouts their origin.",
            connected_npc="Reeve Marta Ashfeld",
        ),
        AdventureHook(
            pillar="social",
            hook="Brother Edric invites the party to a private dinner and asks about their loyalties — testing whether they can be trusted with a dangerous secret.",
            connected_npc="Brother Edric",
        ),
        AdventureHook(
            pillar="exploration",
            hook="A merchant found dead on the road had a torn map sewn into her coat lining. The visible portion shows a route to the old capital — and a circled location marked 'heir'.",
            connected_npc="Sera of the Wandering Road",
        ),
    ],
    CampaignTone.HIGH_FANTASY: [
        AdventureHook(
            pillar="combat",
            hook="A shard of the Sundering Seal was being transported under Sunguard escort. The convoy was ambushed and only one wounded guard survived. The shard is gone.",
            connected_npc="Commander Davan Brightshield",
        ),
        AdventureHook(
            pillar="social",
            hook="Archmage Sylara offers a substantial contract to the party: recover an artefact from a ruined tower. She will not say what it is — only that it is urgently needed.",
            connected_npc="Archmage Sylara Windmere",
        ),
        AdventureHook(
            pillar="exploration",
            hook="Lira tips off the party about a sealed vault beneath the guild hall. It was sealed the same day the ancient evil was defeated. It has never been opened since.",
            connected_npc="Lira Quickfingers",
        ),
    ],
    CampaignTone.HORROR: [
        AdventureHook(
            pillar="exploration",
            hook="A child found at the moors' edge has no memory of where she has been for three days. She keeps drawing the same symbol — one that matches marks found on the missing villagers.",
            connected_npc=None,
        ),
        AdventureHook(
            pillar="social",
            hook="Warden Calla asks the party to quietly investigate two of her own scouts who have been acting strangely. She is too afraid to do it herself.",
            connected_npc="Warden Calla",
        ),
        AdventureHook(
            pillar="combat",
            hook="The pilgrims arrived three days ago and one of the Elder Council's granddaughters has gone missing since. The family begs the party to find her before dark.",
            connected_npc="Elder Grist",
        ),
    ],
    CampaignTone.POLITICAL_INTRIGUE: [
        AdventureHook(
            pillar="social",
            hook="Lord Valdris invites the party to a private reception and offers a retainer — but the terms of the contract contain three clauses that don't appear to be standard.",
            connected_npc="Lord Edwyn Valdris",
        ),
        AdventureHook(
            pillar="exploration",
            hook="A sealed document bearing the royal seal was intercepted by the guilds. Guildmaster Pell will share it — for a price. The document, if real, ends the succession dispute instantly.",
            connected_npc="Guildmaster Pell",
        ),
        AdventureHook(
            pillar="combat",
            hook="An assassin was caught in the Chancellor's quarters. She won't talk to the city guard. She will talk to the party — once — if they can reach her before she is executed at dawn.",
            connected_npc="Chancellor Vassa Mourne",
        ),
    ],
    CampaignTone.SWASHBUCKLING: [
        AdventureHook(
            pillar="social",
            hook="Harbormaster Zada summons the party privately. She has heard they came into possession of the map. She wants to make a deal before the Corsairs find out.",
            connected_npc="Harbormaster Zada",
        ),
        AdventureHook(
            pillar="combat",
            hook="Three Iron Corsair cutters were spotted following the party's ship out of port. Captain Seadark wants the map. He has not yet decided whether to ask nicely.",
            connected_npc="Captain Riven Seadark",
        ),
        AdventureHook(
            pillar="exploration",
            hook="Pip has decoded the map's second layer — there is a navigational cipher that only works at a specific set of ruins half a day's sail away. Someone has already been there recently.",
            connected_npc="Pip the Chart-Reader",
        ),
    ],
}


# ---------------------------------------------------------------------------
# StubCampaignNarrator
# ---------------------------------------------------------------------------


class StubCampaignNarrator(CampaignNarratorPort):
    """
    Template-based campaign world narrator with no LLM calls.

    Output is deterministic: the same Campaign always produces the same world.
    Templates are keyed by CampaignTone. When a real LLM narrator is ready,
    implement CampaignNarratorPort and swap in api/dependencies.py.
    """

    def generate_world(self, campaign: Campaign) -> CampaignWorld:
        """
        Generate a CampaignWorld from tone-based static templates.

        @param campaign - The Campaign aggregate with DM requirements.
        @returns A fully populated CampaignWorld ready for persistence.
        """
        logger.info(
            "StubCampaignNarrator generating world: tone=%s name='%s'",
            campaign.tone,
            campaign.name,
        )
        tone = campaign.tone

        # Pick world name deterministically using player_count as an offset
        name_pool = _WORLD_NAMES[tone]
        world_name = name_pool[campaign.player_count % len(name_pool)]

        world = CampaignWorld(
            world_id=uuid.uuid4(),
            campaign_id=campaign.id,
            world_name=world_name,
            premise=_PREMISES[tone],
            starting_settlement=_SETTLEMENTS[tone],
            factions=tuple(_FACTIONS[tone]),
            key_npcs=tuple(_NPCS[tone]),
            central_conflict=_CONFLICTS[tone],
            adventure_hooks=tuple(_HOOKS[tone]),
            created_at=datetime.now(tz=timezone.utc),
        )

        logger.debug(
            "StubCampaignNarrator complete: world_name=%s npcs=%d factions=%d",
            world_name,
            len(world.key_npcs),
            len(world.factions),
        )
        return world
