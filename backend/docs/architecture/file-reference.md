# File Reference

Maps every source file to its purpose. Use this when you know what you are looking for
but not where it lives.

---

```
app/
  core/
    config.py              Settings loaded from .env via pydantic-settings.
                           All configuration accessed through the `settings` singleton.
                           Declares GEMINI_API_KEY and FRONTEND_URL alongside database
                           and OAuth credentials.
    exceptions.py          Base domain exception hierarchy (DomainError, NotFoundError,
                           AuthenticationError). No HTTP knowledge here.
    error_handlers.py      Global FastAPI exception handlers registered in main.py.
                           Maps domain exceptions to HTTP status codes (404, 401, 400, 500).
                           All handlers return {"detail": "..."} for consistent client shape.

  db/
    base.py                SQLAlchemy DeclarativeBase. All ORM models inherit from Base.
                           Imports orm_models so Alembic can discover tables.
    session.py             Creates the engine and provides get_db() for dependency injection.

  api/
    v1/
      router.py            Top-level router. Includes all context routers.

  main.py                  FastAPI app creation. Adds SessionMiddleware. Registers global
                           exception handlers from core/error_handlers.py. Includes api_router.

  users/                   Authentication, user profiles, Google OAuth, JWT.
    domain/
      events.py            UserRegisteredViaGoogle domain event.
      models.py            Email (value object), GoogleID (value object), User (aggregate root).
      repositories.py      UserRepository (abstract interface), UserNotFoundError.
    application/
      schemas.py           TokenResponse, UserProfileResponse (Pydantic DTOs).
      use_cases.py         RegisterOrRetrieveUser, GetCurrentUser (application services).
    infrastructure/
      orm_models.py        UserORM (SQLAlchemy model — database detail, not domain).
      repositories.py      SqlAlchemyUserRepository (concrete implementation of UserRepository).
      auth.py              create_access_token(), decode_access_token() — JWT utilities.
      google_oauth.py      OAuth client setup, redirect helper, token exchange.
    api/
      dependencies.py      get_user_repository(), get_current_user() — FastAPI dependencies.
      router.py            auth_router (/auth/google, /auth/google/callback),
                           users_router (/users/me).

  campaigns/               Campaign aggregate — tone, themes, level range, content boundaries.
    domain/
      models.py            CampaignTone (enum), LevelRange (value object), ContentBoundaries
                           (value object), Campaign (aggregate root).
      repositories.py      CampaignRepository (abstract interface), campaign domain exceptions.
      exceptions.py        CampaignNotFoundError and related domain exceptions.
    application/
      schemas.py           CampaignCreateRequest, CampaignResponse (Pydantic DTOs).
      use_cases.py         CreateCampaign, GetCampaign, ListCampaigns (application services).
    infrastructure/
      orm_models.py        CampaignORM (SQLAlchemy model).
      repositories.py      SqlAlchemyCampaignRepository.
    api/
      dependencies.py      get_campaign_repository() — FastAPI dependency.
      router.py            Campaign CRUD endpoints.

  worlds/                  World aggregate — lore, factions, bosses. Admin-seeded content.
    domain/
      models.py            WorldTheme (enum), Faction, Boss, World (aggregate root).
      repositories.py      WorldRepository (abstract interface), world domain exceptions.
      exceptions.py        WorldNotFoundError and related domain exceptions.
    application/
      schemas.py           WorldResponse, WorldSeedRequest (Pydantic DTOs).
      use_cases.py         GetWorld, ListWorlds, SeedWorld (application services).
    infrastructure/
      orm_models.py        WorldORM, FactionORM, BossORM (SQLAlchemy models).
      repositories.py      SqlAlchemyWorldRepository.
      seed.py              Data seeder — populates canonical worlds on first boot.
      prompts/             Empty stubs (prompt assembly moved to dungeons/).
    api/
      dependencies.py      get_world_repository() — FastAPI dependency.
      router.py            World read and seed endpoints.

  dungeons/                Dungeon generation — the primary LLM-integration context.
    domain/
      models.py            RoomType (enum), DungeonRoom, DungeonQuest, DungeonSettings,
                           ROOM_COUNT_MIN/MAX (constants), Dungeon (aggregate root).
      repositories.py      DungeonRepository (abstract interface).
      exceptions.py        DungeonNotFoundError, DungeonGenerationError.
    application/
      narrator_port.py     DungeonNarratorPort (ABC) — application-layer interface for the
                           LLM. Use cases depend on this port, not on any Gemini class.
      schemas.py           DungeonSettingsRequest, DungeonResponse (Pydantic DTOs).
      use_cases.py         GenerateDungeon, GetDungeon (application services).
    infrastructure/
      narrator.py          StubDungeonNarrator (template-based, no LLM) and
                           GeminiDungeonNarrator (calls gemini-2.0-flash). Both implement
                           DungeonNarratorPort.
      prompts/
        assembler.py       PromptAssembler — combines World + Campaign + DungeonSettings
                           into a single structured prompt string.
      orm_models.py        DungeonORM, DungeonRoomORM (SQLAlchemy models).
      repositories.py      SqlAlchemyDungeonRepository.
    api/
      dependencies.py      get_dungeon_repository(), get_narrator() — FastAPI dependencies.
                           get_narrator() returns GeminiDungeonNarrator in production and
                           StubDungeonNarrator when GEMINI_API_KEY is a dummy value.
      router.py            Dungeon generation and retrieval endpoints.

  combat/                  Turn-based combat encounters — initiative, turn order, dice rolling.
    domain/
      models.py            CombatStatus (enum), Combatant (entity), CombatEncounter
                           (aggregate root — owns combatants and enforces turn order).
      services.py          DiceRoller domain service (stateless dice-rolling logic).
      repositories.py      CombatRepository (abstract interface).
      events.py            Combat domain events (turn advanced, combatant defeated, etc.).
      exceptions.py        Combat domain exceptions.
    application/
      schemas.py           Pydantic DTOs for combat input and output.
      use_cases.py         StartCombat, AdvanceTurn, ApplyDamage (application services).
    infrastructure/
      dice.py              DiceRoller infrastructure implementation.
      orm_models.py        CombatEncounterORM, CombatantORM (SQLAlchemy models).
      repositories.py      SqlAlchemyCombatRepository.
    api/
      dependencies.py      get_combat_repository() — FastAPI dependency.
      router.py            Combat endpoints.

  rooms/                   Multiplayer rooms — invite codes, WebSocket presence.
    domain/
      models.py            InviteCode (value object), RoomPlayer (entity), Room (aggregate root).
      repositories.py      RoomRepository (abstract interface).
      events.py            RoomCreated, PlayerJoined, RoomClosed domain events.
    application/
      schemas.py           RoomCreateRequest, RoomResponse (Pydantic DTOs).
      use_cases.py         CreateRoom, JoinRoom, CloseRoom (application services).
    infrastructure/
      orm_models.py        RoomORM, RoomPlayerORM (SQLAlchemy models).
      repositories.py      SqlAlchemyRoomRepository.
    api/
      dependencies.py      get_room_repository() — FastAPI dependency.
      router.py            Room HTTP endpoints.
      websocket.py         WebSocket handler for real-time room presence.

alembic/
  env.py                   Wired to settings.DATABASE_URL and Base.metadata for autogenerate.

tests/                     Domain layer tests only. Mirror the app/ structure:
                           tests/{context}/domain/test_models.py, etc.
```

