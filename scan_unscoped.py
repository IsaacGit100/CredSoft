"""
Scan CredSoft for member/model queries missing an `entity` filter.

Finds every `<Model>.objects.filter(...)` call and reports the ones
that don't contain `entity=` or `entity_id=` anywhere in the call.
"""

import os
import re

PROJECT_ROOT = r"C:\credsoft"

# Don't scan these directories
EXCLUDE_DIRS = {
    "migrations",
    "__pycache__",
    "node_modules",
    ".git",
    "venv",
    "env",
    "static",
    "media",
    "logs",
    ".venv",
}

# Models that MUST be entity-scoped in any list/picker context
MODELS_TO_CHECK = [
    "Master",
    "Member",
    "Pupil",
    "Parent",
    "Staff",
    "Customer",
    "Loan",
    "Guarantor",
    "MemberContribution",
    "Role",
    "Guild",
    "Trans",
    "AccountModel",
]


def extract_call(source, open_paren_pos):
    """Return the text from the opening ( to its matching )."""
    depth = 0
    i = open_paren_pos
    while i < len(source):
        if source[i] == "(":
            depth += 1
        elif source[i] == ")":
            depth -= 1
            if depth == 0:
                # include the model and .filter too — grab ~30 chars back
                start = max(0, open_paren_pos - 30)
                return source[start : i + 1], i
        i += 1
    return source[open_paren_pos : open_paren_pos + 400], open_paren_pos


def scan_file(path):
    findings = []
    try:
        with open(path, encoding="utf-8") as f:
            source = f.read()
    except Exception:
        return findings

    for model in MODELS_TO_CHECK:
        # Match `.objects.filter(` on the model
        pattern = rf"\b{model}\.objects\.filter\s*\("
        for match in re.finditer(pattern, source):
            open_pos = match.end() - 1
            call_text, _ = extract_call(source, open_pos)

            # Does it reference entity anywhere?
            if "entity" in call_text:
                continue

            line_no = source[: match.start()].count("\n") + 1
            findings.append(
                {
                    "model": model,
                    "line_no": line_no,
                    "call": " ".join(call_text.split()),
                }
            )
    return findings


def main():
    all_findings = []

    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(root, name)
            for f in scan_file(path):
                f["path"] = path
                all_findings.append(f)

    if not all_findings:
        print("Clean — no unscoped queries found.")
        return

    print(f"Found {len(all_findings)} potential unscoped queries.\n")
    print("=" * 80)

    # group by file
    by_file = {}
    for f in all_findings:
        by_file.setdefault(f["path"], []).append(f)

    for path in sorted(by_file):
        print(f"\n{path}")
        print("-" * len(path))
        for f in sorted(by_file[path], key=lambda x: x["line_no"]):
            print(f"  line {f['line_no']:>5}  [{f['model']}]")
            print(f"      {f['call']}")

    print("\n" + "=" * 80)
    print(f"Total: {len(all_findings)}")


if __name__ == "__main__":
    main()
