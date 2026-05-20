"""Marketing Pipeline — Helper Script

Provides CLI commands for managing the marketing pipeline workflow:

Commands:
    init      — Create output directory structure for a project slug
    validate  — Validate phase outputs (brief, design, landing)
    summary   — Print asset summary for a project

Usage:
    python pipeline.py init <project-slug> [--output-dir <path>]
    python pipeline.py validate <phase> <path>
    python pipeline.py summary <project-slug> [--output-dir <path>]

Phases:
    brief    — Validates brand-brief.md has product_name, description, audience
    design   — Validates design-system.md has colors, typography, spacing
    landing  — Validates HTML is well-formed and free of banned AI-slop patterns
"""

import argparse
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Templates directory (relative to this script's location)
# ---------------------------------------------------------------------------
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


# ---------------------------------------------------------------------------
# Banned landing-page patterns (AI slop detection)
# ---------------------------------------------------------------------------
BANNED_PATTERNS: list[tuple[str, str]] = [
    (
        "purple-to-pink-gradient",
        r"""linear-gradient\([^)]*?(purple|pink|violet)[^)]*?(purple|pink|violet)[^)]*?\)""",
    ),
    (
        "generic-sans-font-family",
        r"""font-family\s*:[^;]*?(Inter|Roboto|Arial)[^;]*;""",
    ),
    (
        "emoji-as-icon-prefix",
        r"""["'\u2018-\u2019]?[\U0001F300-\U0001FAF6\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF]{1,3}\s*["'\u2018-\u2019]?</?(?:h[1-6]|p|div|span|strong|b)\b""",
    ),
    (
        "gradient-button-large-card-combo",
        r"""(?=[\s\S]*(?:btn|button)[^>]*?(?:gradient|rounded[\s-]))(?=[\s\S]*(?:border-radius|rounded)[:\s]+[1-9][0-9]*(?:px|rem|em)).*""",
    ),
]


def _is_valid_slug(slug: str) -> bool:
    """Return True if *slug* is lowercase alphanumeric with optional hyphens."""
    return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug))


def _resolve_path(slug: str, output_dir: str | None) -> Path:
    """Resolve the project directory for *slug* under *output_dir*.

    If *output_dir* is None, the current working directory is used.
    """
    base = Path(output_dir).resolve() if output_dir else Path.cwd().resolve()
    return base / "marketing-output" / slug


# ==============================  INIT  ==================================


def cmd_init(slug: str, output_dir: str | None) -> int:
    """Create the output directory structure for *slug*.

    Creates::

        marketing-output/<slug>/
        ├── brand-brief.md    (from template or empty)
        ├── design-system.md  (empty)
        ├── prompts/
        └── video/

    Returns 0 on success, 1 on error.
    """
    if not _is_valid_slug(slug):
        print(f"Error: Invalid project slug {slug!r}.", file=sys.stderr)
        print("  Use lowercase letters, digits, and hyphens only (e.g. 'my-project').")
        return 1

    base = _resolve_path(slug, output_dir)

    try:
        base.mkdir(parents=True, exist_ok=True)
        (base / "prompts").mkdir(exist_ok=True)
        (base / "video").mkdir(exist_ok=True)

        # brand-brief.md
        brief_path = base / "brand-brief.md"
        if not brief_path.exists():
            template = TEMPLATES_DIR / "brand-brief-template.md"
            if template.exists():
                brief_path.write_text(template.read_text(encoding="utf-8"))
                print(f"  Created {brief_path} (from template)")
            else:
                brief_path.write_text("")
                print(f"  Created {brief_path} (empty — no template found)")

        # design-system.md
        design_path = base / "design-system.md"
        if not design_path.exists():
            design_path.write_text("")
            print(f"  Created {design_path} (empty)")

        print(f"  Created {base / 'prompts'}/")
        print(f"  Created {base / 'video'}/")
        print(f"  Project root: {base}")

    except OSError as e:
        print(f"Error creating directory structure: {e}", file=sys.stderr)
        return 1

    return 0


