---
id: TASK-3
title: Consolidate common configuration and documentation files to repository root
type: chore
priority: medium
status: done
created_by: task-creator-agent
created_at: 2026-02-28T14:55:51Z
assignee: unassigned
bounded_context: none
layer: cross-cutting
estimated_effort: S
depends_on: none
blocks: none
---

## Summary

To improve discoverability and maintainability, we need to unify common repository-level configuration files (like git ignores, docker ignores, and AI guidelines) from the module subdirectories (`frontend/` and `backend/`) into the repository root. This ensures global consistency across our tech stack.

## Background and Context

Presently, both the `frontend/` and `backend/` directories maintain their own copies of `.gitignore` and `CLAUDE.md`, while `.dockerignore` only exists in `frontend/`. Having multiple configuration files causes duplication and makes them harder to update. The original task to unify `docker-compose` files didn't address these.

## Acceptance Criteria

1. A new combined `.gitignore` file must be created at the repository root, merging the contents of `backend/.gitignore` and `frontend/.gitignore`.
   - The original `backend/.gitignore` and `frontend/.gitignore` must be deleted.
   - Any paths in the ignore patterns must be updated if they require prefixing, although standard globs (e.g., `node_modules/`, `__pycache__/`) will work natively at the root.
2. A single `CLAUDE.md` file must be created at the repository root, combining the backend and frontend instructions into distinct sections (e.g., "General Rules", "Backend Instructions", "Frontend Instructions").
   - The original `backend/CLAUDE.md` and `frontend/CLAUDE.md` must be deleted.
3. The `frontend/.dockerignore` file must be moved to the repository root (as `.dockerignore`) and updated to include exclusion patterns for both frontend and backend (e.g., ignoring `.env`, Next.js build output, python virtual environments, and `node_modules`).
4. The backend and frontend `Dockerfile`s and the root `docker-compose.yml` must be updated to build using the root `.` context.
   - `docker-compose.yml` services (`backend` and `frontend`) must use `context: .` and specify their respective `dockerfile` directly (e.g., `dockerfile: backend/Dockerfile` and `dockerfile: frontend/Dockerfile`).
   - `backend/Dockerfile` must copy files from the `backend/` directory instead of `.` (e.g. `COPY backend/requirements.txt .`).
   - `frontend/Dockerfile` must copy files from the `frontend/` directory instead of `.` (e.g. `COPY frontend/package.json frontend/yarn.lock ./`).

## DDD Considerations

N/A - This is purely an infrastructure and development environment unification change.

## Documentation Requirements

- The newly consolidated root `CLAUDE.md` must clearly delineate frontend-specific and backend-specific requirements.

## Out of Scope

- Updating actual dependencies or tool configurations (like `eslint` or `ruff`) that are correctly scoped to the frontend/backend modules.
- Changing application source code.

## Open Questions

- Does `vitest` or `pytest` configuration need adjustments to ignore root-level artifacts? (Likely no, as they typically scope to their execution directory).

## Definition of Done

- [x] All acceptance criteria are met.
- [x] Tests are added or updated.
- [x] Documentation requirements are fulfilled.
- [x] Code review approved by at least one domain expert.
- [x] No broken bounded context contracts.
- [x] Task status updated to `done`.
