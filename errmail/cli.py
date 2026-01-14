"""/**
 * @file cli.py
 * @description CLI entrypoint: `errmail run -- <command...>`.
 */"""

from __future__ import annotations

import argparse
import os
import sys

from .config import load_config
from .notifier import with_overrides
from .runner import run_command


def _env_bool(name: str, default: bool = False) -> bool:
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


def _build_parser() -> argparse.ArgumentParser:
    """/**
     * @returns {argparse.ArgumentParser}
     */"""

    p = argparse.ArgumentParser(prog="errmail", add_help=True)
    sub = p.add_subparsers(dest="subcmd", required=True)

    run = sub.add_parser("run", help="run a command and email on stderr errors")
    run.add_argument("--service", default=None, help="override service name (or ERRMAIL_SERVICE)")
    run.add_argument("--cwd", default=None, help="working directory for the command")
    run.add_argument("--to", default=None, help="recipient email (override ERRMAIL_MAIL_TO)")
    run.add_argument("--cooldown-seconds", type=int, default=None, help="cooldown per fingerprint")
    run.add_argument("--tail-lines", type=int, default=None, help="stderr tail lines included in email")
    run.add_argument("--verbose", action="store_true", help="print errmail internal logs to stderr")

    return p


def _split_command_argv(argv: list[str]) -> tuple[list[str], list[str]]:
    """/**
     * @param {Array<string>} argv
     * @returns {[Array<string>, Array<string>]} (pre_args, command_args)
     */"""

    if "--" not in argv:
        return (argv, [])
    idx = argv.index("--")
    return (argv[:idx], argv[idx + 1 :])


def main(argv: list[str] | None = None) -> int:
    """/**
     * @param {?Array<string>} argv
     * @returns {number}
     */"""

    argv = list(sys.argv[1:] if argv is None else argv)
    pre, cmd = _split_command_argv(argv)

    parser = _build_parser()
    args = parser.parse_args(pre)

    if args.subcmd == "run":
        if not cmd:
            parser.error("missing command. Usage: errmail run [options] -- <command...>")

        verbose = bool(args.verbose or _env_bool("ERRMAIL_VERBOSE", False))
        cfg = load_config(service=args.service)
        cfg = with_overrides(
            cfg,
            service=args.service,
            cooldown_seconds=args.cooldown_seconds,
            tail_lines=args.tail_lines,
            mail_to=args.to,
        )

        # Important: by default we do NOT print anything. Keep output unchanged.
        # Only when verbose=1, print config warnings.
        if verbose:
            missing = []
            if not cfg.smtp_host:
                missing.append("ERRMAIL_SMTP_HOST")
            if not cfg.mail_from:
                missing.append("ERRMAIL_MAIL_FROM")
            if not cfg.mail_to:
                missing.append("ERRMAIL_MAIL_TO or --to")
            if missing:
                print(f"[errmail] email may be disabled, missing: {', '.join(missing)}", file=sys.stderr)

        return run_command(cmd, cfg=cfg, cwd=args.cwd, verbose=verbose)

    parser.error("unknown subcommand")
    return 2

