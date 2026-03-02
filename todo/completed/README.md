# Docker Compose Unification Tasks

This directory contains the technical tasks generated to migrate the application from module-specific container configuration files to a centralized orchestration model at the repository root.

## Execution Order

1. **[infrastructure](infrastructure.md)**: Contains tasks to create the root `docker-compose.yml` and `.env.example`, and subsequently delete the child ones in `frontend/` and `backend/`.
