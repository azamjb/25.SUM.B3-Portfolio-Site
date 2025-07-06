#!/bin/bash


PROJECT_DIR="$HOME/25.SUM.B3-Portfolio-Site-DigitalOcean/"
VENV_DIR="$PROJECT_DIR/venv"
SESSION_NAME="portfolio_site"

set -e

tmux kill-server || echo "No active tmux server to kill."

echo "Changing to project directory: $PROJECT_DIR"
cd "$PROJECT_DIR"

echo "Fetching latest commit and resetting"
git fetch origin && git reset origin/main --hard


echo "Activating venv"
source "$VENV_DIR/bin/activate"

echo "Installing/updating Python dependencies from requirements.txt..."
pip install -r requirements.txt

deactivate

echo "Starting new detached tmux session named '$SESSION_NAME'..."
tmux new-session -d -s "$SESSION_NAME"


tmux send-keys -t "$SESSION_NAME" "cd '$PROJECT_DIR'" C-m

tmux send-keys -t "$SESSION_NAME" "source '$VENV_DIR/bin/activate'" C-m

tmux send-keys -t "$SESSION_NAME" "gunicorn --bind 0.0.0.0:5000 app:app" C-m
