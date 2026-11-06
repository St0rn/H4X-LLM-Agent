#!/usr/bin/env bash
# H4X LLM AGENT - Kali MCP / MetasploitMCP / Ollama
if [ -z "${BASH_VERSION:-}" ]; then exec /usr/bin/env bash "$0" "$@"; fi
set -Eeuo pipefail

if [ "$(id -u)" -ne 0 ]; then
  printf '[ERROR] ROOT privileges required.\n[INFO] sudo bash ./hax.sh\n' >&2
  exit 1
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin:$PATH"
umask 077
mkdir -p "$DIR/logs"
# Explicitly authorized Nmap targets. Set here because sudo normally drops user exports.
# Exact hostnames only; adding a domain does NOT automatically allow subdomains.
export H4X_AUTO_TARGETS="${H4X_AUTO_TARGETS:-localhost,127.0.0.1,::1}"
MODEL="${MODEL:-qwen2.5:7b}"
PYTHON="$DIR/.venv/bin/python3"
OLLAMA_URL="http://127.0.0.1:11434"
KALI_HOST="127.0.0.1"
KALI_PORT=5000
RPC_HOST="127.0.0.1"
RPC_USER="msf"
RPC_PORT=55553
SECRET_FILE="$DIR/.msf-rpc-secret"
RPC_PORT_FILE="$DIR/logs/msfrpcd.port"

RED='\033[1;31m'; CYAN='\033[1;36m'; GREEN='\033[1;32m'
YELLOW='\033[1;33m'; GRAY='\033[0;90m'; WHITE='\033[1;37m'; RESET='\033[0m'
info()    { printf '%b[+]%b %s\n' "$CYAN" "$RESET" "$*"; }
success() { printf '%b[OK]%b %s\n' "$GREEN" "$RESET" "$*"; }
warning() { printf '%b[!]%b %s\n' "$YELLOW" "$RESET" "$*"; }
error()   { printf '%b[-]%b %s\n' "$RED" "$RESET" "$*" >&2; }

