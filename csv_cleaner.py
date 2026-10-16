#!/usr/bin/env python3
"""
csv_cleaner — clean up messy CSV files for data-entry freelancers.

What it does:
  * trims leading/trailing whitespace from every cell
  * normalizes headers -> lowercase, spaces become underscores,
    duplicates get numbered (email, email_2)
  * drops fully-empty rows (including whitespace-only ones)
  * dedupes rows: exact-match by default, or by a key column
  * prints a stats report so you can see exactly what changed

No external dependencies — Python 3.8+ standard library only.

Examples:
    python csv_cleaner.py messy.csv -o clean.csv
    python csv_cleaner.py messy.csv -o clean.csv --dedupe email
    python csv_cleaner.py messy.csv --stats-only
"""

import argparse
import csv
import re
import sys


def normalize_header(name):
    """'  First Name ' -> 'first_name'; strips punctuation, keeps a-z0-9_."""
    name = name.strip().lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-z0-9_]", "", name)
    return name or "col"


def unique_headers(headers):
    """Normalize headers and number duplicates: email, email_2."""
    seen = {}
    out = []
    for raw in headers:
        h = normalize_header(raw)
        if h in seen:
            seen[h] += 1
            out.append(f"{h}_{seen[h]}")
        else:
            seen[h] = 1
            out.append(h)
    return out


def clean(path_in, path_out=None, dedupe_col=None, stats_only=False):
    """Returns 0 on success, 1 on error."""
    stats = {"rows_read": 0, "empty_dropped": 0,
             "dupes_removed": 0, "rows_written": 0}

    try:
        f = open(path_in, newline="", encoding="utf-8-sig")
    except OSError as exc:
        print(f"Error: cannot read '{path_in}': {exc}", file=sys.stderr)
        return 1

    with f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            print(f"Error: '{path_in}' is empty.", file=sys.stderr)
            return 1
        headers = unique_headers(headers)

        if dedupe_col and dedupe_col not in headers:
            print(f"Error: column '{dedupe_col}' not found. "
                  f"Columns: {', '.join(headers)}", file=sys.stderr)
            return 1

        seen = set()
        rows = []
        for raw_row in reader:
            stats["rows_read"] += 1
            row = [cell.strip() for cell in raw_row]
            # pad short rows / trim long rows to header width
            if len(row) < len(headers):
                row += [""] * (len(headers) - len(row))
            row = row[:len(headers)]

            if all(cell == "" for cell in row):
                stats["empty_dropped"] += 1
                continue

            ident = tuple(row) if dedupe_col is None \
                else (row[headers.index(dedupe_col)],)
            if ident in seen:
                stats["dupes_removed"] += 1
                continue
            seen.add(ident)
            rows.append(row)

    if not stats_only:
        if path_out is None:
            print("Error: specify -o/--output, or use --stats-only.",
                  file=sys.stderr)
            return 1
        try:
            with open(path_out, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
        except OSError as exc:
            print(f"Error: cannot write '{path_out}': {exc}", file=sys.stderr)
            return 1
        stats["rows_written"] = len(rows)

    print(f"rows read:      {stats['rows_read']}")
    print(f"empty dropped:  {stats['empty_dropped']}")
    print(f"duplicates out: {stats['dupes_removed']}")
    print(f"rows written:   {stats['rows_written']}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Clean messy CSV files: trim whitespace, normalize "
                    "headers, drop empty rows, dedupe.")
    parser.add_argument("input", help="input CSV file")
    parser.add_argument("-o", "--output", help="output CSV file "
                        "(required unless --stats-only)")
    parser.add_argument("--dedupe", metavar="COLUMN",
                        help="dedupe by this column (after header "
                        "normalization); default: exact-row dedupe")
    parser.add_argument("--stats-only", action="store_true",
                        help="print stats without writing a file")
    args = parser.parse_args(argv)
    return clean(args.input, args.output, args.dedupe, args.stats_only)


if __name__ == "__main__":
    sys.exit(main())
