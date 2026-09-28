# Implementation Plan: tefas-telegram-alert

## Overview
A lightweight, zero-dependency, open-source automated alerting engine that tracks TEFAS investment funds (default: `KTV` - KT Portföy Kira Sertifikası Katılım Fonu) every business morning, calculates daily returns, and delivers instant Telegram notifications distinguishing positive gains from negative drops. Powered by pure Python 3 standard library and automated for free via GitHub Actions cron schedules.

## Architecture Decisions
- **Zero External Dependencies (`/ponytail full`):** Use pure Python 3 standard library (`urllib.request`, `json`, `datetime`, `os`). Eliminates `pip install` failures, maintenance overhead, and security vulnerability supply chains.
- **Direct Official TEFAS JSON API:** Use `https://www.tefas.gov.tr/api/funds/fonGnlBlgSiraliGetir` endpoint with proper payload. Zero brittle HTML scraping.
- **Serverless Automation via GitHub Actions:** Schedule workflow cron at `15 6 * * 1-5` (09:15 TSI) on business days with `workflow_dispatch` manual trigger. Zero server hosting costs.
- **Clear Telegram Visual Contract:**
  - Positive gain: `🟢 [FON] Günlük Getiri: +%X.XX`
  - Negative loss: `🚨 [FON] DİKKAT: Negatif Getiri: -%X.XX`
  - Neutral / Weekend: Informative status without false alarms.

## Task List

### Phase 1: Core Engine & Testing
- [ ] Task 1: Build `tefas_alert.py` with pure Python stdlib (TEFAS fetcher, return calculator, Telegram dispatcher, env config).
- [ ] Task 2: Build `test_alert.py` verifying math, message formatting, and live TEFAS query in dry-run mode.

### Checkpoint: Core Engine
- [ ] `python3 test_alert.py` passes 100%.
- [ ] Live TEFAS fetch for `KTV` returns accurate price and calculated return.

### Phase 2: Automation & Documentation
- [ ] Task 3: Create GitHub Actions workflow `.github/workflows/daily_alert.yml` with cron schedule and secrets injection.
- [ ] Task 4: Write comprehensive, open-source `README.md` with step-by-step setup guide (BotFather, Chat ID, GitHub Secrets, multi-fund configuration).

### Checkpoint: Complete Project
- [ ] All files in place and clean.
- [ ] `git init`, `.gitignore`, and initial commit prepared.
- [ ] End-to-end dry-run verified.

## Risks and Mitigations
| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| TEFAS rate limits or temporary downtime | Med | Retry loop with exponential backoff in `tefas_alert.py`. |
| Weekend or official holidays (no trading) | Low | Detect matching last two dates; report holiday/stable status without false negative alert. |
| Telegram API errors / invalid tokens | Low | Catch HTTP errors, print clear diagnostic messages in GitHub Actions logs. |

## Open Questions
- None. Requirements are clear, minimal, and fully scoped.
