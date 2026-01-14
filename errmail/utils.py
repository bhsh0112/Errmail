"""/**
 * @file utils.py
 * @description Small helpers (ring buffer, fingerprint normalization).
 */"""

from __future__ import annotations

from collections import deque
import hashlib
import re
from typing import Deque, Iterable


class RingBuffer:
    """/**
     * @class RingBuffer
     * @description Keep last N lines for email context.
     *
     * @param {number} max_lines
     */"""

    def __init__(self, max_lines: int) -> None:
        self._buf: Deque[str] = deque(maxlen=max_lines)

    def push(self, line: str) -> None:
        """/**
         * @param {string} line
         */"""

        self._buf.append(line)

    def extend(self, lines: Iterable[str]) -> None:
        """/**
         * @param {Iterable<string>} lines
         */"""

        for ln in lines:
            self._buf.append(ln)

    def tail(self) -> str:
        """/**
         * @returns {string}
         */"""

        return "".join(self._buf)


_RE_HEX_ADDR = re.compile(r"0x[0-9a-fA-F]+")
_RE_LINE_NO = re.compile(r"\bline\s+\d+\b")
_RE_INT = re.compile(r"\b\d+\b")


def normalize_for_fingerprint(text: str) -> str:
    """/**
     * @param {string} text
     * @returns {string}
     */"""

    s = text.strip()
    s = _RE_HEX_ADDR.sub("0x?", s)
    s = _RE_LINE_NO.sub("line ?", s)
    # Avoid over-normalizing: only replace stand-alone integers (counts/ports/etc.)
    s = _RE_INT.sub("?", s)
    return s


def fingerprint(text: str) -> str:
    """/**
     * @param {string} text
     * @returns {string} short fingerprint
     */"""

    norm = normalize_for_fingerprint(text).encode("utf-8", errors="replace")
    return hashlib.sha1(norm).hexdigest()[:12]

