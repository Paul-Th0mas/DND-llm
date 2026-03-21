# Project Architecture: DDD with FastAPI

This document is the entry point. The architecture is split across four focused files —
load only what you need.

## Reading order (first time)

1. [concepts.md](architecture/concepts.md) — Why DDD, the dependency rule, bounded contexts,
   the four layers. Start here.
2. [layers.md](architecture/layers.md) — How each layer works in depth: value objects,
   aggregates, use cases, ORM mapping, JWT, OAuth, the Narrator Port (LLM integration),
   dependency injection.
3. [lifecycle.md](architecture/lifecycle.md) — Full request traces through all layers
   (Google OAuth sign-in, authenticated GET).
4. [python-concepts.md](architecture/python-concepts.md) — Python-specific patterns used
   throughout: dataclasses, frozen dataclasses, ABCs, generators, `cast()`.
5. [file-reference.md](architecture/file-reference.md) — Every file in the project mapped
   to its purpose, plus the dependency diagram.

## Quick links

| I want to understand... | File |
|-------------------------|------|
| Why DDD / what problem it solves | [concepts.md](architecture/concepts.md#1-the-core-problem-ddd-solves) |
| The dependency rule | [concepts.md](architecture/concepts.md#2-the-dependency-rule) |
| What bounded contexts exist | [concepts.md](architecture/concepts.md#3-bounded-contexts) |
| Value objects, aggregates, domain events | [layers.md](architecture/layers.md#5-domain-layer-in-depth) |
| Use cases and DTOs | [layers.md](architecture/layers.md#6-application-layer-in-depth) |
| ORM mapping, JWT, OAuth | [layers.md](architecture/layers.md#7-infrastructure-layer-in-depth) |
| How LLM / Gemini integration works | [layers.md](architecture/layers.md#narrator-port-pattern-llm-integration) |
| FastAPI dependency injection | [layers.md](architecture/layers.md#8-api-layer-in-depth) |
| Full request trace (OAuth sign-in) | [lifecycle.md](architecture/lifecycle.md#sign-in-with-google) |
| What a specific file does | [file-reference.md](architecture/file-reference.md) |
| A specific class or pattern | See index below |

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
| RoomCreated / PlayerJoined / RoomClosed | docs/architecture/file-reference.md |
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
| Request lifecycle: sign in with Google | docs/architecture/lifecycle.md#sign-in-with-google |
| Request lifecycle: GET /users/me | docs/architecture/lifecycle.md#authenticated-request-get-usersme |
| Dataclasses | docs/architecture/python-concepts.md#dataclasses |
| object.__setattr__ | docs/architecture/python-concepts.md#objectsetattr-in-frozen-dataclasses |
| Abstract Base Classes | docs/architecture/python-concepts.md#abstract-base-classes |
| Type hints / X | None | docs/architecture/python-concepts.md#type-hints-and-x--none |
| Classmethods as factories | docs/architecture/python-concepts.md#classmethods-as-factories |
| Generators (session lifecycle) | docs/architecture/python-concepts.md#generators-for-session-lifecycle |
| cast() | docs/architecture/python-concepts.md#cast-for-type-narrowing |
