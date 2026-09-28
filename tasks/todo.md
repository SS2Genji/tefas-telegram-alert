# Tasks: tefas-telegram-alert

## Task 1: Core TEFAS Fetcher & Alert Engine
**Description:** Implement `tefas_alert.py` using pure Python 3 standard library. Fetches latest fund prices from official TEFAS JSON API, calculates day-over-day return and percentage change, formats an HTML Telegram notification, and dispatches it via Telegram Bot API or prints to stdout in dry-run mode.

**Acceptance criteria:**
- [x] Pure Python 3 standard library only (no pip dependencies).
- [x] Fetches at least the last 2 trading sessions from TEFAS JSON API (`https://www.tefas.gov.tr/api/funds/fonGnlBlgSiraliGetir`).
- [x] Accurately computes price difference and percentage return.
- [x] Distinguishes positive (+), negative (-), and neutral (0.00%) return states.
- [x] Supports configuration via environment variables: `FUND_CODE`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `ALERT_NEGATIVE_ONLY`, `DRY_RUN`.
- [x] Multi-fund support via comma-separated `FUND_CODE` (e.g. `KTV,TI1`).

**Verification:**
- [x] Run `FUND_CODE=KTV DRY_RUN=true python3 tefas_alert.py` and verify correct price and return output.

**Dependencies:** None
**Files likely touched:** `tefas_alert.py`
**Estimated scope:** S (1 file)

---

## Task 2: Unit & Integration Tests
**Description:** Implement `test_alert.py` using Python's standard `unittest` framework to verify return calculations, message formatting, threshold filtering, and mock API handling.

**Acceptance criteria:**
- [x] Tests positive return formatting (`🟢`).
- [x] Tests negative return formatting (`🚨 DİKKAT`).
- [x] Tests neutral/zero return formatting.
- [x] Tests `ALERT_NEGATIVE_ONLY` filter logic.
- [x] Tests multi-fund parsing.

**Verification:**
- [x] `python3 test_alert.py` passes with 0 failures.

**Dependencies:** Task 1
**Files likely touched:** `test_alert.py`
**Estimated scope:** S (1 file)

---

## Checkpoint: Core Engine
- [x] All tests in `test_alert.py` pass.
- [x] Live TEFAS fetch in dry-run mode displays accurate KTV price and return.

---

## Task 3: GitHub Actions Workflow
**Description:** Create `.github/workflows/daily_alert.yml` to run the alert script on a scheduled cron during business mornings, with workflow_dispatch manual trigger and secret injection.

**Acceptance criteria:**
- [x] Cron schedule set to `15 6 * * 1-5` (06:15 UTC -> 09:15 TSI, Monday-Friday).
- [x] `workflow_dispatch` enabled for manual runs from GitHub UI.
- [x] Injects `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `FUND_CODE`, and `ALERT_NEGATIVE_ONLY` from GitHub Secrets / Variables.
- [x] Uses standard Ubuntu runner with system Python 3 (no pip installation steps needed).

**Verification:**
- [x] Lint/validate YAML syntax.

**Dependencies:** Task 1
**Files likely touched:** `.github/workflows/daily_alert.yml`
**Estimated scope:** S (1 file)

---

## Task 4: Comprehensive Open-Source README
**Description:** Write a production-quality, open-source `README.md` following the project's established standards (clean headings, zero badges/decorative HTML wrappers). Includes step-by-step instructions for creating a Telegram bot, finding Chat ID, setting GitHub Secrets, configuring funds, and local testing.

**Acceptance criteria:**
- [x] Clear overview and features.
- [x] Step 1: Telegram Bot setup with `@BotFather`.
- [x] Step 2: Finding Chat ID with `@userinfobot`.
- [x] Step 3: GitHub Repository setup (Fork & Secrets).
- [x] Step 4: Configuration reference table (Environment variables).
- [x] Step 5: Local execution & Dry Run guide.
- [x] Technical architecture & FAQ (market clearing hours, weekend handling).

**Verification:**
- [x] Markdown renders cleanly with verified links and instructions.

**Dependencies:** Task 1, Task 3
**Files likely touched:** `README.md`
**Estimated scope:** S (1 file)

---

## Task 5: Repository Initialization
**Description:** Initialize git repository, configure `.gitignore` (ignoring `.env`, `__pycache__`, etc.), and create initial git commit.

**Acceptance criteria:**
- [x] `.gitignore` in place.
- [x] Clean git commit ready for open-sourcing.

**Verification:**
- [x] `git status` shows clean working tree.

**Dependencies:** Tasks 1-4
**Files likely touched:** `.gitignore`
**Estimated scope:** XS (1 file)

---

## Checkpoint: Complete Project
- [x] Full suite passes.
- [x] Documentation complete.
- [x] Repository ready for publication.
