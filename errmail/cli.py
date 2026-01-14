"""/**
 * @file cli.py
 * @description CLI entrypoint:
 * - `errmail init` generate config template
 * - `errmail test` send a test email
 * - `errmail run -- <command...>` run command and alert on errors
 */"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from .config import load_config
from .notifier import with_overrides
from .mailer import MailPayload, build_subject, send_mail
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

    init = sub.add_parser("init", help="generate an env config template")
    init.add_argument(
        "--path",
        default=str(Path.home() / ".errmail.env"),
        help="where to write the config template (default: ~/.errmail.env)",
    )
    init.add_argument(
        "--provider",
        default="custom",
        choices=["custom", "gmail", "outlook", "qq", "163", "126"],
        help="preset common SMTP settings for the provider",
    )
    init.add_argument("--force", action="store_true", help="overwrite existing file")
    init.add_argument("--print", dest="do_print", action="store_true", help="print template to stdout (no write)")

    test = sub.add_parser("test", help="send a test email using current config")
    test.add_argument("--service", default=None, help="override service name (or ERRMAIL_SERVICE)")
    test.add_argument("--to", default=None, help="recipient email (override ERRMAIL_MAIL_TO)")
    test.add_argument("--verbose", action="store_true", help="print errmail internal logs to stderr")

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

    if args.subcmd == "init":
        presets = {
            "custom": {
                "host": "smtp.example.com",
                "port": "587",
                "tls": "1",
                "ssl": "0",
                "user": "your_email@example.com",
            },
            "gmail": {
                "host": "smtp.gmail.com",
                "port": "587",
                "tls": "1",
                "ssl": "0",
                "user": "your_account@gmail.com",
            },
            "outlook": {
                "host": "smtp.office365.com",
                "port": "587",
                "tls": "1",
                "ssl": "0",
                "user": "your_account@outlook.com",
            },
            # QQ/163/126 often use 465 implicit SSL in many regions/accounts.
            "qq": {
                "host": "smtp.qq.com",
                "port": "465",
                "tls": "0",
                "ssl": "1",
                "user": "your_account@qq.com",
            },
            "163": {
                "host": "smtp.163.com",
                "port": "465",
                "tls": "0",
                "ssl": "1",
                "user": "your_account@163.com",
            },
            "126": {
                "host": "smtp.126.com",
                "port": "465",
                "tls": "0",
                "ssl": "1",
                "user": "your_account@126.com",
            },
        }
        preset = presets.get(str(args.provider), presets["custom"])
        template = "\n".join(
            [
                "# errmail config template (KEY=VALUE)",
                "# You can place this at /etc/errmail.env (system-wide) or ~/.errmail.env (per-user).",
                "# Or point ERRMAIL_CONFIG_FILE to a custom path.",
                "# SECURITY: never share this file with others. It contains your SMTP credential.",
                "",
                "# SMTP server settings",
                f"ERRMAIL_SMTP_HOST={preset['host']}",
                f"ERRMAIL_SMTP_PORT={preset['port']}",
                f"ERRMAIL_SMTP_TLS={preset['tls']}",
                f"ERRMAIL_SMTP_SSL={preset['ssl']}",
                f"ERRMAIL_SMTP_USER={preset['user']}",
                "ERRMAIL_SMTP_PASS=YOUR_APP_PASSWORD_OR_AUTH_CODE",
                "",
                "# Mail settings",
                f"ERRMAIL_MAIL_FROM={preset['user']}",
                "# End users can set ERRMAIL_MAIL_TO themselves or pass --to",
                "# ERRMAIL_MAIL_TO=user@example.com",
                "",
                "# Optional",
                "ERRMAIL_COOLDOWN_SECONDS=300",
                "ERRMAIL_TAIL_LINES=200",
                "ERRMAIL_SERVICE=unknown-service",
                "",
            ]
        )

        if args.do_print:
            sys.stdout.write(template)
            return 0

        path = Path(str(args.path)).expanduser()
        if path.exists() and not args.force:
            print(f"[errmail] {path} already exists. Use --force to overwrite.", file=sys.stderr)
            return 2
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(template, encoding="utf-8")
            print(f"[errmail] wrote template to {path}", file=sys.stderr)
            return 0
        except Exception as e:  # noqa: BLE001
            print(f"[errmail] failed to write {path}: {type(e).__name__}: {e}", file=sys.stderr)
            return 1

    if args.subcmd == "test":
        verbose = bool(args.verbose or _env_bool("ERRMAIL_VERBOSE", False))
        cfg = load_config(service=args.service)
        cfg = with_overrides(cfg, service=args.service, mail_to=args.to)

        subject = build_subject(cfg.service, "test", "manual")
        body = "This is a test email from errmail.\nIf you received it, SMTP config works.\n"
        err = send_mail(cfg, MailPayload(subject=subject, body=body))
        if err:
            if verbose:
                print(f"[errmail] test send failed: {err}", file=sys.stderr)
            return 1
        if verbose:
            print("[errmail] test email sent.", file=sys.stderr)
        return 0

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