# ============================  VALIDATE  ================================


def _pass(msg: str) -> None:
    """Print a PASS message to stdout."""
    print(f"  PASS: {msg}")


def _fail(msg: str) -> None:
    """Print a FAIL message to stderr."""
    print(f"  FAIL: {msg}", file=sys.stderr)


def validate_brief(path: Path) -> int:
    """Validate a brand-brief.md file.

    Checks that the file exists and contains the sections:
      - product_name (or product name)
      - description
      - audience

    Returns 0 if all pass, 1 if any fail.
    """
    if not path.is_file():
        _fail(f"File not found: {path}")
        return 1

    text = path.read_text(encoding="utf-8")

    checks = {
        "product_name": r"product[ _]?name",
        "description": r"description",
        "audience": r"audience",
    }

    failed = 0
    for label, regex in checks.items():
        if re.search(regex, text, re.IGNORECASE):
            _pass(f"brief contains '{label}' section")
        else:
            _fail(f"brief missing '{label}' section")
            failed += 1

    return 0 if failed == 0 else 1


def validate_design(path: Path) -> int:
    """Validate a design-system.md file.

    Checks that the file exists and contains the sections:
      - colors (or color)
      - typography
      - spacing

    Returns 0 if all pass, 1 if any fail.
    """
    if not path.is_file():
        _fail(f"File not found: {path}")
        return 1

    text = path.read_text(encoding="utf-8")

    checks = {
        "colors": r"colou?rs?",
        "typography": r"typography",
        "spacing": r"spacing",
    }

    failed = 0
    for label, regex in checks.items():
        if re.search(regex, text, re.IGNORECASE):
            _pass(f"design-system contains '{label}' section")
        else:
            _fail(f"design-system missing '{label}' section")
            failed += 1

    return 0 if failed == 0 else 1


def validate_landing(path: Path) -> int:
    """Validate a landing page HTML file.

    Checks:
      - DOCTYPE declaration present
      - <html> tag present
      - <head> tag present
      - <body> tag present
      - No banned AI-slop patterns (gradients, generic fonts, emoji icons, etc.)

    Returns 0 if all pass, 1 if any fail.
    """
    if not path.is_file():
        _fail(f"File not found: {path}")
        return 1

    text = path.read_text(encoding="utf-8")
    failed = 0

    # --- Structural checks ---
    structure_checks = {
        "doctype": r"<!DOCTYPE\s+html",
        "html_tag": r"<html[\s>]",
        "head_tag": r"<head[\s>]",
        "body_tag": r"<body[\s>]",
    }

    for label, regex in structure_checks.items():
        if re.search(regex, text, re.IGNORECASE):
            _pass(f"landing has {label}")
        else:
            _fail(f"landing missing {label}")
            failed += 1

    # --- Banned pattern checks ---
    for name, regex in BANNED_PATTERNS:
        if re.search(regex, text, re.IGNORECASE | re.DOTALL):
            _fail(f"landing contains banned pattern: {name}")
            failed += 1
        else:
            _pass(f"landing clear of banned pattern: {name}")

    return 0 if failed == 0 else 1


VALIDATORS = {
    "brief": validate_brief,
    "design": validate_design,
    "landing": validate_landing,
}


def cmd_validate(phase: str, path_str: str) -> int:
    """Validate a pipeline output for the given *phase*.

    Dispatches to the appropriate phase-specific validator.
    Returns 0 on pass, 1 on failure.
    """
    normalised = phase.lower().strip()
    if normalised not in VALIDATORS:
        valid = ", ".join(VALIDATORS)
        print(f"Error: Unknown phase {phase!r}. Valid phases: {valid}", file=sys.stderr)
        return 1

    p = Path(path_str).resolve()
    print(f"Validating phase '{normalised}' — {p}")
    return VALIDATORS[normalised](p)


# ============================  SUMMARY  ================================


