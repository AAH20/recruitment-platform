# Independent Audit — recruitment-platform

**Auditor:** orchestrator subagent (adversarial verification pass)
**Date:** 2026-10-11
**Scope:** dependency, security, Python-version, test-integrity, dead/duplicate code.
**Method:** every claim below is backed by an exact command and its raw output tail.
Environment: repo venv `.venv/bin/python` = **Python 3.12.14**; system `python3` = **Python 3.9.6**.

---

## 1. Dependency audit

```text
$ ./.venv/bin/pip list --outdated 2>&1 | head -20
[exit=0]                # <- no packages listed
```
**Outdated packages: 0.** Network was confirmed live (`curl https://pypi.org/simple/click/` → `http_code=200`; `pip download click` → "Successfully downloaded"), so the empty result is genuine, not a network artifact.

Dependency files are **fully unbounded (`>=` with no upper cap)** in both `requirements.txt` and `pyproject.toml` — e.g. `fastapi>=0.115.0`, `sqlalchemy>=2.0.0`, `pytest>=8.0.0`. No `>=0.0` wildcards, but no upper bounds anywhere.

**Divergence between the two dependency sources of truth:** `pyproject.toml` declares `urllib3>=2.5.0` and `requests>=2.32.0` (and `click>=8.3.3`, `certifi>=2024.7.4`, `anyio>=4.14.2`) that are **absent from `requirements.txt`**; `requirements.txt` lists `psutil`, `bleach`, `aiosqlite` that are absent from `pyproject.toml`. Installed venv has neither `urllib3` nor `requests` (they are pyproject-only). A fresh `pip install -r requirements.txt` and a fresh `pip install -e .` therefore produce different environments.

## 2. Security scan

`bandit` is **not installed** in this venv (`./.venv/bin/python -m bandit` → `No module named bandit`) though `requirements-dev.txt` lists it. Ran the analyzer from the gated-communities venv (bandit 1.9.4) against this repo's source:

```text
$ gated-communities/.venv/bin/python -m bandit -r recruitment-platform/src -ll
Run metrics:
        Total issues (by severity):
                Low: 117
                Medium: 1
                High: 0
```
**MEDIUM+ findings: 1.**
```
Issue: [B104:hardcoded_bind_all_interfaces] Severity: Medium
Location: src/recruitment_platform/config/settings.py:24:30
24   host: str = Field(default="0.0.0.0")
```
LOW count 117 (test/assert noise). **Verified defect**: default bind to `0.0.0.0`.

## 3. Python-version compatibility

- Declared: `pyproject.toml` → `requires-python = ">=3.10"`.
- CI: `.github/workflows/ci.yml` uses `python-version: ["3.12"]` only (plus 3.12 in lint/codeql/frontend jobs).
- Grammar check: compiled **all 193 src files with the system Python 3.9.6** → **0 syntax errors**. No PEP-634 `match`, no PEP-695 (3.12) generics, no `except*`, no `typing.Self`. `X | None` unions are used but are valid on the declared 3.10 floor.
- **No declared-vs-syntax mismatch.** The real gap is procedural: the declared minimum (3.10) is **never exercised in CI** (matrix is 3.12 only), so a 3.10 regression could ship undetected.

**Verdict: no version/syntax defect; CI does not test the declared minimum (suspicion → low severity).**

## 4. Test-suite integrity

Plain invocation **fails at collection** — the suite cannot even start in the provided venv:
```
$ .venv/bin/python -m pytest tests -q --no-header
ImportError while loading conftest 'tests/conftest.py'.
tests/conftest.py:27: in <module>
    from recruitment_platform.main import app
E   ModuleNotFoundError: No module named 'recruitment_platform'
```
Root cause: package not installed in the venv, and `pyproject.toml` `[tool.pytest.ini_options]` has **no `pythonpath`** setting. CI masks this by running `pip install -e ".[dev]"` first (ci.yml:91). Mirroring CI's editable install with `PYTHONPATH=src`:

```
$ PYTHONPATH=src .venv/bin/python -m pytest tests -q --no-header
18 failed, 238 passed, 30 warnings in 49.47s
```
**REAL tail line: `18 failed, 238 passed`.**

