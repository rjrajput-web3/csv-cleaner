# csv-cleaner

A small, dependency-free Python CLI that cleans up messy CSV files — the
kind of files data-entry freelancers get from clients every day.

## What it does

- **Trims whitespace** from every cell (leading and trailing)
- **Normalizes headers** — lowercase, spaces become underscores, punctuation removed; duplicate headers get numbered (`email`, `email_2`)
- **Drops empty rows**, including whitespace-only ones
- **Dedupes rows** — exact-match by default, or by a key column with `--dedupe`
- **Reports stats** — rows read, empty rows dropped, duplicates removed, rows written

No external packages. Python 3.8+ standard library only.

## Run it

```bash
# basic clean
python csv_cleaner.py messy.csv -o clean.csv

# dedupe by a column (e.g. keep first row per email)
python csv_cleaner.py messy.csv -o clean.csv --dedupe email

# preview what would change, without writing a file
python csv_cleaner.py messy.csv --stats-only
```

## Example

Input (`messy.csv`):

```csv
First Name,  Last Name,Email,Email
Rohit ,Rajput, rohit@example.com,rohit@example.com
  Aisha,Khan, aisha@example.com,
Rohit ,Rajput, rohit@example.com,rohit@example.com
Bob,,bob@example.com,
```

Output (`clean.csv`):

```csv
first_name,last_name,email,email_2
Rohit,Rajput,rohit@example.com,rohit@example.com
Aisha,Khan,aisha@example.com,
Bob,,bob@example.com,
```

Stats printed:

```
rows read:      5
empty dropped:  1
duplicates out: 1
rows written:   3
```

## Notes

- Input is read as UTF-8 (BOM tolerated), output written as UTF-8.
- `--dedupe` compares the key column after whitespace trimming; the first occurrence wins.
- Rows shorter than the header get padded with empty cells; extra cells are dropped.
