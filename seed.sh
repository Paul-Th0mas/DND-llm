#!/usr/bin/env bash
# seed.sh — Interactive seed runner for the DnD backend.
#
# Usage:
#   ./seed.sh
#
# Discovers all seed*.py files under backend/app/, asks whether to run
# locally or inside the Docker backend container, checks that the required
# infrastructure is up, then lets the user select which seeds to run.
#
# Environment variables (local mode only):
#   DATABASE_URL  — defaults to postgresql://postgres:admin@localhost:5432/dnd_db

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

# Name of the docker compose services (must match docker-compose.yml).
DB_SERVICE="db"
BACKEND_SERVICE="backend"

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

print_header() {
    echo ""
    echo "========================================"
    echo "  DnD Backend — Seed Runner"
    echo "========================================"
    echo ""
}

# ---------------------------------------------------------------------------
# Execution mode selection
# ---------------------------------------------------------------------------

# Sets the global RUN_MODE to "local" or "docker".
ask_run_mode() {
    echo "Where should the seeds be executed?"
    echo ""
    echo "  [1] Locally  (requires Python and a reachable database on this machine)"
    echo "  [2] Docker   (runs inside the running backend container)"
    echo ""
    read -rp "Select an option [1/2]: " mode_choice

    case "$mode_choice" in
        1) RUN_MODE="local" ;;
        2) RUN_MODE="docker" ;;
        *)
            echo "Invalid choice. Please enter 1 or 2."
            ask_run_mode
            ;;
    esac
}

# ---------------------------------------------------------------------------
# Infrastructure checks — Docker mode
# ---------------------------------------------------------------------------

# Verify docker and docker compose are available.
check_docker_available() {
    if ! command -v docker &>/dev/null; then
        echo ""
        echo "ERROR: 'docker' is not installed or not on PATH."
        exit 1
    fi

    # Support both 'docker compose' (plugin) and 'docker-compose' (standalone).
    if docker compose version &>/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &>/dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        echo ""
        echo "ERROR: Neither 'docker compose' nor 'docker-compose' is available."
        exit 1
    fi
}

# Check that a given compose service is running.
check_service_running() {
    local service="$1"
    local state
    state="$($COMPOSE_CMD -f "$SCRIPT_DIR/docker-compose.yml" ps --format json "$service" 2>/dev/null \
        | grep -o '"State":"[^"]*"' | head -1 | cut -d'"' -f4 || true)"

    # Fallback for older compose versions that do not support --format json.
    if [[ -z "$state" ]]; then
        state="$($COMPOSE_CMD -f "$SCRIPT_DIR/docker-compose.yml" ps "$service" 2>/dev/null \
            | grep "$service" | awk '{print $NF}' || true)"
    fi

    if [[ "$state" != "running" && "$state" != "Up" ]]; then
        echo ""
        echo "ERROR: The '$service' container is not running."
        echo "       Start it with: docker compose up -d $service"
        exit 1
    fi
}

check_docker_infra() {
    echo "Checking Docker infrastructure..."
    check_docker_available

    check_service_running "$DB_SERVICE"
    echo "  [ok] $DB_SERVICE container is running."

    check_service_running "$BACKEND_SERVICE"
    echo "  [ok] $BACKEND_SERVICE container is running."

    # Verify the database inside the container is accepting connections.
    local db_user="postgres"
    local db_name="dnd_db"
    echo "  Checking database readiness inside container..."
    if ! $COMPOSE_CMD -f "$SCRIPT_DIR/docker-compose.yml" \
            exec "$DB_SERVICE" pg_isready -U "$db_user" -d "$db_name" -q; then
        echo ""
        echo "ERROR: Database inside the '$DB_SERVICE' container is not ready."
        exit 1
    fi
    echo "  [ok] Database is ready."
}

# ---------------------------------------------------------------------------
# Infrastructure checks — local mode
# ---------------------------------------------------------------------------

# Extract a component from the DATABASE_URL.
# Usage: parse_db_url <field>  where field is host|port|user|dbname
parse_db_url() {
    local field="$1"
    local url="${DATABASE_URL:-postgresql://postgres:admin@localhost:5432/dnd_db}"

    local without_scheme="${url#*://}"
    local userinfo="${without_scheme%%@*}"
    local hostinfo="${without_scheme#*@}"

    local user="${userinfo%%:*}"
    local host="${hostinfo%%:*}"
    local port_and_db="${hostinfo#*:}"
    local port="${port_and_db%%/*}"
    local dbname="${port_and_db#*/}"

    case "$field" in
        host)   echo "$host" ;;
        port)   echo "$port" ;;
        user)   echo "$user" ;;
        dbname) echo "$dbname" ;;
    esac
}

