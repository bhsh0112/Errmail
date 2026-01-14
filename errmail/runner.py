"""/**
 * @file runner.py
 * @description Run a subprocess, passthrough stdout/stderr, and detect stderr errors.
 */"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from typing import Optional

from .config import ErrmailConfig
from .detector import ErrorEvent, StderrDetector
from .notifier import Notifier
from .utils import fingerprint


def _pump_stdout(stream: Optional[object]) -> None:
    """/**
     * @param {?object} stream
     */"""

    if stream is None:
        return
    try:
        for line in iter(stream.readline, ""):
            sys.stdout.write(line)
            sys.stdout.flush()
    except Exception:  # noqa: BLE001
        return


def _pump_stderr(stream: Optional[object], detector: StderrDetector, on_event) -> None:
    """/**
     * @param {?object} stream
     * @param {StderrDetector} detector
     * @param {Function} on_event
     */"""

    if stream is None:
        return
    try:
        for line in iter(stream.readline, ""):
            sys.stderr.write(line)
            sys.stderr.flush()
            evt = detector.push_line(line)
            if evt is not None:
                on_event(evt)
    except Exception:  # noqa: BLE001
        return


def run_command(
    command: list[str],
    *,
    cfg: ErrmailConfig,
    cwd: str | None = None,
    verbose: bool = False,
) -> int:
    """/**
     * @param {Array<string>} command
     * @param {ErrmailConfig} cfg
     * @param {?string} cwd
     * @param {boolean} verbose
     * @returns {number} exit code
     */"""

    workdir = cwd or os.getcwd()
    detector = StderrDetector(tail_lines=cfg.tail_lines)
    notifier = Notifier(cfg, command=command, cwd=workdir, verbose=verbose)

    # NOTE: text=True + bufsize=1 gives line-buffered behavior for many commands,
    # but some programs still buffer; passthrough is still best-effort.
    p = subprocess.Popen(  # noqa: S603
        command,
        cwd=workdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
        errors="replace",
    )

    pid = p.pid
    seen_any_event = False

    def on_event(evt: ErrorEvent) -> None:
        nonlocal seen_any_event
        seen_any_event = True
        notifier.enqueue(evt, pid=pid, exit_code=None, tail=detector.tail_text())

    t_out = threading.Thread(target=_pump_stdout, args=(p.stdout,), daemon=True)
    t_err = threading.Thread(target=_pump_stderr, args=(p.stderr, detector, on_event), daemon=True)
    t_out.start()
    t_err.start()

    exit_code = p.wait()
    # Give pump threads a moment to flush remaining lines.
    t_out.join(timeout=1.0)
    t_err.join(timeout=1.0)

    if exit_code != 0 and not seen_any_event:
        tail = detector.tail_text()
        msg = f"process exited with code {exit_code}"
        excerpt = (msg + "\n").strip() + "\n"
        fp = fingerprint(msg + "\n" + " ".join(command))
        evt = ErrorEvent(kind="exit-nonzero", fp=fp, message=msg, excerpt=excerpt, ts=time.time())
        notifier.enqueue(evt, pid=pid, exit_code=exit_code, tail=tail)

    # Best-effort: allow background email thread to process queued notifications.
    notifier.flush(timeout_seconds=2.0)

    return exit_code

