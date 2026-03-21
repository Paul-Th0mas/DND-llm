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

Open `.env` and review the following variables before starting the application:

- **`GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`**: OAuth credentials from the [Google Cloud Console](https://console.cloud.google.com/) under APIs & Services > Credentials. Required for user authentication.
- **`SECRET_KEY`**: Used to sign JWT tokens. Must be a cryptographically random string in any non-trivial deployment. Generate one with:
  ```bash
  openssl rand -hex 32
  ```
- **`GEMINI_API_KEY`**: Required for world and campaign generation. Obtain a key from [Google AI Studio](https://aistudio.google.com/app/apikey). The application will start with the dummy value but LLM generation calls will fail until a real key is provided.
- **`FRONTEND_URL`**: The URL of the frontend, used for CORS and OAuth redirects. Defaults to `http://localhost:3000` for local development.

The remaining variables (`POSTGRES_*`, `DATABASE_URL`) use sensible local defaults and do not need to be changed for local development.

### 2. Building and Running the Application

This project uses a single root `docker-compose.yml` to orchestrate all services natively.

To build the images and start the database, backend, and frontend containers (in detached mode), run:

```bash
docker compose up --build -d
```

### 3. Run Database Migrations

The database schema is not created automatically on first boot. After the containers are running, apply all Alembic migrations to create the required tables:

```bash
docker compose exec backend alembic upgrade head
```

This command must be re-run whenever new migrations are added (e.g. after pulling changes that include schema updates).

### 4. Accessing the Services

Once all the containers are running, you can access the components at the following local URLs:

- **Frontend (Next.js)**: [http://localhost:3000](http://localhost:3000)
- **Backend API (FastAPI)**: [http://localhost:8000](http://localhost:8000)
- **API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Documentation (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 5. Viewing Logs

If you want to view the logs for the running services to monitor activity or troubleshoot errors:

```bash
# View live logs for all services
docker compose logs -f

# View live logs for a specific service (e.g., backend)
docker compose logs -f backend
```

### 6. Stopping the Application

To cleanly stop the containers and their network without destroying your persisted PostgreSQL data, run:

```bash
docker compose down
```

_Note: The database data is persisted in a Docker volume. If you ever need to completely wipe the database and start fresh, you can run `docker compose down -v`._

## Running Tests

### Backend

Run the backend test suite inside the backend container (or a local virtualenv with dependencies installed):

```bash
docker compose exec backend pytest tests/ -v
```

### Frontend

Run the frontend test suite from the `frontend/` directory:

```bash
yarn test:run
```

Use `yarn test` to run in watch mode during development.
