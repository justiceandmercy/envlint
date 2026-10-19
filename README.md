# envlint

Lint `.env` files for common mistakes: duplicate keys, invalid names, empty values,
unterminated quotes, trailing whitespace, BOMs, and values that look like secrets.

## Features

- Zero dependencies (Python standard library only)
- Detects duplicate keys and reports the first occurrence
- Validates variable names against the POSIX-ish `[A-Za-z_][A-Za-z0-9_]*` pattern
- Warns on empty values, trailing whitespace, and BOM-prefixed files
- Flags values that look like API tokens or private keys
- `--strict` mode to fail on warnings
- Works on single files, directories (recursively finds `.env*`), or many paths at once

## Install

No installation required beyond Python 3.9+.

```sh
git clone https://github.com/example/envlint.git
cd envlint
python -m envlint --version
```

Or copy the `envlint/` package anywhere on your `PYTHONPATH`.

## Usage

Lint a default `.env` file:

```sh
python -m envlint
```

Lint specific files:

```sh
python -m envlint .env .env.local .env.example
```

Lint a directory (finds every `.env*` file recursively):

```sh
python -m envlint ./config
```

Fail on warnings too:

```sh
python -m envlint --strict
```

Example output:

```
.env:
  line 3: [error] E003 duplicate key 'DATABASE_URL' (first on line 1)
  line 5: [warning] W001 EMPTY has an empty value
  line 7: [info] I001 key 'debug' is not uppercase

3 issue(s) found.
```

## Exit codes

- `0` — no errors (and no warnings in `--strict` mode)
- `1` — errors found (or warnings in `--strict` mode)

## License

MIT