"""
Thin wrapper around the Anthropic (Claude) Python SDK.

Everything the rest of the app needs from the API lives here:

* creating the client with the company API key from ``.env``
* a cheap connectivity / credential check used before a run starts
* ``complete_text``  -> plain-text generation (Press Release)
* ``complete_json``  -> schema-constrained JSON generation (Approval / Action Plan)
* translation of SDK exceptions into clear, user-facing Japanese messages

All requests are streamed. Streaming avoids HTTP read timeouts on the long
outputs these documents produce; ``get_final_message()`` gives back the whole
message once the stream completes.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

import anthropic

from core import config

# Generous output ceiling -- business documents are long, and streaming means
# a high ceiling costs nothing when the model finishes early.
MAX_TOKENS = 16000


# ---------------------------------------------------------------------------
# Error types -- each carries a message that is safe to show the user directly
# ---------------------------------------------------------------------------

class AIClientError(Exception):
    """Base class for all failures raised by this module."""


class NoConnectionError(AIClientError):
    """No internet connection / the API host is unreachable."""


class AuthError(AIClientError):
    """The API key is missing, invalid, expired or lacks permission."""


class RateLimitedError(AIClientError):
    """The organisation's rate limit was hit."""


class ServiceError(AIClientError):
    """Anthropic returned a server-side error, or the request was rejected."""


class MalformedResponseError(AIClientError):
    """The model's answer could not be used (not valid JSON, empty, refused)."""


def _wrap(exc: Exception) -> AIClientError:
    """Map an SDK exception onto one of our user-facing error types."""
    if isinstance(exc, anthropic.APIConnectionError):
        return NoConnectionError(
            "インターネットに接続できません。\n\n"
            "ネットワーク接続を確認してから、もう一度実行してください。\n"
            "社内プロキシ環境の場合は、api.anthropic.com への通信が許可されているか"
            "情報システム部門にご確認ください。\n\n"
            "(No internet connection: could not reach api.anthropic.com)"
        )
    if isinstance(exc, anthropic.AuthenticationError):
        return AuthError(
            "APIキーが無効です。\n\n"
            f".env ファイル（{config.app_dir() / '.env'}）の ANTHROPIC_API_KEY を"
            "確認してください。キーが失効している可能性もあります。\n\n"
            "(Invalid or expired API key.)"
        )
    if isinstance(exc, anthropic.PermissionDeniedError):
        return AuthError(
            "APIキーに必要な権限がありません。\n\n"
            "社内の管理者にキーの権限をご確認ください。\n\n"
            "(The API key lacks the required permission.)"
        )
    if isinstance(exc, anthropic.NotFoundError):
        return ServiceError(
            f"指定されたモデルが見つかりません: {config.get_model()}\n\n"
            ".env の ANTHROPIC_MODEL の値を確認してください。\n\n"
            "(Model not found.)"
        )
    if isinstance(exc, anthropic.RateLimitError):
        return RateLimitedError(
            "APIの利用制限に達しました。\n\n"
            "しばらく待ってから、もう一度実行してください。\n\n"
            "(Rate limited. Please retry in a few minutes.)"
        )
    if isinstance(exc, anthropic.APIStatusError):
        status = getattr(exc, "status_code", "?")
        detail = getattr(exc, "message", str(exc))
        if isinstance(status, int) and status >= 500:
            return ServiceError(
                "Anthropic側で一時的な障害が発生しています。\n\n"
                "しばらく待ってから、もう一度実行してください。\n\n"
                f"(Server error {status}: {detail})"
            )
        return ServiceError(f"APIリクエストが拒否されました。\n\n(API error {status}: {detail})")
    if isinstance(exc, anthropic.APIError):
        return ServiceError(f"API呼び出しに失敗しました。\n\n({exc})")
    return ServiceError(f"予期しないエラーが発生しました。\n\n({exc})")


