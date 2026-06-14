#!/usr/bin/env zsh

# Agent-OS bootstrap draft.
# Purpose:
# - Load the single shared secrets file: ~/.env-secrets
# - Detect the current terminal/runtime context where possible
# - Keep native harness auth paths clean for Claude Code / Codex / Gemini
# - Avoid scattering per-project .env files
#
# Source this from ~/.zshrc once you are happy with the behavior.

typeset -g AGENT_BOOTSTRAP_SECRETS_FILE="${HOME}/.env-secrets"
typeset -g AGENT_RUNTIME="${AGENT_RUNTIME:-unknown}"
typeset -g AGENT_SHELL_CONTEXT="${AGENT_SHELL_CONTEXT:-unknown}"
typeset -g AGENT_RUNTIME_PROMPTED="${AGENT_RUNTIME_PROMPTED:-0}"

typeset -g AGENT_BOOTSTRAP_OPENAI_SNAPSHOT=""
typeset -g AGENT_BOOTSTRAP_GEMINI_SNAPSHOT=""

agent_bootstrap_load_secrets() {
  if [[ -f "$AGENT_BOOTSTRAP_SECRETS_FILE" ]]; then
    source "$AGENT_BOOTSTRAP_SECRETS_FILE"
  fi
}

agent_bootstrap_detect_shell_context() {
  if [[ -n "${CODING_AGENT:-}" ]]; then
    print -r -- "${CODING_AGENT}"
    return
  fi

  case "${TERM_PROGRAM:-}" in
    Obsidian|obsidian)
      print -r -- "obsidian-terminal"
      return
      ;;
    Warp|WarpTerminal)
      print -r -- "warp-terminal"
      return
      ;;
    VSCode|vscode|vscodium)
      print -r -- "vscode-terminal"
      return
      ;;
    Apple_Terminal|Terminal)
      print -r -- "terminal"
      return
      ;;
  esac

  if [[ -n "${VSCODE_PID:-}" ]]; then
    print -r -- "vscode-terminal"
    return
  fi

  print -r -- "terminal"
}

agent_bootstrap_prompt_runtime() {
  if [[ "$AGENT_RUNTIME_PROMPTED" == "1" ]]; then
    return
  fi

  if [[ ! -t 0 ]]; then
    return
  fi

  print -n -- "Agent-OS runtime unknown. Are you in Claude Code CLI, Codex CLI, Gemini CLI, or other? [claude/codex/gemini/other]: "
  local reply
  read -r reply

  case "${reply:l}" in
    claude*)
      AGENT_RUNTIME="claude-cli"
      ;;
    codex*)
      AGENT_RUNTIME="codex-cli"
      ;;
    gemini*)
      AGENT_RUNTIME="gemini-cli"
      ;;
    *)
      AGENT_RUNTIME="terminal"
      ;;
  esac

  AGENT_RUNTIME_PROMPTED=1
}

agent_bootstrap_save_env_snapshot() {
  AGENT_BOOTSTRAP_OPENAI_SNAPSHOT="${OPENAI_API_KEY-__UNSET__}"
  AGENT_BOOTSTRAP_GEMINI_SNAPSHOT="${GEMINI_API_KEY-__UNSET__}"
}

agent_bootstrap_restore_env_snapshot() {
  if [[ "$AGENT_BOOTSTRAP_OPENAI_SNAPSHOT" == "__UNSET__" ]]; then
    unset OPENAI_API_KEY
  else
    export OPENAI_API_KEY="$AGENT_BOOTSTRAP_OPENAI_SNAPSHOT"
  fi

  if [[ "$AGENT_BOOTSTRAP_GEMINI_SNAPSHOT" == "__UNSET__" ]]; then
    unset GEMINI_API_KEY
  else
    export GEMINI_API_KEY="$AGENT_BOOTSTRAP_GEMINI_SNAPSHOT"
  fi
}

agent_bootstrap_command_kind() {
  local cmd="$1"

  case "$cmd" in
    codex|codex\ *)
      print -r -- "codex-cli"
      return
      ;;
    claude|claude\ *)
      print -r -- "claude-cli"
      return
      ;;
    gemini|gemini\ *)
      print -r -- "gemini-cli"
      return
      ;;
    *process_image_ingest.py*|*rename_screenshots.py*|*update_asset_notes_vision.py*)
      print -r -- "gemini-vision-script"
      return
      ;;
    *process_video_ingest.py*)
      print -r -- "video-ingest-script"
      return
      ;;
  esac

  print -r -- "generic"
}

agent_bootstrap_preexec() {
  local cmd="$1"

  agent_bootstrap_save_env_snapshot

  case "$(agent_bootstrap_command_kind "$cmd")" in
    codex-cli|claude-cli)
      # Keep native subscription/auth paths clean for the agent CLI itself.
      unset OPENAI_API_KEY
      unset GEMINI_API_KEY
      ;;
    gemini-cli|gemini-vision-script)
      # Gemini-based commands can use the shared key from ~/.env-secrets.
      [[ -n "${GEMINI_API_KEY:-}" ]] && export GEMINI_API_KEY
      ;;
    video-ingest-script)
      # Leave the current env intact. The script can decide which providers it needs.
      ;;
    generic)
      # No changes.
      ;;
  esac
}

preexec() {
  agent_bootstrap_preexec "$1"
}

precmd() {
  agent_bootstrap_restore_env_snapshot
}

agent() {
  local subcommand="$1"
  shift

  case "$subcommand" in
    codex)
      AGENT_RUNTIME="codex-cli"
      command codex "$@"
      ;;
    claude)
      AGENT_RUNTIME="claude-cli"
      command claude "$@"
      ;;
    gemini)
      AGENT_RUNTIME="gemini-cli"
      command gemini "$@"
      ;;
    *)
      if [[ "$AGENT_RUNTIME" == "unknown" ]]; then
        agent_bootstrap_prompt_runtime
      fi
      command "$subcommand" "$@"
      ;;
  esac
}

claude() {
  AGENT_RUNTIME="claude-cli"
  command claude "$@"
}

codex() {
  AGENT_RUNTIME="codex-cli"
  command codex "$@"
}

gemini() {
  AGENT_RUNTIME="gemini-cli"
  command gemini "$@"
}

agy() {
  AGENT_RUNTIME="antigravity-cli"
  command agy "$@"
}

agent_bootstrap_load_secrets
AGENT_SHELL_CONTEXT="$(agent_bootstrap_detect_shell_context)"
AGENT_RUNTIME="unknown"
