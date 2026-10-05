"""
Scan CredSoft for non-ASCII characters and mojibake sequences.
Pure ASCII source - no encoding issues in the scanner itself.
"""

import os
import re
import unicodedata
from collections import defaultdict

PROJECT_ROOT = r"C:\credsoft"

SKIP_DIRS = {
    "migrations",
    "__pycache__",
    ".git",
    "node_modules",
    "venv",
    "env",
    ".venv",
    "static",
    "staticfiles",
    "media",
    "logs",
    "backups",
    ".pytest_cache",
    ".mypy_cache",
}

EXTENSIONS = (".py", ".html", ".txt", ".md", ".json", ".csv")

# Mojibake codepoints that should never appear in a clean source file.
# Each one is a Unicode character that arises when UTF-8 bytes are
# misinterpreted as CP1252 / Latin-1.
MOJIBAKE_CODEPOINTS = {
    0x20AC,  # Euro sign - appears in "aEUR" mojibake
    0x201A,  # Single low-9 quotation mark
    0x0192,  # Latin small letter f with hook
    0x201E,  # Double low-9 quotation mark
    0x2026,  # Horizontal ellipsis
    0x2020,  # Dagger
    0x2021,  # Double dagger
    0x02C6,  # Modifier letter circumflex
    0x2030,  # Per mille sign
    0x0160,  # Latin capital letter S with caron
    0x2039,  # Single left-pointing angle quotation mark
    0x0152,  # Latin capital ligature OE
    0x017D,  # Latin capital letter Z with caron
    0x2018,  # Left single quotation mark
    0x2019,  # Right single quotation mark
    0x201C,  # Left double quotation mark
    0x201D,  # Right double quotation mark
    0x2022,  # Bullet
    0x2013,  # En dash
    0x2014,  # Em dash
    0x02DC,  # Small tilde
    0x2122,  # Trade mark sign
    0x0161,  # Latin small letter s with caron
    0x203A,  # Single right-pointing angle quotation mark
    0x0153,  # Latin small ligature oe
    0x017E,  # Latin small letter z with caron
    0x0178,  # Latin capital letter Y with diaeresis
    # Cyrillic chars that appear in the "Gv" mojibake we saw
    0x0413,
    0x0433,  # GH / gh
    0x0412,
    0x0432,  # V / v
    0x0402,
    0x0452,  # DJ / dj
    0x0403,
    0x0453,  # GJ / gj
    0x2019,  # also the arrow tail
}


# CJK ranges - Chinese / Japanese / Korean
def is_cjk(ch):
    cp = ord(ch)
    return (
        0x4E00 <= cp <= 0x9FFF  # CJK Unified Ideographs
        or 0x3400 <= cp <= 0x4DBF  # CJK Extension A
        or 0x3040 <= cp <= 0x30FF  # Hiragana / Katakana
        or 0xAC00 <= cp <= 0xD7AF  # Hangul syllables
        or 0xFF00 <= cp <= 0xFFEF  # Fullwidth forms
    )


# Legitimate symbols we expect and want to keep
LEGIT_SYMBOLS = {
    0x20B5,  # GHS cedi sign
    0x2713,  # check mark
    0x2717,  # ballot X
    0x2192,  # rightwards arrow
    0x2190,  # leftwards arrow
    0x2191,  # upwards arrow
    0x2193,  # downwards arrow
    0x2022,  # bullet
    0x2026,  # ellipsis
    0x00A0,  # non-breaking space
    0x00B0,  # degree
    0x00B1,  # plus-minus
    0x00D7,  # multiplication
    0x00F7,  # division
    0x2260,  # not equal
    0x2264,  # less than or equal
    0x2265,  # greater than or equal
    0x00A3,  # pound
    0x20AC,  # euro
    0x00A5,  # yen
    0x2605,  # black star
    0x2606,  # white star
    0x26A0,  # warning sign
    0x2139,  # information source
    0x00AE,  # registered
    0x2122,  # trade mark
    0x2013,  # en dash
    0x2014,  # em dash
    0x2018,
    0x2019,
    0x201C,
    0x201D,  # smart quotes
}


def classify_line(line):
    """Return (severity, kind, sample) or None."""
    sample = line.strip()[:90]

    # CJK
    for ch in line:
        if is_cjk(ch):
            return ("HIGH", "CJK", sample)

    # Any non-ASCII character we don't expect
    bad_chars = []
    for ch in line:
        cp = ord(ch)
        if cp < 128:
            continue
        if cp in LEGIT_SYMBOLS:
            continue
        bad_chars.append(ch)

    if bad_chars:
        # Build a hex summary of the bad chars
        codes = ", ".join(f"U+{ord(c):04X}" for c in bad_chars[:5])
        return ("HIGH", f"unexpected: {codes}", sample)

    # Any legit non-ASCII (informational)
    if any(ord(c) > 127 for c in line):
        return ("INFO", "legit symbol", sample)

    return None


def scan_file(path):
    findings = []
    try:
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                r = classify_line(line)
                if r:
                    findings.append((i, r[0], r[1], r[2]))
    except UnicodeDecodeError as e:
        findings.append((0, "HIGH", "not-UTF-8", str(e)[:80]))
    except Exception:
        pass
    return findings


def main():
    all_findings = defaultdict(list)

    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if not name.endswith(EXTENSIONS):
                continue
            path = os.path.join(root, name)
            rows = scan_file(path)
            if rows:
                all_findings[path] = rows

    high = medium = info = 0
    for path, rows in all_findings.items():
        for _, sev, _, _ in rows:
            if sev == "HIGH":
                high += 1
            elif sev == "MEDIUM":
                medium += 1
            else:
                info += 1

    print("=" * 78)
    print("Encoding scan complete")
    print(f"  HIGH   (fix now)       : {high}")
    print(f"  MEDIUM (review)        : {medium}")
    print(f"  INFO   (legit symbols) : {info}")
    print("=" * 78)

    print("\n### HIGH severity - files needing attention\n")
    for path in sorted(all_findings):
        rows = [r for r in all_findings[path] if r[1] == "HIGH"]
        if not rows:
            continue
        print(f"\n{path}")
        print("-" * min(len(path), 78))
        for line_no, _, kind, sample in rows[:20]:
            print(f"  line {line_no:>5}  [{kind}]")
            print(f"      {sample}")
        if len(rows) > 20:
            print(f"      ... and {len(rows) - 20} more")

    print(
        "\n\n### INFO - files with legitimate non-ASCII (cedi, check marks, arrows)\n"
    )
    for path in sorted(all_findings):
        rows = [r for r in all_findings[path] if r[1] == "INFO"]
        if rows:
            print(f"  {path}  ({len(rows)} line(s))")


if __name__ == "__main__":
    main()