# ---------------------------------------------------------------------------
# JSON recovery helper
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def _parse_json(text: str) -> dict:
    """
    Parse the model's answer as JSON.
    """
    cleaned = _FENCE_RE.sub("", text.strip())
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end <= start:
            raise MalformedResponseError(
                "AIの応答をJSONとして解釈できませんでした。\n\n"
                "もう一度実行してください。繰り返し失敗する場合は、"
                "企画書の内容が読み取れているかご確認ください。\n\n"
                f"(Malformed AI response: {cleaned[:300]})"
            ) from None
        try:
            parsed = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise MalformedResponseError(
                "AIの応答をJSONとして解釈できませんでした。\n\n"
                "もう一度実行してください。\n\n"
                f"(Malformed AI response: {exc})"
            ) from exc

    if not isinstance(parsed, dict):
        raise MalformedResponseError(
            "AIの応答形式が想定と異なります（オブジェクトではありません）。\n\n"
            "もう一度実行してください。"
        )
    return parsed


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class AIClient:
    """
    Unified client supporting both Anthropic Claude API and local fine-tuned models
    (via Ollama / vLLM / OpenAI-compatible HTTP endpoints).
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.provider = config.get_provider()
        self.model = config.get_model()
        self.effort = config.get_effort()
        self.local_url = config.get_local_base_url()
        self.key = api_key or config.get_api_key()

        if self.provider == "anthropic":
            self._client = anthropic.Anthropic(api_key=self.key, max_retries=2, timeout=600.0)
        else:
            self._client = None

    # -- pre-flight ---------------------------------------------------------

    def check_ready(self) -> None:
        """Verify connectivity and credentials before starting a run."""
        if self.provider == "anthropic":
            try:
                self._client.models.retrieve(self.model)
            except Exception as exc:
                raise _wrap(exc) from exc
        else:
            # Check local server connectivity.
            endpoint = f"{self.local_url.rstrip('/')}/models"
            try:
                req = urllib.request.Request(endpoint, headers={"Authorization": f"Bearer {self.key}"})
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    if resp.status != 200:
                        raise ServiceError(f"ローカルモデルサーバーからの応答コード: {resp.status}")
                    body = json.loads(resp.read().decode("utf-8"))
            except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as exc:
                raise NoConnectionError(
                    f"ローカルAIサーバー（{self.local_url}）に接続できません。\n\n"
                    "Ollama や vLLM が起動しているかご確認ください。\n\n"
                    f"({exc})"
                ) from exc

            # A reachable server does not guarantee the *configured* model is
            # actually loaded there -- catch that mismatch now, with a
            # specific message, rather than a raw HTTP 404 mid-generation.
            available = [m.get("id", "") for m in body.get("data", []) if isinstance(m, dict)]
            configured = self.model
            if available and not any(
                m == configured or m.startswith(f"{configured}:") for m in available
            ):
                raise ServiceError(
                    f"モデル「{configured}」がローカルサーバーに見つかりません。\n\n"
                    f".env の ANTHROPIC_MODEL を確認するか、次のコマンドでモデルを"
                    f"作成/取得してください:\n  ollama create {configured} -f Modelfile\n\n"
                    f"利用可能なモデル: {', '.join(available) if available else '(なし)'}"
                )

    # -- generation ---------------------------------------------------------

    def _call_local(self, system: str, user: str, schema: dict | None = None) -> str:
        """Call local OpenAI-compatible Chat Completions endpoint (Ollama/vLLM)."""
        endpoint = f"{self.local_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": 2500,
            "temperature": 0.1,
            "stop": ["<|im_end|>", "<|endoftext|>", "\n\n\n\n"],
        }
        if schema:
            payload["response_format"] = {"type": "json_object"}

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=600.0) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300] if exc.fp else ""
            raise ServiceError(
                f"ローカルモデルがエラーを返しました（{exc.code}）。\n\n"
                f"モデル名が正しいか、サーバーが正常に応答しているかご確認ください。\n\n"
                f"({detail or exc.reason})"
            ) from exc
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as exc:
            raise NoConnectionError(
                f"ローカルAIサーバー（{self.local_url}）との通信が切断されました。\n\n"
                "Ollama や vLLM が起動したままか、生成の途中で停止していないかご確認ください。\n\n"
                f"({exc})"
            ) from exc
        except json.JSONDecodeError as exc:
            raise MalformedResponseError(
                "ローカルモデルからの応答形式が不正です。\n\n"
                f"サーバーの実装がOpenAI互換のレスポンス形式に対応しているかご確認ください。\n\n"
                f"({exc})"
            ) from exc

        try:
            return res_data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise MalformedResponseError(
                "ローカルモデルからの応答に生成結果が含まれていません。\n\n"
                f"({exc}: {str(res_data)[:300]})"
            ) from exc

    def _stream(self, system: str, user: str, output_config: dict) -> str:
        """Run request via Anthropic API."""
        try:
            with self._client.messages.stream(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=system,
                messages=[{"role": "user", "content": user}],
                output_config=output_config,
            ) as stream:
                message = stream.get_final_message()
        except Exception as exc:
            raise _wrap(exc) from exc

        if message.stop_reason == "refusal":
            raise MalformedResponseError("AIが安全上の理由でこの内容の生成を拒否しました。")

        text = "".join(block.text for block in message.content if block.type == "text").strip()
        if not text:
            raise MalformedResponseError("AIから空の応答が返されました。")
        return text

    def complete_text(self, system: str, user: str) -> str:
        """Generate plain text (Press Release)."""
        if self.provider == "anthropic":
            return self._stream(system, user, {"effort": self.effort})
        return self._call_local(system, user)

    def complete_json(self, system: str, user: str, schema: dict) -> dict:
        """Generate JSON constrained to schema."""
        if self.provider == "anthropic":
            output_config = {
                "effort": self.effort,
                "format": {"type": "json_schema", "schema": schema},
            }
            try:
                text = self._stream(system, user, output_config)
            except ServiceError:
                text = self._stream(
                    system + "\n\n出力は有効なJSONオブジェクトのみとし、コードフェンスを含めないこと。",
                    user,
                    {"effort": self.effort},
                )
        else:
            text = self._call_local(system, user, schema=schema)

        return _parse_json(text)
