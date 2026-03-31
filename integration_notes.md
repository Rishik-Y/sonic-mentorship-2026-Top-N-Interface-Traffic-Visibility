# Integration Notes: Top-N Interface Traffic Visibility

## Files changed

- `/home/runner/work/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/cli.py`
- `/home/runner/work/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/db_connector.py`
- `/home/runner/work/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/show/__init__.py`
- `/home/runner/work/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/show/interfaces/__init__.py`
- `/home/runner/work/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/show/interfaces/counters.py`
- `/home/runner/work/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/show/interfaces/top_n.py`
- `/home/runner/work/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/tests/test_top_n.py`

## How to run tests without a SONiC device

1. Install dependencies:
   - `pip install -r /home/runner/work/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/requirements.txt`
   - `pip install pytest`
2. Run only Top-N tests:
   - `pytest /home/runner/work/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/tests/ -v -k top_n`
3. Run full local test set:
   - `pytest /home/runner/work/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/sonic-mentorship-2026-Top-N-Interface-Traffic-Visibility/tests/ -v`

The tests mock COUNTERS_DB access via monkeypatched client factories and do not require swsscommon.

## Known limitations

- Real COUNTERS_DB reads require execution in a SONiC runtime where `swsscommon` is available.
- The implementation currently supports a single namespace per command invocation via `--namespace`.
