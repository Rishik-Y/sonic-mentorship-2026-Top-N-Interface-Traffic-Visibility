# Integration Notes: Top-N Interface Traffic Visibility

## Files changed

- `./cli.py`
- `./db_connector.py`
- `./show/__init__.py`
- `./show/interfaces/__init__.py`
- `./show/interfaces/counters.py`
- `./show/interfaces/top_n.py`
- `./tests/test_top_n.py`

## How to run tests without a SONiC device

1. Install dependencies:
   - `pip install -r ./requirements.txt`
   - `pip install pytest`
2. Run only Top-N tests:
   - `pytest ./tests/ -v -k top_n`
3. Run full local test set:
   - `pytest ./tests/ -v`

The tests mock COUNTERS_DB access via monkeypatched client factories and do not require swsscommon.

## Known limitations

- Real COUNTERS_DB reads require execution in a SONiC runtime where `swsscommon` is available.
- The implementation currently supports a single namespace per command invocation via `--namespace`.
