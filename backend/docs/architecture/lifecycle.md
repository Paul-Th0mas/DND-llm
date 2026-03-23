# Request Lifecycle

Traces full requests through all layers. Assumes you have read
[concepts.md](concepts.md) and [layers.md](layers.md) first.

---

## Sign in with Google

```
Browser                  API Layer              Application           Domain            Infrastructure
   |                         |                      |                   |                    |
   |-- GET /api/v1/auth/google -->                  |                   |                    |
   |                         |                      |                   |                    |
   |                 google_oauth.py                |                   |                    |
   |                 builds redirect URL            |                   |                    |
   |<-- 302 to accounts.google.com ---------------  |                   |                    |
   |                         |                      |                   |                    |
   |    (user approves)      |                      |                   |                    |
   |                         |                      |                   |                    |
   |-- GET /api/v1/auth/google/callback?code=... -->|                   |                    |
   |                         |                      |                   |                    |
   |               exchange_code_for_user_info()    |                   |                    |
   |                         |-- POST token endpoint (Google) -------->|                    |
   |                         |<-- {id_token, access_token} -----------|                    |
   |                         |                      |                   |                    |
   |               RegisterOrRetrieveUser.execute() |                   |                    |
   |                         |-- repo.get_by_google_id() ------------>|                    |
   |                         |                      |         SqlAlchemyUserRepository       |
   |                         |                      |         SELECT from users              |
   |                         |                      |<-------- None (first login) ----------|
   |                         |                      |                   |                    |
   |                         |         User.register_via_google()       |                    |
   |                         |                      |-- Email("x@y.com")                    |
   |                         |                      |   validates + lowercases               |
   |                         |                      |-- GoogleID("123")                      |
   |                         |                      |   validates non-empty                  |
   |                         |                      |-- uuid4()                              |
   |                         |                      |<-- (User, UserRegisteredViaGoogle)     |
   |                         |                      |                   |                    |
   |                         |-- repo.save(user) -------------------- |                    |
   |                         |                      |         session.merge() + flush()      |
   |                         |                      |                   |                    |
   |               db.commit()                      |                   |                    |
   |               create_access_token(sub=user.id) |                   |                    |
   |<-- 302 to frontend?token=<jwt> --------------- |                   |                    |
```

---

## Authenticated request: GET /users/me

```
Browser                  API Layer              Application           Domain            Infrastructure
   |                         |                      |                   |                    |
   |-- GET /me  Authorization: Bearer <jwt> ------->|                   |                    |
   |                         |                      |                   |                    |
   |               HTTPBearer extracts token        |                   |                    |
   |               decode_access_token()            |                   |                    |
   |               -- verifies signature, expiry    |                   |                    |
   |               -- returns uuid.UUID             |                   |                    |
   |                         |                      |                   |                    |
   |               GetCurrentUser.execute(uuid)     |                   |                    |
   |                         |-- repo.get_by_id() ------------------- |                    |
   |                         |                      |         SELECT from users              |
   |                         |                      |<-------- UserORM row ----------------- |
   |                         |                      |         _to_domain() wraps into User   |
   |                         |<-- User -------------|                   |                    |
   |                         |                      |                   |                    |
   |               UserProfileResponse(...)         |                   |                    |
   |<-- 200 {"id": "...", "email": "..."} --------- |                   |                    |
```

---

## Index

| Entity | Documentation |
|--------|---------------|
| DDD / Domain-Driven Design | docs/architecture/concepts.md |
| Dependency rule | docs/architecture/concepts.md#2-the-dependency-rule |
| Bounded context | docs/architecture/concepts.md#3-bounded-contexts |
| Four layers | docs/architecture/concepts.md#4-the-four-layers |
| Value Object | docs/architecture/layers.md#value-objects |
| Aggregate root | docs/architecture/layers.md#aggregate-root |
| Factory method | docs/architecture/layers.md#factory-method |
| Domain event | docs/architecture/layers.md#domain-events |
| Repository interface | docs/architecture/layers.md#repository-interface |
| Use case / Application service | docs/architecture/layers.md#use-cases-application-services |
| DTO / Schema | docs/architecture/layers.md#schemas-dtos |
| ORM model vs domain model | docs/architecture/layers.md#orm-model-vs-domain-model |
| Concrete repository | docs/architecture/layers.md#concrete-repository |
| JWT | docs/architecture/layers.md#jwt-utilities |
| Google OAuth / OIDC | docs/architecture/layers.md#google-oauth--oidc |
| Narrator Port pattern | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| Dependency injection (FastAPI Depends) | docs/architecture/layers.md#dependency-injection |
| Thin router | docs/architecture/layers.md#thin-router |
| Request lifecycle: sign in with Google | docs/architecture/lifecycle.md#sign-in-with-google |
| Request lifecycle: GET /users/me | docs/architecture/lifecycle.md#authenticated-request-get-usersme |
| Dataclasses | docs/architecture/python-concepts.md#dataclasses |
| Abstract Base Classes | docs/architecture/python-concepts.md#abstract-base-classes |
| Generators (session lifecycle) | docs/architecture/python-concepts.md#generators-for-session-lifecycle |
| cast() | docs/architecture/python-concepts.md#cast-for-type-narrowing |
| File reference | docs/architecture/file-reference.md |
| Dependency diagram | docs/architecture/file-reference.md#dependency-diagram-users-excerpt |
