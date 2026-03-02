"""
FastAPI router for the worlds bounded context.

Five endpoints:
  POST   /worlds/compile                      → WorldSkeletonResponse (201) — DM only
  GET    /worlds/themes                       → list[str]              (200)
  GET    /worlds/{world_id}                   → WorldSkeletonResponse  (200)
  GET    /worlds/{world_id}/rooms/{n}         → DungeonRoomResponse    (200)
  POST   /worlds/{world_id}/rooms/{n}/narrate → NarrateRoomResponse   (200)

Routers are thin: validate input via Pydantic, delegate to a use case,
return the response.  No business logic lives here.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, status

from app.rooms.api.dependencies import get_dm_user
from app.users.domain.models import User
from app.worlds.api.dependencies import (
    get_narrator,
    get_preset_repository,
    get_theme_repository,
    get_world_compiler,
    get_world_skeleton_repository,
)
from app.worlds.application.schemas import (
    CompileWorldRequest,
    DungeonRoomResponse,
    NarrateRoomRequest,
    NarrateRoomResponse,
    WorldSkeletonResponse,
)
from app.worlds.application.use_cases import (
    CompileWorldUseCase,
    GetRoomUseCase,
    NarrateRoomUseCase,
    NarratorPort,
)
from app.worlds.domain.models import ThemeName, WorldSettings
from app.worlds.domain.repositories import (
    PresetRepository,
    ThemeRepository,
    WorldSkeletonRepository,
)
from app.worlds.domain.services import WorldCompiler

logger = logging.getLogger(__name__)

worlds_router = APIRouter(prefix="/worlds", tags=["worlds"])


@worlds_router.post(
    "/compile",
    response_model=WorldSkeletonResponse,
    status_code=status.HTTP_201_CREATED,
)
def compile_world(
    body: CompileWorldRequest,
    theme_repo: ThemeRepository = Depends(get_theme_repository),
    preset_repo: PresetRepository = Depends(get_preset_repository),
    world_repo: WorldSkeletonRepository = Depends(get_world_skeleton_repository),
    compiler: WorldCompiler = Depends(get_world_compiler),
    _current_user: User = Depends(get_dm_user),  # enforces DM-only access
) -> WorldSkeletonResponse:
    """
    Compile a themed dungeon world for the given room.

    Only Dungeon Masters may call this endpoint.
    Returns the compiled WorldSkeleton overview with 10-room structure.
    """
    logger.info(
        "POST /worlds/compile room_id=%s theme=%s difficulty=%s",
        body.room_id,
        body.theme.value,
        body.difficulty,
    )
    settings = WorldSettings(
        theme=body.theme,
        difficulty=body.difficulty,
        seed=body.seed,
    )
    use_case = CompileWorldUseCase(
        theme_repo=theme_repo,
        preset_repo=preset_repo,
        world_repo=world_repo,
        compiler=compiler,
    )
    return use_case.execute(settings=settings, room_id=body.room_id)


@worlds_router.get(
    "/themes",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
)
def list_themes() -> list[str]:
    """Return the list of supported theme names."""
    logger.info("GET /worlds/themes")
    return [t.value for t in ThemeName]


@worlds_router.get(
    "/{world_id}",
    response_model=WorldSkeletonResponse,
    status_code=status.HTTP_200_OK,
)
def get_world(
    world_id: uuid.UUID,
    world_repo: WorldSkeletonRepository = Depends(get_world_skeleton_repository),
) -> WorldSkeletonResponse:
    """Return the high-level overview of a compiled world."""
    logger.info("GET /worlds/%s", world_id)
    from app.worlds.domain.repositories import WorldNotFoundError

    skeleton = world_repo.get_by_id(world_id)
    if skeleton is None:
        raise WorldNotFoundError(f"World {world_id} not found")

    return WorldSkeletonResponse(
        id=skeleton.id,
        theme=skeleton.theme.name.value,
        difficulty=skeleton.settings.difficulty,
        room_count=len(skeleton.room_sequence),
        active_quests=[q.name for q in skeleton.active_quests],
    )


@worlds_router.get(
    "/{world_id}/rooms/{room_number}",
    response_model=DungeonRoomResponse,
    status_code=status.HTTP_200_OK,
)
def get_room(
    world_id: uuid.UUID,
    room_number: int,
    world_repo: WorldSkeletonRepository = Depends(get_world_skeleton_repository),
    preset_repo: PresetRepository = Depends(get_preset_repository),
) -> DungeonRoomResponse:
    """Return full detail for a specific dungeon room including enemy presets."""
    logger.info("GET /worlds/%s/rooms/%d", world_id, room_number)
    use_case = GetRoomUseCase(world_repo=world_repo, preset_repo=preset_repo)
    return use_case.execute(world_id=world_id, room_number=room_number)


@worlds_router.post(
    "/{world_id}/rooms/{room_number}/narrate",
    response_model=NarrateRoomResponse,
    status_code=status.HTTP_200_OK,
)
def narrate_room(
    world_id: uuid.UUID,
    room_number: int,
    body: NarrateRoomRequest,
    world_repo: WorldSkeletonRepository = Depends(get_world_skeleton_repository),
    narrator: NarratorPort = Depends(get_narrator),
) -> NarrateRoomResponse:
    """
    Generate themed narrative text for a room.

    Falls back to the room's lore_seed text when the LLM narrator is unavailable.
    """
    logger.info("POST /worlds/%s/rooms/%d/narrate", world_id, room_number)
    use_case = NarrateRoomUseCase(world_repo=world_repo, narrator=narrator)
    return use_case.execute(
        world_id=world_id,
        room_number=room_number,
        game_state=body.game_state,
    )