---

## Dependency diagram (users/ excerpt)

The diagram below shows the wiring for the `users` context. All other contexts follow
the same pattern: `api/ -> application/ -> domain/`, with `infrastructure/` implementing
domain or application-layer interfaces and pointing inward.

```
app/main.py
  -> app/api/v1/router.py
       -> app/users/api/router.py
            -> app/users/api/dependencies.py
                 -> app/users/application/use_cases.py
                      -> app/users/domain/models.py
                      -> app/users/domain/repositories.py (interface only)
                 -> app/users/infrastructure/auth.py
                      -> app/core/config.py
            -> app/users/infrastructure/repositories.py  (implements domain interface)
                 -> app/users/infrastructure/orm_models.py
                 -> app/users/domain/models.py
            -> app/users/infrastructure/google_oauth.py
                 -> app/core/config.py
            -> app/users/application/schemas.py

  domain/models.py and domain/repositories.py import nothing from app/
```

The last line is the proof that the dependency rule is respected. Open `app/users/domain/models.py`
and `app/users/domain/repositories.py` — their imports are only standard library modules
(`uuid`, `abc`, `re`, `datetime`). No FastAPI, no SQLAlchemy, no authlib.

The `dungeons` context adds one wrinkle: `dungeons/application/narrator_port.py` imports
`World` from `worlds/domain` and `Campaign` from `campaigns/domain`. This cross-context read
at the *application* layer is acceptable in a monolith — domain layers still import nothing
outside their own context.

---

## Index

