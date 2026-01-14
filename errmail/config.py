"""/**
 * @file config.py
 * @description Read configuration from environment variables.
 */"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class ErrmailConfig:
    """/**
     * @class ErrmailConfig
     *
     * @property {string} smtp_host
     * @property {number} smtp_port
     * @property {string} smtp_user
     * @property {string} smtp_pass
     * @property {boolean} smtp_tls
     * @property {string} mail_from
     * @property {string} mail_to
     * @property {number} cooldown_seconds
     * @property {number} tail_lines
     * @property {string} service
     */"""

    smtp_host: str | None
    smtp_port: int
    smtp_user: str | None
    smtp_pass: str | None
    smtp_tls: bool
    smtp_ssl: bool
    mail_from: str | None
    mail_to: str | None
    cooldown_seconds: int
    tail_lines: int
    service: str


def _read_kv_env_file(path: str) -> dict[str, str]:
    """/**
     * @description Parse a simple KEY=VALUE file (like .env).
     * Lines starting with # are ignored.
     *
     * @param {string} path
     * @returns {Object<string, string>}
     */"""

    p = Path(path).expanduser()
    if not p.exists() or not p.is_file():
        return {}
    data: dict[str, str] = {}
    try:
        for raw in p.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            key = k.strip()
            val = v.strip().strip("'").strip('"')
            if key:
                data[key] = val
    except Exception:  # noqa: BLE001
        return {}
    return data


def _coalesce(*vals: Optional[str]) -> Optional[str]:
    """/**
     * @param {...?string} vals
     * @returns {?string}
     */"""

    for v in vals:
        if v is not None and str(v).strip() != "":
            return v
    return None


def _env_bool(name: str, default: bool) -> bool:
    """/**
     * @param {string} name
     * @param {boolean} default
     * @returns {boolean}
     */"""

    raw = os.getenv(name)
    if raw is None:
        return default
    raw = raw.strip().lower()
    return raw in ("1", "true", "yes", "y", "on")


def _env_int(name: str, default: int) -> int:
    """/**
     * @param {string} name
     * @param {number} default
     * @returns {number}
     */"""

    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def load_config(service: str | None = None) -> ErrmailConfig:
    """/**
     * @param {?string} service
     * @returns {ErrmailConfig}
     */"""

    svc = service or os.getenv("ERRMAIL_SERVICE") or "unknown-service"
    # Support "preset SMTP": your org can provision /etc/errmail.env once,
    # and end-users only set their own recipient email.
    #
    # Precedence: ENV > config file.
    cfg_path = os.getenv("ERRMAIL_CONFIG_FILE")
    preset_paths = []
    if cfg_path:
        preset_paths.append(cfg_path)
    preset_paths.extend(
        [
            "/etc/errmail.env",
            str(Path.home() / ".errmail.env"),
        ]
    )
    preset: dict[str, str] = {}
    for p in preset_paths:
        preset.update(_read_kv_env_file(p))

    return ErrmailConfig(
        smtp_host=_coalesce(os.getenv("ERRMAIL_SMTP_HOST"), preset.get("ERRMAIL_SMTP_HOST")),
        smtp_port=_env_int("ERRMAIL_SMTP_PORT", 587),
        smtp_user=_coalesce(os.getenv("ERRMAIL_SMTP_USER"), preset.get("ERRMAIL_SMTP_USER")),
        smtp_pass=_coalesce(os.getenv("ERRMAIL_SMTP_PASS"), preset.get("ERRMAIL_SMTP_PASS")),
        smtp_tls=_env_bool("ERRMAIL_SMTP_TLS", True),
        smtp_ssl=_env_bool("ERRMAIL_SMTP_SSL", False),
        mail_from=_coalesce(os.getenv("ERRMAIL_MAIL_FROM"), preset.get("ERRMAIL_MAIL_FROM")),
        mail_to=_coalesce(os.getenv("ERRMAIL_MAIL_TO"), preset.get("ERRMAIL_MAIL_TO")),
        cooldown_seconds=_env_int("ERRMAIL_COOLDOWN_SECONDS", 300),
        tail_lines=_env_int("ERRMAIL_TAIL_LINES", 200),
        service=svc,
    )