check_local_infra() {
    local host port user
    host="$(parse_db_url host)"
    port="$(parse_db_url port)"
    user="$(parse_db_url user)"

    echo "Checking local database connectivity ($host:$port)..."

    if command -v pg_isready &>/dev/null; then
        if ! pg_isready -h "$host" -p "$port" -U "$user" -q; then
            echo ""
            echo "ERROR: Database is not ready at $host:$port."
            echo "       Make sure Postgres is running locally or via Docker:"
            echo "         docker compose up -d db"
            exit 1
        fi
    else
        # Fallback: TCP probe via bash builtins.
        if ! (echo >/dev/tcp/"$host"/"$port") &>/dev/null; then
            echo ""
            echo "ERROR: Cannot reach $host:$port."
            echo "       Make sure Postgres is running locally or via Docker:"
            echo "         docker compose up -d db"
            exit 1
        fi
    fi

    echo "  [ok] Database is reachable."
}

# ---------------------------------------------------------------------------
# Seed discovery and module conversion
# ---------------------------------------------------------------------------

discover_seeds() {
    mapfile -t SEED_FILES < <(
        find "$BACKEND_DIR/app" -type f -name "seed*.py" | sort
    )
}

# Convert an absolute file path to a Python dotted module string.
# e.g. /project/backend/app/worlds/infrastructure/seed.py
#   -> app.worlds.infrastructure.seed
path_to_module() {
    local abs_path="$1"
    local rel="${abs_path#"$BACKEND_DIR/"}"
    local no_ext="${rel%.py}"
    echo "${no_ext//\//.}"
}

# ---------------------------------------------------------------------------
# Seed execution
# ---------------------------------------------------------------------------

# Resolve the local Python interpreter: prefer backend venv, fall back to python3.
resolve_python() {
    local venv_python="$BACKEND_DIR/.venv/bin/python"
    if [[ -x "$venv_python" ]]; then
        echo "$venv_python"
    elif command -v python3 &>/dev/null; then
        echo "python3"
    else
        echo ""
    fi
}

run_seed_local() {
    local module="$1"
    echo ""
    echo "--- Running: $module ---"
    (cd "$BACKEND_DIR" && "$LOCAL_PYTHON" -m "$module")
    echo "--- Done:    $module ---"
}

run_seed_docker() {
    local module="$1"
    echo ""
    echo "--- Running: $module (in container '$BACKEND_SERVICE') ---"
    # The container WORKDIR is /app, which is where the backend code lives.
    $COMPOSE_CMD -f "$SCRIPT_DIR/docker-compose.yml" \
        exec "$BACKEND_SERVICE" python -m "$module"
    echo "--- Done:    $module ---"
}

run_seed() {
    local module="$1"
    if [[ "$RUN_MODE" == "docker" ]]; then
        run_seed_docker "$module"
    else
        run_seed_local "$module"
    fi
}

# ---------------------------------------------------------------------------
# Interactive menu
# ---------------------------------------------------------------------------

show_menu() {
    echo "Available seed files:"
    echo ""

    local i=1
    for path in "${SEED_FILES[@]}"; do
        local module
        module="$(path_to_module "$path")"
        printf "  [%d] %s\n" "$i" "$module"
        ((i++))
    done

    echo ""
    printf "  [A] Run all\n"
    printf "  [Q] Quit\n"
    echo ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

print_header

# 1. Ask execution mode.
ask_run_mode
echo ""

# 2. Discover seed files.
discover_seeds
if [[ ${#SEED_FILES[@]} -eq 0 ]]; then
    echo "No seed files found under backend/app/."
    exit 0
fi

# 3. Check infrastructure for the chosen mode.
if [[ "$RUN_MODE" == "docker" ]]; then
    check_docker_infra
else
    LOCAL_PYTHON="$(resolve_python)"
    if [[ -z "$LOCAL_PYTHON" ]]; then
        echo "ERROR: No Python interpreter found."
        echo "       Install Python 3 or create a venv at backend/.venv."
        exit 1
    fi
    echo "  [ok] Python interpreter: $LOCAL_PYTHON"
    check_local_infra
fi

echo ""

# 4. Interactive seed selection loop.
while true; do
    show_menu
    read -rp "Select an option: " choice

    case "${choice^^}" in
        Q)
            echo "Exiting."
            exit 0
            ;;
        A)
            for path in "${SEED_FILES[@]}"; do
                run_seed "$(path_to_module "$path")"
            done
            echo ""
            echo "All seeds completed."
            break
            ;;
        *)
            if [[ "$choice" =~ ^[0-9]+$ ]] && \
               (( choice >= 1 && choice <= ${#SEED_FILES[@]} )); then
                run_seed "$(path_to_module "${SEED_FILES[$(( choice - 1 ))]}")"
                echo ""
                read -rp "Run another seed? [y/N]: " again
                [[ "${again,,}" == "y" ]] || break
            else
                echo "Invalid selection. Please enter a number between 1 and ${#SEED_FILES[@]}, A, or Q."
            fi
            ;;
    esac
done