| Entity | Documentation |
|--------|---------------|
| DDD / Domain-Driven Design | docs/architecture/concepts.md |
| Dependency rule | docs/architecture/concepts.md#2-the-dependency-rule |
| Bounded context | docs/architecture/concepts.md#3-bounded-contexts |
| Four layers | docs/architecture/concepts.md#4-the-four-layers |
| Value Object | docs/architecture/layers.md#value-objects |
| Email (value object) | docs/architecture/layers.md#value-objects |
| GoogleID (value object) | docs/architecture/layers.md#value-objects |
| InviteCode (value object) | docs/architecture/file-reference.md |
| LevelRange (value object) | docs/architecture/file-reference.md |
| ContentBoundaries (value object) | docs/architecture/file-reference.md |
| Aggregate root | docs/architecture/layers.md#aggregate-root |
| User (aggregate) | docs/architecture/layers.md#aggregate-root |
| Campaign (aggregate) | docs/architecture/file-reference.md |
| World (aggregate) | docs/architecture/file-reference.md |
| Dungeon (aggregate) | docs/architecture/file-reference.md |
| CombatEncounter (aggregate) | docs/architecture/file-reference.md |
| Room (aggregate) | docs/architecture/file-reference.md |
| Factory method | docs/architecture/layers.md#factory-method |
| Domain event | docs/architecture/layers.md#domain-events |
| UserRegisteredViaGoogle | docs/architecture/layers.md#domain-events |
| RoomCreated | docs/architecture/file-reference.md |
| PlayerJoined | docs/architecture/file-reference.md |
| RoomClosed | docs/architecture/file-reference.md |
| Repository interface | docs/architecture/layers.md#repository-interface |
| UserRepository | docs/architecture/layers.md#repository-interface |
| CampaignRepository | docs/architecture/file-reference.md |
| WorldRepository | docs/architecture/file-reference.md |
| DungeonRepository | docs/architecture/file-reference.md |
| CombatRepository | docs/architecture/file-reference.md |
| RoomRepository | docs/architecture/file-reference.md |
| Use case / Application service | docs/architecture/layers.md#use-cases-application-services |
| RegisterOrRetrieveUser | docs/architecture/layers.md#use-cases-application-services |
| GetCurrentUser | docs/architecture/layers.md#authentication-dependency |
| CreateCampaign / GetCampaign / ListCampaigns | docs/architecture/file-reference.md |
| GetWorld / ListWorlds / SeedWorld | docs/architecture/file-reference.md |
| GenerateDungeon / GetDungeon | docs/architecture/file-reference.md |
| StartCombat / AdvanceTurn / ApplyDamage | docs/architecture/file-reference.md |
| CreateRoom / JoinRoom / CloseRoom | docs/architecture/file-reference.md |
| DTO / Schema | docs/architecture/layers.md#schemas-dtos |
| UserProfileResponse | docs/architecture/layers.md#schemas-dtos |
| ORM model vs domain model | docs/architecture/layers.md#orm-model-vs-domain-model |
| UserORM | docs/architecture/layers.md#orm-model-vs-domain-model |
| CampaignORM | docs/architecture/file-reference.md |
| WorldORM / FactionORM / BossORM | docs/architecture/file-reference.md |
| DungeonORM / DungeonRoomORM | docs/architecture/file-reference.md |
| CombatEncounterORM / CombatantORM | docs/architecture/file-reference.md |
| RoomORM / RoomPlayerORM | docs/architecture/file-reference.md |
| Concrete repository | docs/architecture/layers.md#concrete-repository |
| SqlAlchemyUserRepository | docs/architecture/layers.md#concrete-repository |
| SqlAlchemyCampaignRepository | docs/architecture/file-reference.md |
| SqlAlchemyWorldRepository | docs/architecture/file-reference.md |
| SqlAlchemyDungeonRepository | docs/architecture/file-reference.md |
| SqlAlchemyCombatRepository | docs/architecture/file-reference.md |
| SqlAlchemyRoomRepository | docs/architecture/file-reference.md |
| JWT | docs/architecture/layers.md#jwt-utilities |
| create_access_token | docs/architecture/layers.md#jwt-utilities |
| decode_access_token | docs/architecture/layers.md#jwt-utilities |
| SECRET_KEY | docs/architecture/layers.md#jwt-utilities |
| Google OAuth / OIDC | docs/architecture/layers.md#google-oauth--oidc |
| SessionMiddleware | docs/architecture/layers.md#google-oauth--oidc |
| Narrator Port pattern | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| DungeonNarratorPort | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| StubDungeonNarrator | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| GeminiDungeonNarrator | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| PromptAssembler | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| GEMINI_API_KEY | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| DiceRoller | docs/architecture/file-reference.md |
| WebSocket handler | docs/architecture/file-reference.md |
| Settings / config.py | docs/architecture/file-reference.md |
| DomainError | docs/architecture/file-reference.md |
| NotFoundError | docs/architecture/file-reference.md |
| AuthenticationError | docs/architecture/file-reference.md |
| error_handlers.py | docs/architecture/file-reference.md |
| get_db() | docs/architecture/python-concepts.md#generators-for-session-lifecycle |
| Dependency injection (FastAPI Depends) | docs/architecture/layers.md#dependency-injection |
| Thin router | docs/architecture/layers.md#thin-router |
| Dependency diagram | docs/architecture/file-reference.md#dependency-diagram-users-excerpt |
| Request lifecycle | docs/architecture/lifecycle.md |
| Dataclasses | docs/architecture/python-concepts.md#dataclasses |
| object.__setattr__ | docs/architecture/python-concepts.md#objectsetattr-in-frozen-dataclasses |
| Abstract Base Classes | docs/architecture/python-concepts.md#abstract-base-classes |
| Type hints / X | None | docs/architecture/python-concepts.md#type-hints-and-x--none |
| Classmethods as factories | docs/architecture/python-concepts.md#classmethods-as-factories |
| Generators (session lifecycle) | docs/architecture/python-concepts.md#generators-for-session-lifecycle |
| cast() | docs/architecture/python-concepts.md#cast-for-type-narrowing |
