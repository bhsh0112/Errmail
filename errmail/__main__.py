"""/**
 * @file __main__.py
 * @description Allow `python -m errmail ...`.
 */"""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())

