"""/**
 * @file mailer.py
 * @description SMTP mail sending (best-effort, never block the main process).
 */"""

from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
import smtplib
import ssl
import time
from typing import Optional

from .config import ErrmailConfig


@dataclass(frozen=True)
class MailPayload:
    """/**
     * @class MailPayload
     * @property {string} subject
     * @property {string} body
     */"""

    subject: str
    body: str


def can_send(cfg: ErrmailConfig) -> bool:
    """/**
     * @param {ErrmailConfig} cfg
     * @returns {boolean}
     */"""

    return bool(cfg.smtp_host and cfg.smtp_port and cfg.mail_from and cfg.mail_to)


def send_mail(cfg: ErrmailConfig, payload: MailPayload, timeout_seconds: int = 10) -> Optional[str]:
    """/**
     * @param {ErrmailConfig} cfg
     * @param {MailPayload} payload
     * @param {number} timeout_seconds
     * @returns {?string} error string (if failed)
     */"""

    if not can_send(cfg):
        return "missing SMTP config (ERRMAIL_SMTP_HOST/PORT, ERRMAIL_MAIL_FROM/TO)"

    msg = EmailMessage()
    msg["From"] = cfg.mail_from
    msg["To"] = cfg.mail_to
    msg["Subject"] = payload.subject
    msg.set_content(payload.body)

    try:
        # Priority: SMTP_SSL (implicit TLS, usually port 465) > STARTTLS (usually port 587) > plain.
        if cfg.smtp_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(cfg.smtp_host, cfg.smtp_port, timeout=timeout_seconds, context=context) as s:
                if cfg.smtp_user and cfg.smtp_pass:
                    s.login(cfg.smtp_user, cfg.smtp_pass)
                s.send_message(msg)
        elif cfg.smtp_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port, timeout=timeout_seconds) as s:
                s.ehlo()
                s.starttls(context=context)
                s.ehlo()
                if cfg.smtp_user and cfg.smtp_pass:
                    s.login(cfg.smtp_user, cfg.smtp_pass)
                s.send_message(msg)
        else:
            with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port, timeout=timeout_seconds) as s:
                if cfg.smtp_user and cfg.smtp_pass:
                    s.login(cfg.smtp_user, cfg.smtp_pass)
                s.send_message(msg)
        return None
    except Exception as e:  # noqa: BLE001
        return f"{type(e).__name__}: {e}"


def build_subject(service: str, kind: str, fp: str) -> str:
    """/**
     * @param {string} service
     * @param {string} kind
     * @param {string} fp
     * @returns {string}
     */"""

    return f"[errmail] {service} {kind} fp={fp}"


def format_body(
    *,
    service: str,
    command: list[str],
    cwd: str,
    pid: int | None,
    exit_code: int | None,
    kind: str,
    fp: str,
    message: str,
    excerpt: str,
    tail: str,
    ts: float | None = None,
) -> str:
    """/**
     * @param {string} service
     * @param {Array<string>} command
     * @param {string} cwd
     * @param {?number} pid
     * @param {?number} exit_code
     * @param {string} kind
     * @param {string} fp
     * @param {string} message
     * @param {string} excerpt
     * @param {string} tail
     * @param {?number} ts
     * @returns {string}
     */"""

    t = ts or time.time()
    when = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
    cmd_str = " ".join(command)

    parts = [
        f"Time: {when}",
        f"Service: {service}",
        f"Kind: {kind}",
        f"Fingerprint: {fp}",
        f"PID: {pid}",
        f"ExitCode: {exit_code}",
        f"CWD: {cwd}",
        f"Command: {cmd_str}",
        "",
        "Message:",
        message,
        "",
        "Excerpt:",
        excerpt.rstrip("\n"),
        "",
        "Stderr Tail:",
        tail.rstrip("\n"),
        "",
    ]
    return "\n".join(parts)

