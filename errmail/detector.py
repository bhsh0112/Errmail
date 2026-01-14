"""/**
 * @file detector.py
 * @description Detect "error events" from stderr line stream.
 */"""

from __future__ import annotations

from dataclasses import dataclass
import re
import time
from typing import Optional

from .utils import RingBuffer, fingerprint


@dataclass(frozen=True)
class ErrorEvent:
    """/**
     * @class ErrorEvent
     * @property {string} kind
     * @property {string} fp
     * @property {string} message
     * @property {string} excerpt
     * @property {number} ts
     */"""

    kind: str
    fp: str
    message: str
    excerpt: str
    ts: float


_RE_PY_TRACEBACK_START = re.compile(r"^Traceback \(most recent call last\):\s*$")
_RE_PY_EXCEPTION_LINE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(Error|Exception|Warning)\b.*")
_RE_GENERIC_ERROR = re.compile(r"\b(ERROR|CRITICAL|FATAL)\b")


class StderrDetector:
    """/**
     * @class StderrDetector
     * @description Feed stderr lines and produce structured ErrorEvent when detected.
     *
     * @param {number} tail_lines
     */"""

    def __init__(self, tail_lines: int = 200) -> None:
        self._tail = RingBuffer(max_lines=tail_lines)
        self._in_tb = False
        self._tb_lines: list[str] = []

    def push_line(self, line: str) -> Optional[ErrorEvent]:
        """/**
         * @param {string} line
         * @returns {?ErrorEvent}
         */"""

        self._tail.push(line)

        if _RE_PY_TRACEBACK_START.match(line.rstrip("\n")):
            self._in_tb = True
            self._tb_lines = [line]
            return None

        if self._in_tb:
            self._tb_lines.append(line)
            # Python traceback ends with the exception line; emit immediately.
            if _RE_PY_EXCEPTION_LINE.match(line.strip()):
                excerpt = "".join(self._tb_lines[-40:])  # keep email short
                msg = line.strip()
                fp = fingerprint(excerpt)
                self._in_tb = False
                self._tb_lines = []
                return ErrorEvent(kind="python-traceback", fp=fp, message=msg, excerpt=excerpt, ts=time.time())
            return None

        stripped = line.strip()
        if not stripped:
            return None

        # Heuristic: generic error logs / exception words on stderr.
        if _RE_GENERIC_ERROR.search(stripped) or _RE_PY_EXCEPTION_LINE.match(stripped):
            excerpt = stripped + "\n"
            fp = fingerprint(excerpt)
            return ErrorEvent(kind="stderr-line", fp=fp, message=stripped[:200], excerpt=excerpt, ts=time.time())

        return None

    def tail_text(self) -> str:
        """/**
         * @returns {string}
         */"""

        return self._tail.tail()

