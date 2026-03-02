#!/usr/bin/env bash
# Kill the process listening on a given TCP port.
# Works on Linux, macOS, and WSL (where lsof may miss processes).
# Usage: ./scripts/kill-port.sh <port>
# Example: ./scripts/kill-port.sh 3000

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $(basename "$0") <port>" >&2
  exit 1
fi

PORT="$1"

if ! [[ "$PORT" =~ ^[0-9]+$ ]] || (( PORT < 1 || PORT > 65535 )); then
  echo "Error: '$PORT' is not a valid port number (1-65535)." >&2
  exit 1
fi

find_pid() {
  local pid

  # Primary: lsof (works on macOS and most Linux)
  pid=$(lsof -ti tcp:"$PORT" 2>/dev/null || true)
  [[ -n "$pid" ]] && echo "$pid" && return

  # Fallback 1: fuser (works on Linux/WSL when lsof cannot see the socket)
  pid=$(fuser "${PORT}/tcp" 2>/dev/null | tr -s ' ' '\n' | grep -E '^[0-9]+$' | head -1 || true)
  [[ -n "$pid" ]] && echo "$pid" && return

  # Fallback 2: ss — parse inode from the socket entry then look it up in /proc
  local hex_port
  hex_port=$(printf '%04X' "$PORT")
  local inode
  inode=$(ss -tlnp 2>/dev/null \
    | awk -v port=":${PORT}" '$4 ~ port || $5 ~ port {
        match($0, /pid=([0-9]+)/, arr); if (arr[1]) print arr[1]
      }' | head -1 || true)
  [[ -n "$inode" ]] && echo "$inode" && return

  # Fallback 3: parse /proc/net/tcp and /proc/net/tcp6 directly
  for f in /proc/net/tcp /proc/net/tcp6; do
    [[ -f "$f" ]] || continue
    inode=$(awk -v port="$hex_port" '
      NR > 1 && $2 ~ (":" port "$") && $4 == "0A" { print $10; exit }
    ' "$f" 2>/dev/null || true)
    if [[ -n "$inode" ]]; then
      pid=$(grep -rl "socket:\[$inode\]" /proc/*/fd 2>/dev/null \
        | grep -oP '(?<=/proc/)\d+' | head -1 || true)
      [[ -n "$pid" ]] && echo "$pid" && return
    fi
  done
}

PID=$(find_pid)

if [[ -z "$PID" ]]; then
  echo "No process found on port $PORT."
  exit 0
fi

echo "Killing PID $PID on port $PORT..."
kill -TERM "$PID" 2>/dev/null || true

# Wait up to 3 seconds for graceful exit, then force-kill.
for _ in {1..6}; do
  sleep 0.5
  if ! kill -0 "$PID" 2>/dev/null; then
    echo "Process $PID terminated."
    exit 0
  fi
done

echo "Process $PID did not exit — sending SIGKILL..."
kill -KILL "$PID" 2>/dev/null || true
echo "Process $PID force-killed."
