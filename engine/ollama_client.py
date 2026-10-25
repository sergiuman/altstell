"""
Local Ollama LLM Client for the AltStell Multi-Agent Graph Engine.
Uses local macOS Ollama daemon (default model: gemma2:latest) with structured JSON parsing,
automatic retry, latency tracking, and graceful deterministic fallback if daemon is offline.
"""
import json
import os
import re
import subprocess
import time
import urllib.request
import urllib.error
from typing import Any, Dict, Optional


OLLAMA_BASE_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("ALTSTELL_OLLAMA_MODEL", "gemma2:latest")


def ensure_ollama_running(timeout_sec: float = 8.0) -> bool:
    """Checks if Ollama HTTP API is live; attempts `ollama serve` in background if not."""
    if is_ollama_alive():
        return True
    try:
        subprocess.Popen(
            ["/opt/homebrew/bin/ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            if is_ollama_alive():
                return True
            time.sleep(0.5)
    except Exception:
        pass
    return is_ollama_alive()


def is_ollama_alive() -> bool:
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            return resp.status == 200
    except Exception:
        return False


def generate_text(
    prompt: str,
    system: str = "",
    model: str = DEFAULT_MODEL,
    temperature: float = 0.5,
    max_tokens: int = 1200,
    json_mode: bool = False,
    timeout: int = 90,
) -> Dict[str, Any]:
    """Invokes local Ollama /api/generate endpoint and returns {ok, text, latency_ms, model}."""
    t0 = time.time()
    if not ensure_ollama_running():
        return {
            "ok": False,
            "text": "",
            "error": "Ollama daemon unreachable",
            "latency_ms": int((time.time() - t0) * 1000),
            "model": model,
        }

    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }
    if system:
        payload["system"] = system
    if json_mode:
        payload["format"] = "json"

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return {
                "ok": True,
                "text": body.get("response", "").strip(),
                "latency_ms": int((time.time() - t0) * 1000),
                "model": model,
            }
    except Exception as exc:
        return {
            "ok": False,
            "text": "",
            "error": str(exc),
            "latency_ms": int((time.time() - t0) * 1000),
            "model": model,
        }


def generate_json(
    prompt: str,
    system: str = "",
    model: str = DEFAULT_MODEL,
    temperature: float = 0.4,
    max_tokens: int = 1600,
    retries: int = 2,
) -> Optional[Dict[str, Any]]:
    """Generates and parses structured JSON from local Ollama model with fenced-block cleanup."""
    for attempt in range(retries + 1):
        res = generate_text(
            prompt=prompt,
            system=system,
            model=model,
            temperature=temperature + (attempt * 0.1),
            max_tokens=max_tokens,
            json_mode=True,
        )
        if not res.get("ok") or not res.get("text"):
            continue
        raw = res["text"]
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    pass
    return None
