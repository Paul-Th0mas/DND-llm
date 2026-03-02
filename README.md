# DnD LLM Project

A complete full-stack web application with a Next.js frontend, FastAPI backend, and PostgreSQL database, fully orchestratable via Docker Compose.

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Local Setup

### 1. Environment Variables

Start by creating your local environment variables file. Copy the provided `.env.example` file to create a `.env` file at the root of the project:

```bash
cp .env.example .env
```

Ensure the variables are correctly filled out. Dummy values are provided by default, which is sufficient to get the containers initialized and running locally without crashing.

### 2. Building and Running the Application

This project uses a single root `docker-compose.yml` to orchestrate all services natively.

To build the images and start the database, backend, and frontend containers (in detached mode), run:

```bash
docker compose up --build -d
```

### 3. Accessing the Services

Once all the containers are running, you can access the components at the following local URLs:

- **Frontend (Next.js)**: [http://localhost:3000](http://localhost:3000)
- **Backend API (FastAPI)**: [http://localhost:8000](http://localhost:8000)

### 4. Viewing Logs

If you want to view the logs for the running services to monitor activity or troubleshoot errors:

```bash
# View live logs for all services
docker compose logs -f

# View live logs for a specific service (e.g., backend)
docker compose logs -f backend
```

### 5. Stopping the Application

To cleanly stop the containers and their network without destroying your persisted PostgreSQL data, run:

```bash
docker compose down
```

_Note: The database data is persisted in a Docker volume. If you ever need to completely wipe the database and start fresh, you can run `docker compose down -v`._
