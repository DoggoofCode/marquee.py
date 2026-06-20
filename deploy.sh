#!/usr/bin/env bash
set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
SERVICE="marquee"
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$APP_DIR/.venv"
PYTHON="$VENV/bin/python3"
PIP="$VENV/bin/pip"
SERVICE_FILE="/etc/systemd/system/$SERVICE.service"

# ── Helpers ───────────────────────────────────────────────────────────────────
info()    { echo "  $*"; }
section() { echo; echo "── $* ──────────────────────────────────────────────────"; }

# ── Pull latest code ──────────────────────────────────────────────────────────
section "Updating code"
git -C "$APP_DIR" pull --ff-only
info "Branch: $(git -C "$APP_DIR" branch --show-current)  |  $(git -C "$APP_DIR" log -1 --format='%h %s')"

# ── Python venv ───────────────────────────────────────────────────────────────
section "Python environment"
if [ ! -f "$PYTHON" ]; then
    info "Creating venv..."
    python3 -m venv "$VENV"
fi
info "Installing / upgrading dependencies..."
$PIP install --quiet --upgrade pip
$PIP install --quiet \
    nicegui \
    "pydantic>=2.7" \
    "pydantic-settings>=2.3" \
    plotly \
    httpx \
    python-dotenv \
    yfinance \
    numpy
info "Done."

# ── Data directory ────────────────────────────────────────────────────────────
section "Data directory"
mkdir -p "$APP_DIR/data"
info "$APP_DIR/data"

# ── Systemd service ───────────────────────────────────────────────────────────
section "Systemd service"
if [ ! -f "$SERVICE_FILE" ]; then
    info "Writing $SERVICE_FILE ..."
    # Detect the user running this script to own the service
    DEPLOY_USER="${SUDO_USER:-$(whoami)}"
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Marquee Portfolio Dashboard
After=network.target

[Service]
User=$DEPLOY_USER
WorkingDirectory=$APP_DIR
ExecStart=$PYTHON -m marquee.dashboard.app
Restart=on-failure
RestartSec=5
Environment=HOST=127.0.0.1
Environment=PORT=8080

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE"
    info "Service installed and enabled."
else
    info "Service file already exists — skipping write."
fi

# ── Restart ───────────────────────────────────────────────────────────────────
section "Restarting service"
sudo systemctl restart "$SERVICE"
sleep 2
STATUS=$(systemctl is-active "$SERVICE" 2>/dev/null || true)
if [ "$STATUS" = "active" ]; then
    info "marquee is running."
else
    echo
    echo "ERROR: service failed to start. Showing last 30 log lines:"
    sudo journalctl -u "$SERVICE" -n 30 --no-pager
    exit 1
fi

# ── Done ──────────────────────────────────────────────────────────────────────
section "Done"
info "App:     http://localhost:8080"
info "Logs:    sudo journalctl -u $SERVICE -f"
info "Status:  sudo systemctl status $SERVICE"