# Center ASCII text according to terminal width; avoid clear failing in non-TTY shells.
COLS="$(tput cols 2>/dev/null || echo 80)"
[[ "$COLS" =~ ^[0-9]+$ ]] || COLS=80
center() {
  local line="$1" indent=0
  if (( COLS > ${#line} )); then indent=$(( (COLS - ${#line}) / 2 )); fi
  printf '%*s%s\n' "$indent" '' "$line"
}
banner_line() { printf '%b' "$1"; center "$2"; printf '%b' "$RESET"; }
show_banner() {
  clear 2>/dev/null || true
  echo
  banner_line "$RED" ' _   _  _  _   __  __'
  banner_line "$RED" '| | | || || |  \ \/ /'
  banner_line "$RED" '| |_| || || |_  \  / '
  banner_line "$RED" '|  _  ||__   _| /  \ '
  banner_line "$RED" '|_| |_ |   |_| /_/\_\'
  echo
  banner_line "$CYAN" ' _     _     __  __'
  banner_line "$CYAN" '| |   | |   |  \/  |'
  banner_line "$CYAN" '| |   | |   | |\/| |'
  banner_line "$CYAN" '| |___| |___| |  | |'
  banner_line "$CYAN" '|_____|_____|_|  |_ |'
  echo
  banner_line "$WHITE" 'A  G  E  N  T'
  echo
  banner_line "$GRAY" '---------------------------------------------'
  banner_line "$RED" 'H4X // OFFENSIVE AI ENGINE'
  banner_line "$WHITE" 'Author: St0rn - www.cybersecurit.fr'
  banner_line "$GRAY" '---------------------------------------------'
  echo
  banner_line "$CYAN" "LLM       : Ollama / $MODEL"
  banner_line "$CYAN" 'FRAMEWORK : Kali Linux'
  banner_line "$CYAN" 'PROTOCOL  : Model Context Protocol'
  banner_line "$CYAN" 'MODULES   : Kali MCP + MetasploitMCP'
  banner_line "$CYAN" 'RPC       : Metasploit Framework'
  echo
  banner_line "$GRAY" '---------------------------------------------'
  banner_line "$GREEN" 'SYSTEM INITIALIZATION'
  banner_line "$GRAY" '---------------------------------------------'
  echo
}
show_banner

info 'Checking dependencies...'
for cmd in curl ss python3 ollama msfconsole msfrpcd kali-server-mcp systemctl; do
  command -v "$cmd" >/dev/null 2>&1 || { error "Missing dependency: $cmd"; exit 1; }
done
[[ -x "$PYTHON" ]] || { error 'Missing .venv; install requirements first.'; exit 1; }
[[ -f "$DIR/agent.py" ]] || { error 'agent.py not found.'; exit 1; }
for file in /usr/share/mcp-kali-server/client.py /usr/share/metasploitmcp/MetasploitMCP.py; do
  [[ -f "$file" ]] || { error "Missing MCP component: $file"; exit 1; }
done
"$PYTHON" -c 'from mcp.server.fastmcp import FastMCP; import requests, fastapi, uvicorn, pymetasploit3, httpx, prompt_toolkit, rich' \
  >/dev/null 2>&1 || { error 'Python dependencies missing/incompatible; run .venv/bin/python3 -m pip install -r requirements.txt'; exit 1; }
success 'Dependencies available.'
info "Auto Nmap targets: $H4X_AUTO_TARGETS"

info 'Starting PostgreSQL...'
systemctl start postgresql
systemctl is-active --quiet postgresql || { error 'PostgreSQL unavailable.'; exit 1; }
success 'PostgreSQL ONLINE.'

info 'Starting Ollama...'
if ! curl -fsS --max-time 3 "$OLLAMA_URL/api/tags" >/dev/null 2>&1; then systemctl start ollama; fi
ollama_ready=false
for ((i=1;i<=30;i++)); do
  if curl -fsS --max-time 3 "$OLLAMA_URL/api/tags" >/dev/null 2>&1; then ollama_ready=true; break; fi
  sleep 1
done
[[ "$ollama_ready" == true ]] || { error 'Ollama API unavailable.'; exit 1; }
success 'Ollama ONLINE.'
info "Checking Ollama model: $MODEL"
if ! ollama show "$MODEL" >/dev/null 2>&1; then ollama pull "$MODEL"; fi
success "Model available: $MODEL"

info 'Checking Metasploit database...'
if command -v msfdb >/dev/null 2>&1; then
  msfdb status > "$DIR/logs/msfdb-status.log" 2>&1 || msfdb init
fi

info 'Preparing Metasploit RPC credentials...'
if [[ ! -s "$SECRET_FILE" ]]; then
  "$PYTHON" -c 'import secrets; print(secrets.token_urlsafe(32))' > "$SECRET_FILE"
fi
chmod 600 "$SECRET_FILE"
MSF_RPC_PASSWORD="$(cat "$SECRET_FILE")"
[[ -n "$MSF_RPC_PASSWORD" ]] || { error 'Empty RPC password.'; exit 1; }
export MSF_PASSWORD="$MSF_RPC_PASSWORD" MSF_SERVER="$RPC_HOST" MSF_SSL=false

listening() { ss -ltnH | awk '{print $4}' | grep -Fxq "$1"; }
rpc_auth_check() {
  MSF_PORT="$RPC_PORT" MSF_RPC_USER="$RPC_USER" "$PYTHON" - <<'PY' >/dev/null 2>&1
import os
from pymetasploit3.msfrpc import MsfRpcClient
client = MsfRpcClient(
    password=os.environ['MSF_PASSWORD'],
    username=os.environ['MSF_RPC_USER'],
    server=os.environ['MSF_SERVER'],
    port=int(os.environ['MSF_PORT']),
    ssl=False,
)
assert client.core.version
PY
}

info 'Checking Metasploit RPC authentication...'
RPC_REUSED=false
if [[ -s "$RPC_PORT_FILE" ]]; then
  saved_port="$(cat "$RPC_PORT_FILE")"
  if [[ "$saved_port" =~ ^[0-9]+$ ]] && (( saved_port >= 1 && saved_port <= 65535 )); then
    RPC_PORT="$saved_port"
    if listening "$RPC_HOST:$RPC_PORT" && rpc_auth_check; then RPC_REUSED=true; fi
  fi
fi
# Also reuse a correctly authenticated default instance on first run.
if [[ "$RPC_REUSED" != true ]]; then
  RPC_PORT=55553
  if listening "$RPC_HOST:$RPC_PORT" && rpc_auth_check; then RPC_REUSED=true; fi
fi
if [[ "$RPC_REUSED" == true ]]; then
  success "Reusing authenticated RPC instance on $RPC_HOST:$RPC_PORT"
else
  RPC_PORT=''
  for candidate in $(seq 55553 55580); do
    if ! listening "$RPC_HOST:$candidate" && ! listening "0.0.0.0:$candidate" && ! listening "[::]:$candidate"; then
      RPC_PORT="$candidate"
      break
    fi
  done
  [[ -n "$RPC_PORT" ]] || { error 'No free RPC port in 55553-55580.'; exit 1; }
  info "Starting Metasploit RPC on $RPC_HOST:$RPC_PORT..."
  msfrpcd -U "$RPC_USER" -P "$MSF_RPC_PASSWORD" -S -a "$RPC_HOST" -p "$RPC_PORT" -f \
    > "$DIR/logs/msfrpcd.log" 2>&1 &
  RPC_PID=$!
  echo "$RPC_PID" > "$DIR/logs/msfrpcd.pid"
  rpc_ready=false
  for ((i=1;i<=60;i++)); do
    if listening "$RPC_HOST:$RPC_PORT" && rpc_auth_check; then rpc_ready=true; break; fi
    if ! kill -0 "$RPC_PID" 2>/dev/null; then break; fi
    sleep 2
  done
  if [[ "$rpc_ready" != true ]]; then
    error 'RPC unavailable or authentication failed.'
    tail -n 30 "$DIR/logs/msfrpcd.log" 2>/dev/null || true
    exit 1
  fi
  success 'RPC started and authenticated.'
fi
printf '%s\n' "$RPC_PORT" > "$RPC_PORT_FILE"
chmod 600 "$RPC_PORT_FILE"
export MSF_PORT="$RPC_PORT"
rpc_auth_check || { error 'Final RPC authentication test failed.'; exit 1; }
success "Metasploit RPC AUTHENTICATED ($RPC_HOST:$RPC_PORT)"

info 'Checking Kali MCP API...'
if ! listening "$KALI_HOST:$KALI_PORT"; then
  kali-server-mcp --ip "$KALI_HOST" --port "$KALI_PORT" > "$DIR/logs/kali-mcp.log" 2>&1 &
  echo $! > "$DIR/logs/kali-mcp.pid"
fi
kali_ready=false
for ((i=1;i<=30;i++)); do
  if curl -fsS --max-time 3 "http://$KALI_HOST:$KALI_PORT/health" >/dev/null 2>&1; then
    kali_ready=true; break
  fi
  sleep 1
done
if [[ "$kali_ready" == true ]]; then
  success 'Kali MCP API HEALTHY.'
elif listening "$KALI_HOST:$KALI_PORT"; then
  warning 'Kali MCP listening; health endpoint not confirmed. MCP client will verify.'
else
  error 'Kali MCP API unavailable.'
  tail -n 30 "$DIR/logs/kali-mcp.log" 2>/dev/null || true
  exit 1
fi

# The agent uses these full paths for both MCP subprocesses.
# agent.py must explicitly forward MSF_* to MetasploitMCP.
export KALI_MCP_CMD="$PYTHON"
export KALI_MCP_ARGS="/usr/share/mcp-kali-server/client.py --server http://$KALI_HOST:$KALI_PORT"
export MSF_MCP_CMD="$PYTHON"
export MSF_MCP_ARGS='/usr/share/metasploitmcp/MetasploitMCP.py --transport stdio'
export OLLAMA_MODEL="$MODEL"
export OLLAMA_URL

echo
banner_line "$GRAY" '---------------------------------------------'
banner_line "$GREEN" 'ALL SYSTEMS READY'
banner_line "$GRAY" '---------------------------------------------'
success 'PostgreSQL    : ONLINE'
success 'Ollama        : ONLINE'
success "Model         : $MODEL"
success "Metasploit RPC: AUTHENTICATED ($RPC_HOST:$RPC_PORT)"
success 'MetasploitMCP : CONFIGURED'
success 'Kali MCP      : AVAILABLE'
success "Python        : $("$PYTHON" --version)"
echo
banner_line "$CYAN" 'LAUNCHING H4X LLM AGENT...'
echo
exec "$PYTHON" "$DIR/agent.py" --model "$MODEL" "$@"
