"""
Application configuration and file-path resolution.

Responsibilities
----------------
* Locate the application's base directory, both when running from source and
  when running as a PyInstaller one-file executable.
* Load the company Anthropic API key from a local ``.env`` file.
  The key is NEVER hardcoded and never written to disk by this application.
* Load the three predefined document templates at runtime (they are plain
  files under ``templates/`` so the business teams can edit them without
  touching the source code).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Default model / effort. These can be overridden in .env, but the defaults are
# what the app ships with.
DEFAULT_MODEL = "claude-opus-5"
DEFAULT_EFFORT = "high"

# Template file names inside the templates/ directory.
TEMPLATE_APPROVAL = "approval_document.json"
TEMPLATE_ACTION_PLAN = "action_plan.json"
TEMPLATE_PRESS_RELEASE = "press_release.txt"


class ConfigError(Exception):
    """Raised for configuration problems that the user can fix (missing key, missing template)."""


def bundle_dir() -> Path:
    """
    Directory that holds bundled read-only resources (the templates).

    * Running from source  -> the project root.
    * Running from a PyInstaller one-file build -> the temporary extraction
      directory that PyInstaller creates (``sys._MEIPASS``).
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return Path(__file__).resolve().parent.parent


def app_dir() -> Path:
    """
    Directory where the user's own files live (the ``.env`` file).

    For a packaged build this is the folder containing the .exe / .app, so the
    person deploying the tool can drop a ``.env`` next to the executable.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def templates_dir() -> Path:
    """Directory holding the three predefined document templates."""
    # A templates/ folder placed next to the executable wins over the bundled
    # one, so templates can be updated after packaging without a rebuild.
    external = app_dir() / "templates"
    if external.is_dir():
        return external
    return bundle_dir() / "templates"


def load_env() -> None:
    """
    Load environment variables from a ``.env`` file.
    """
    for candidate in (app_dir() / ".env", Path.cwd() / ".env"):
        if candidate.is_file():
            load_dotenv(candidate, override=True)
            return


def get_provider() -> str:
    """Return the active AI backend provider: 'anthropic' | 'local' | 'ollama' | 'openai'."""
    load_env()
    return (os.environ.get("AI_PROVIDER") or "anthropic").strip().lower()


def get_local_base_url() -> str:
    """Return the base URL for local fine-tuned models (e.g. Ollama or vLLM)."""
    load_env()
    return (os.environ.get("LOCAL_BASE_URL") or "http://localhost:11434/v1").strip()


def get_api_key() -> str:
    """
    Return the API key. For local models, a dummy key is accepted.
    """
    load_env()
    provider = get_provider()
    if provider in {"local", "ollama"}:
        return (os.environ.get("LOCAL_API_KEY") or "ollama-local").strip()

    key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not key:
        raise ConfigError(
            "APIキーが設定されていません。\n\n"
            f"次の場所に .env ファイルを作成し、社内のAPIキーを記入してください:\n"
            f"  {app_dir() / '.env'}\n\n"
            "内容の例:\n"
            "  ANTHROPIC_API_KEY=sk-ant-xxxxxxxx\n\n"
            "またはローカルモデル（Ollama/vLLM等）を使用する場合:\n"
            "  AI_PROVIDER=local\n"
            "  ANTHROPIC_MODEL=qwen2.5:3b\n"
            "  LOCAL_BASE_URL=http://localhost:11434/v1"
        )
    return key


def get_model() -> str:
    """Model ID to use for generation."""
    load_env()
    return (os.environ.get("ANTHROPIC_MODEL") or "").strip() or DEFAULT_MODEL


def get_effort() -> str:
    """Reasoning effort level passed to the API (low | medium | high | xhigh | max)."""
    load_env()
    effort = (os.environ.get("ANTHROPIC_EFFORT") or "").strip().lower()
    return effort if effort in {"low", "medium", "high", "xhigh", "max"} else DEFAULT_EFFORT


def _read_template(filename: str) -> str:
    path = templates_dir() / filename
    if not path.is_file():
        raise ConfigError(
            f"テンプレートファイルが見つかりません: {path}\n"
            f"(Template file not found: {path})"
        )
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:  # unreadable file, permission problem, ...
        raise ConfigError(f"テンプレートを読み込めません: {path}\n({exc})") from exc


def load_json_template(filename: str) -> dict:
    """Load and parse one of the JSON templates (Approval Document / Action Plan)."""
    raw = _read_template(filename)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"テンプレートのJSON形式が不正です: {templates_dir() / filename}\n({exc})"
        ) from exc


def load_text_template(filename: str) -> str:
    """Load one of the plain-text templates (Press Release)."""
    return _read_template(filename)
