#!/bin/bash

APP_NAME="Koopman Analysis GUI"
REPO_URL="https://github.com/fumito100111/koopman-analysis-gui.git"

function error() {
  echo "Error: $1"
  exit 1
}

function setup() {
  if ! command -v python3 &> /dev/null; then
      echo "Python 3 is not installed. Please install Python 3 to run this application."
      exit 1
  fi

  if [ ! -d ".venv" ]; then
      echo "Creating virtual environment from $(python3 --version)"
      python3 -m venv .venv
  fi

  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
}

function add_path() {
  BIN="$1"
  case "$(uname -s)" in
    Darwin*)
      PATH_FILE="$HOME/.zshrc"
      ;;
    Linux*)
      PATH_FILE="$HOME/.bashrc"
      ;;
    *)
      error "Unsupported OS: $(uname -s). This application supports only macOS and Linux."
      ;;
  esac

  if ! grep -q "export PATH=\"$BIN:\$PATH\"" "$PATH_FILE"; then
    echo "export PATH=\"$BIN:\$PATH\"" >> "$PATH_FILE"
    source "$PATH_FILE"
  fi
}

function move_executable() {
  case "$(uname -s)" in
    Darwin*)
      BIN="$HOME/.local/bin"
      ;;
    Linux*)
      BIN="$HOME/.local/bin"
      ;;
    *)
      error "Unsupported OS: $(uname -s). This application supports only macOS and Linux."
      ;;
  esac
  mkdir -p "$BIN" || error "Failed to create bin directory at $BIN."
  cp "$APP_DATA/kagui" "$BIN/" || error "Failed to copy executable to $BIN."
  chmod +x "$BIN/kagui" || error "Failed to make executable at $BIN/kagui."
  add_path "$BIN"
}

function update() {
  cd "$APP_DATA" || error "Failed to navigate to application directory at $APP_DATA."
  git pull origin main || error "Failed to update application from repository."
  setup
  move_executable
}

function install() {
  case "$(uname -s)" in
    Darwin*)
      APP_DATA="$HOME/.local/share/koopman-analysis-gui"
      ;;
    Linux*)
      APP_DATA="$HOME/.local/share/koopman-analysis-gui"
      ;;
    *)
      error "Unsupported OS: $(uname -s). This application supports only macOS and Linux."
      ;;
  esac

  if [ -d "$APP_DATA" ]; then
    echo "Already installed at $APP_DATA."
    update
    echo "\nUpdated successfully."
    exit 0
  fi

  if ! command -v git &> /dev/null; then
    error "Git is not installed. Please install Git to proceed."
  fi

  git clone "$REPO_URL" "$APP_DATA" || error "Failed to clone repository from $REPO_URL."
  cd "$APP_DATA" || error "Failed to navigate to application directory at $APP_DATA."
  setup
  move_executable
}

install