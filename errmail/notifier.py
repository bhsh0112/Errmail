"""/**
 * @file notifier.py
 * @description Background notification worker with cooldown + best-effort delivery.
 */"""

from __future__ import annotations

from dataclasses import replace
import os
import queue
import threading
import time
from typing import Optional

from .config import ErrmailConfig
from .detector import ErrorEvent
from .mailer import MailPayload, build_subject, format_body, send_mail


class Notifier:
    """/**
     * @class Notifier
     * @description Enqueue events and send emails in a background thread.
     *
     * Guarantees:
     * - Never blocks the main process on SMTP.
     * - Cooldown per fingerprint to avoid email storms.
     *
     * @param {ErrmailConfig} cfg
     * @param {Array<string>} command
     * @param {string} cwd
     * @param {boolean} verbose
     */"""

    def __init__(self, cfg: ErrmailConfig, command: list[str], cwd: str, verbose: bool = False) -> None:
        self._cfg = cfg
        self._command = command
        self._cwd = cwd
        self._verbose = verbose

        self._q: "queue.Queue[tuple[ErrorEvent, int | None, int | None, str]]" = queue.Queue()
        self._lock = threading.Lock()
        self._last_sent: dict[str, float] = {}

        self._thread = threading.Thread(target=self._worker, name="errmail-notifier", daemon=True)
        self._thread.start()

    def enqueue(self, event: ErrorEvent, *, pid: int | None, exit_code: int | None, tail: str) -> None:
        """/**
         * @param {ErrorEvent} event
         * @param {?number} pid
         * @param {?number} exit_code
         * @param {string} tail
         */"""

        if not self._should_send(event.fp):
            return
        try:
            self._q.put_nowait((event, pid, exit_code, tail))
        except Exception:  # noqa: BLE001
            # Best-effort; never break the main flow.
            return

    def _should_send(self, fp: str) -> bool:
        """/**
         * @param {string} fp
         * @returns {boolean}
         */"""

        now = time.time()
        with self._lock:
            last = self._last_sent.get(fp, 0.0)
            if now - last < self._cfg.cooldown_seconds:
                return False
            self._last_sent[fp] = now
            return True

    def _worker(self) -> None:
        """/**
         * @returns {void}
         */"""

        while True:
            try:
                event, pid, exit_code, tail = self._q.get()
            except Exception:  # noqa: BLE001
                continue

            subject = build_subject(self._cfg.service, event.kind, event.fp)
            body = format_body(
                service=self._cfg.service,
                command=self._command,
                cwd=self._cwd,
                pid=pid,
                exit_code=exit_code,
                kind=event.kind,
                fp=event.fp,
                message=event.message,
                excerpt=event.excerpt,
                tail=tail,
                ts=event.ts,
            )
            err = send_mail(self._cfg, MailPayload(subject=subject, body=body))
            if err and self._verbose:
                try:
                    print(f"[errmail] send failed: {err}", file=os.sys.stderr)
                except Exception:  # noqa: BLE001
                    pass
            try:
                self._q.task_done()
            except Exception:  # noqa: BLE001
                pass

    def flush(self, timeout_seconds: float = 2.0) -> None:
        """/**
         * @description Best-effort wait for queued notifications to be processed.
         * @param {number} timeout_seconds
         * @returns {void}
         */"""

        end = time.time() + max(0.0, timeout_seconds)
        # queue.join() has no timeout, so we poll unfinished_tasks.
        while time.time() < end:
            try:
                if getattr(self._q, "unfinished_tasks", 0) == 0:
                    return
            except Exception:  # noqa: BLE001
                return
            time.sleep(0.05)


def with_overrides(
    cfg: ErrmailConfig,
    *,
    service: Optional[str] = None,
    cooldown_seconds: Optional[int] = None,
    tail_lines: Optional[int] = None,
    mail_to: Optional[str] = None,
) -> ErrmailConfig:
    """/**
     * @param {ErrmailConfig} cfg
     * @param {?string} service
     * @param {?number} cooldown_seconds
     * @param {?number} tail_lines
     * @returns {ErrmailConfig}
     */"""

    return replace(
        cfg,
        service=service or cfg.service,
        cooldown_seconds=cooldown_seconds if cooldown_seconds is not None else cfg.cooldown_seconds,
        tail_lines=tail_lines if tail_lines is not None else cfg.tail_lines,
        mail_to=mail_to or cfg.mail_to,
    )