The 18 failures are **order-dependent (non-hermetic)**. The exact tests that fail in the full run **pass in isolation**:
```
$ PYTHONPATH=src .venv/bin/python -m pytest \
    tests/test_api/test_export_routes.py::TestExportRoutes::test_doubled_prefix_path_is_not_registered \
    tests/test_api/test_search_routes.py::TestSearchRoutes::test_search_jobs -q
2 passed, 4 warnings in 0.52s
```
Failing group: `test_api/test_export_routes.py`, `test_api/test_search_routes.py`, `test_api/test_notifications_routes.py`, `test_api/test_assessments.py` — repeatedly `test_doubled_prefix_path_is_not_registered` and route tests. **Verified defect: shared mutable app/DB state leaks across tests → suite result depends on collection order.**

No test-deletion/quarantine directories exist in this repo.

## 5. Dead / duplicate code signal

**Missing module breaks three model files (verified):**
```
$ grep -rn "from recruitment_platform.models.base import Base" src
models/interview.py:11:   from recruitment_platform.models.base import Base
models/job.py:12:         from recruitment_platform.models.base import Base
models/application.py:13: from recruitment_platform.models.base import Base
$ ls src/recruitment_platform/models/base.py
ls: .../models/base.py: No such file or directory
```
`import`-scan of every module → these fail with `ModuleNotFoundError: No module named 'recruitment_platform.models.base'`.

**Duplicate `candidates` table (verified):**
```
models/__init__.py:40:    __tablename__ = "candidates"     # class Candidate(Base) @ line 37
models/candidate.py:19:   __tablename__ = "candidates"     # class Candidate(Base) @ line 16
```
Importing both → `InvalidRequestError: Table 'candidates' is already defined for this MetaData instance`.

Full import scan also flags (env-related, not repo defects): `extensions` (greenlet missing), `middleware.rate_limit` (redis missing), `tasks.celery_tasks` (celery missing).

**Largest source files vs test coverage** (grep of module name across `tests/`):
| file | lines | tests refs | import refs |
|---|---|---|---|
| agents/talent_pool_manager.py | 1646 | 2 | 0 |
| agents/employer_branding.py | 976 | 2 | 0 |
| agents/candidate_matcher.py | 739 | 2 | 0 |
| agents/resume_parser.py | 685 | 2 | 0 |
| agents/bias_detector.py | 671 | 2 | 0 |
The five biggest modules have **no test that imports them** (2 fuzzy name hits each). ~4,700 lines with effectively zero behavioural coverage.

---

## Top 3 REAL issues (ranked)

1. **[VERIFIED DEFECT — HIGH] Broken model layer.** `models/base.py` is missing (imported by `job.py`, `interview.py`, `application.py` → 3 unimportable modules) **and** the `candidates` table is defined twice (`models/__init__.py:40`, `models/candidate.py:19`) → `InvalidRequestError`. The ORM layer cannot be imported cleanly.
2. **[VERIFIED DEFECT — MEDIUM] Non-hermetic test suite.** 18 tests fail in the full run yet pass in isolation (shared state leakage); suite also cannot start without an editable install / `PYTHONPATH=src`.
3. **[VERIFIED DEFECT — LOW/MEDIUM] Security & supply-chain hygiene.** bandit MEDIUM B104 default-bind `0.0.0.0`; every dependency unbounded (`>=` only); `pyproject.toml` and `requirements.txt` disagree on the dependency set.

### Minimal, verifiable fix (one per repo) — `docs/AUDIT-orchestrator.patch`
Adds the missing `src/recruitment_platform/models/base.py` (the highest-severity unblocker).
```text
$ git -C recruitment-platform apply --check docs/AUDIT-orchestrator.patch
[exit=0]     # patch is well-formed and applies cleanly
```
> NOTE: this is a **patch artifact only** — no `src/**` file was modified by this audit (out of scope). A source-owning agent should `git apply docs/AUDIT-orchestrator.patch`, then de-duplicate the `Candidate` model in `models/candidate.py` vs `models/__init__.py`.