def _file_info(fp: Path, base: Path) -> tuple[int, int, str]:
    """Return (size_bytes, line_count, relative_path_str) for *fp*."""
    size = fp.stat().st_size
    lines = len(fp.read_text(encoding="utf-8").splitlines())
    rel = str(fp.relative_to(base))
    return size, lines, rel


def cmd_summary(slug: str, output_dir: str | None) -> int:
    """Print a summary of generated assets for *slug*.

    Reports file sizes, line counts, and phase completion status
    (brief, design, landing).

    Returns 0 on success, 1 if the project directory doesn't exist.
    """
    if not _is_valid_slug(slug):
        print(f"Error: Invalid project slug {slug!r}.", file=sys.stderr)
        return 1

    base = _resolve_path(slug, output_dir)
    if not base.is_dir():
        print(f"Error: Project directory not found: {base}", file=sys.stderr)
        print("  Run 'pipeline.py init' first.")
        return 1

    print(f"Summary for project: {slug}")
    print(f"  Project root: {base}")
    print()

    # --- Gather all files ---
    all_files = sorted(base.rglob("*"))
    files_only = [f for f in all_files if f.is_file()]

    if not files_only:
        print("  No generated assets found.")
        return 0

    print("  Generated Assets:")
    for fp in files_only:
        try:
            size, lines, rel = _file_info(fp, base)
            print(f"    {rel}  —  {size} bytes, {lines} lines")
        except Exception as e:
            rel = str(fp.relative_to(base))
            print(f"    {rel}  —  error: {e}")

    print()

    # --- Phase completion ---
    print("  Phase Readiness:")

    # Brief
    brief_path = base / "brand-brief.md"
    if brief_path.is_file():
        ok = validate_brief(brief_path)
        status = "READY" if ok == 0 else "INCOMPLETE"
    else:
        status = "MISSING"
    print(f"    brief          [{status}]")

    # Design
    design_path = base / "design-system.md"
    if design_path.is_file():
        ok = validate_design(design_path)
        status = "READY" if ok == 0 else "INCOMPLETE"
    else:
        status = "MISSING"
    print(f"    design         [{status}]")

    # Landing — look for HTML files
    html_files = sorted(base.rglob("*.html"))
    if html_files:
        all_ok = True
        for hf in html_files:
            if validate_landing(hf) != 0:
                all_ok = False
        status = "READY" if all_ok else "ISSUES"
        print(f"    landing        [{status}]  ({len(html_files)} file(s))")
    else:
        print(f"    landing        [MISSING]  (no .html files found)")

    return 0


# ============================  CLI  ====================================


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments and return the namespace."""
    parser = argparse.ArgumentParser(
        description="Marketing Pipeline Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # init
    init_p = sub.add_parser("init", help="Create output directory structure")
    init_p.add_argument("project_slug", help="Project slug (e.g. 'my-app')")
    init_p.add_argument(
        "--output-dir",
        default=None,
        help="Base output directory (default: current working directory)",
    )

    # validate
    val_p = sub.add_parser("validate", help="Validate a phase output")
    val_p.add_argument(
        "phase",
        choices=list(VALIDATORS),
        help="Phase to validate",
    )
    val_p.add_argument("path", help="Path to the file to validate")

    # summary
    sum_p = sub.add_parser("summary", help="Print summary of generated assets")
    sum_p.add_argument("project_slug", help="Project slug")
    sum_p.add_argument(
        "--output-dir",
        default=None,
        help="Base output directory (default: current working directory)",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point. Parses args and dispatches to the correct command.

    Returns the exit code (0 for success, 1 for error).
    """
    args = parse_args(argv)

    if args.command == "init":
        return cmd_init(args.project_slug, args.output_dir)
    elif args.command == "validate":
        return cmd_validate(args.phase, args.path)
    elif args.command == "summary":
        return cmd_summary(args.project_slug, args.output_dir)
    else:
        # argparse enforces subcommands, so this shouldn't happen
        print(f"Error: Unknown command {args.command!r}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
