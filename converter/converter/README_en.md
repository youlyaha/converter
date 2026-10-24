# 🔢 Number Base Converter

[🇷🇺 Русский](README.md) · 🇬🇧 English

## Overview
A Python/Tkinter application that converts integers from decimal to bases 2–16. It supports GUI or TXT input, saving results, backup and restore of the internal JSON mapping table, and event logging.

## Features
- Convert positive and negative integers and zero.
- Bases 2–16, using `A–F` for digit values above 9.
- Load input and save results as TXT.
- Create and restore JSON mapping backups.
- Write events to `logs/app.log` using the separate `logger.py` module.
- GUI and optional console mode.

## Requirements
Python 3.10+. Only Python standard-library modules are used; no third-party runtime dependencies are required.

## Run
```bash
python converter_tkinter.py
```
Console mode:
```bash
python converter_tkinter.py --console
```

## Usage
Enter a decimal integer, select a base from 2 to 16, and click Convert. A TXT input may contain a number and an optional base, for example `255 16`.

## Backup and restore
The Create Backup button copies `data/encoding_mapping.json` into `backups/`. To restore, select a JSON backup and confirm replacement. The file must contain a valid JSON object. This is an application mapping table, not a Windows system code-page table.

## Logging
`logs/app.log` is created automatically. Startup/shutdown, conversions, errors, file operations, and backup actions are logged.

## Tests
```bash
python -m unittest discover -s tests -v
```
See [test cases](docs/test-cases.md), [technical specification](docs/TZ.md), [maintenance procedure](docs/maintenance.md), and [Git workflow](docs/GIT.md).

## Author
Educational project. Add author and supervisor details if required.
