---
id: TASK-1
title: Create centralized root docker-compose.yml
type: chore
priority: high
status: done
created_by: task-creator-agent
created_at: 2026-02-28T14:51:22Z
assignee: unassigned
bounded_context: none
layer: infrastructure
estimated_effort: S
depends_on: none
blocks: [TASK-2]
---

## Summary

To simplify local development and deployment, we need to consolidate the container orchestration into a single `docker-compose.yml` built at the repository root. This will orchestrate the frontend, backend, and database services within a single network.

## Background and Context

Presently, both the `frontend/` and `backend/` directories contain their own separate `docker-compose.yml` files (`frontend/docker-compose.yml` and `backend/docker-compose.yml`). Working with multiple compose files complicates local development workflows and environment variable management.

## Acceptance Criteria

1. A new `docker-compose.yml` file must exist in the root of the repository.
2. The root compose file must define three services: `frontend`, `backend` (named `app` previously, but refer to it logically as backend), and `db`.
3. The `backend` service must build from `./backend` and expose port `8000:8000`.
4. The `frontend` service must build from `./frontend` and expose port `3000:3000`.
5. The `db` service must continue to use `postgres:16-alpine`, map port `5432:5432`, and persist data locally via a named volume.
6. A single `.env.example` file must be added to the root directory for defining environment variables (e.g., `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).

## DDD Considerations

N/A - This is purely an infrastructure and developer-experience change. It doesn't modify the domain.

## Documentation Requirements

- The repository-level `README.md` must be updated to instruct users to run `docker compose up` from the root directory instead of individual subdirectories.

## Out of Scope

- Making changes to the application code inside the backend or frontend directories.
- Refactoring `Dockerfile` contents unless necessary to support the consolidated build context.

## Open Questions

- Do we need to introduce a web server (e.g. NGINX) as a reverse proxy, or just expose both frontend and backend ports directly for now? (Assumption: expose ports directly for now.)

## Definition of Done

- [x] All acceptance criteria are met.
- [x] Tests are added or updated.
- [x] Documentation requirements are fulfilled.
- [x] Code review approved by at least one domain expert.
- [x] No broken bounded context contracts.
- [x] Task status updated to `done`.

---

id: TASK-2
title: Remove deprecated module-level docker-compose files
type: chore
priority: medium
status: done
created_by: task-creator-agent
created_at: 2026-02-28T14:51:22Z
assignee: unassigned
bounded_context: none
layer: infrastructure
estimated_effort: XS
depends_on: [TASK-1]
blocks: none

---

## Summary

With the orchestration logic now centralized in a single root docker-compose file, the old module-specific docker-compose files are redundant and must be removed to prevent confusion.

## Background and Context

The `backend/docker-compose.yml` and `frontend/docker-compose.yml` files were the legacy mode of running containers. They are replaced by the task described in TASK-1.

## Acceptance Criteria

1. The file `backend/docker-compose.yml` must be deleted.
2. The file `frontend/docker-compose.yml` must be deleted.

## DDD Considerations

N/A

## Documentation Requirements

None. Handled by TASK-1.

## Out of Scope

- Modifying `backend/Dockerfile` or `frontend/Dockerfile`.

## Open Questions

N/A

## Definition of Done

- [x] All acceptance criteria are met.
- [x] Tests are added or updated.
- [x] Documentation requirements are fulfilled.
- [x] Code review approved by at least one domain expert.
- [x] No broken bounded context contracts.
- [x] Task status updated to `done`.
