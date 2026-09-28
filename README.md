# tefas-telegram-alert

Automated daily TEFAS investment fund tracker and Telegram alert engine. Built with pure Python 3 standard library, requiring zero third-party dependencies, and running completely free in the cloud via GitHub Actions.

---

## Overview

Tracking Turkish Electronic Fund Trading Platform (TEFAS) funds manually every morning is tedious. `tefas-telegram-alert` connects directly to TEFAS's official JSON API, calculates day-over-day price differences and percentage returns, and delivers clean, formatted Telegram alerts directly to your phone every business morning at 09:15 TSI (06:15 UTC).

When daily returns are positive, it sends a green status notification. When returns drop into negative territory, it fires an immediate high-priority warning alert (`🚨 DİKKAT`).

---

## Features

- **Zero External Dependencies:** Built strictly using Python 3 standard library (`urllib.request`, `json`, `datetime`, `os`). No `pip install`, no broken dependency trees, no supply-chain vulnerabilities.
- **Direct Official TEFAS API:** Queries `https://www.tefas.gov.tr/api/funds/fonGnlBlgSiraliGetir` natively. No fragile HTML parsing or headless browser scraping.
- **Serverless & 100% Free:** Runs on GitHub Actions scheduled cron. Requires no 24/7 server, VPS, or always-on home computer.
- **Smart Return Classification:** Automatically distinguishes gains (`🟢`), losses (`🚨`), and neutral market sessions (`⚪`).
- **Multi-Fund Monitoring:** Track a single fund (`KTV`) or multiple funds concurrently (`KTV,TI1,MAC,ZKP`).
- **Filter Mode:** Optional `ALERT_NEGATIVE_ONLY` toggle to receive alerts exclusively when returns are negative.
- **Local Dry-Run Support:** Test output locally without sending real Telegram messages (`DRY_RUN=true`).

---

## Telegram Message Showcase

### Positive Session (Gain)
```text
🟢 GÜNLÜK GETİRİ: POZİTİF

Fon: KTV - KUVEYT TÜRK PORTFÖY KISA VADELİ KİRA SERTİFİKALARI KATILIM (TL) FONU
Tarih: 2026-09-28 (Önceki seans: 2026-09-25)

Güncel Fiyat: 7,973047 ₺
Günlük Fark: +0,022285 ₺
Getiri Oranı: +0.28%

Yatırımcı Sayısı: 47.029
Portföy Büyüklüğü: 39,37 Milyar ₺
```

### Negative Session (Alert)
```text
🔴 GÜNLÜK GETİRİ: NEGATİF

Fon: KTV - KUVEYT TÜRK PORTFÖY KISA VADELİ KİRA SERTİFİKALARI KATILIM (TL) FONU
Tarih: 2026-09-28 (Önceki seans: 2026-09-25)

Güncel Fiyat: 7,940000 ₺
Günlük Fark: -0,010762 ₺
Getiri Oranı: -0.14%

Yatırımcı Sayısı: 47.000
Portföy Büyüklüğü: 39,00 Milyar ₺
```

---

## Step-by-Step Setup Guide

Setting up your personal bot takes less than 3 minutes.

### 1. Create Your Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Send `/newbot` and follow the instructions:
   - Provide a display name (e.g. `My Fund Tracker`).
   - Provide a unique username ending in `bot` (e.g. `my_tefas_tracker_bot`).
3. BotFather will provide your **HTTP API Token** (e.g. `7123456789:AAH...`). Copy this token.
4. Open your newly created bot in Telegram and click **Start** (or send `/start`).

### 2. Get Your Telegram Chat ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot).
2. Click **Start** or send any message.
3. The bot will respond with your personal numerical **Id** (e.g. `123456789`). Copy this number.

### 3. Fork and Configure GitHub Secrets

1. Fork this repository to your personal GitHub account.
2. In your forked repository, navigate to **Settings** &rarr; **Secrets and variables** &rarr; **Actions**.
3. Under **Repository secrets**, click **New repository secret** and add:

| Secret Name | Value | Required | Description |
| :--- | :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | `7123456789:AAH...` | Yes | Token received from `@BotFather` |
| `TELEGRAM_CHAT_ID` | `123456789` | Yes | Numerical ID received from `@userinfobot` |

4. *(Optional)* Under **Variables** (or Secrets), configure optional parameters:

| Variable Name | Default | Example | Description |
| :--- | :--- | :--- | :--- |
| `FUND_CODE` | `KTV` | `KTV,TI1,MAC` | Comma-separated TEFAS fund codes |
| `ALERT_NEGATIVE_ONLY` | `false` | `true` | When `true`, only notifies on negative returns |

### 4. Run First Test (Manual Trigger)

1. In your repository, go to the **Actions** tab.
2. Select **Daily TEFAS Fund Alert** from the left sidebar.
3. Click **Run workflow** &rarr; **Run workflow**.
4. Check your Telegram: your fund notification will arrive in seconds!

---

## Customizing Alert Schedule & Funds

### Option A: Interactive Setup Wizard (Fastest)

Run the built-in wizard to pick your desired delivery time and funds:

```bash
python3 configure.py
```

The wizard prompts you for your preferred Istanbul time (e.g. `10:00` for stock market open, `09:15` for debt securities/money market, or any custom time), automatically converts it to GitHub Actions UTC cron, updates `.github/workflows/daily_alert.yml`, and offers to commit and push changes.

### Option B: Manual Workflow Edit

Edit `.github/workflows/daily_alert.yml` directly on GitHub:

```yaml
on:
  schedule:
    # 09:15 TSI (06:15 UTC) -> Kira sertifikası & para piyasası fonları
    - cron: '15 6 * * 1-5'

    # 10:00 TSI (07:00 UTC) -> BIST & hisse senedi fonları
    # - cron: '0 7 * * 1-5'

    # 10:30 TSI (07:30 UTC) -> Tüm fonların kesinleştiği saat
    # - cron: '30 7 * * 1-5'
```

---

## Configuration Reference

| Environment Variable | Default | Allowed Values | Description |
| :--- | :--- | :--- | :--- |
| `FUND_CODE` | `KTV` | String (e.g. `KTV`, `TI1,ZKP`) | Target TEFAS fund code(s). Comma-separated for batch tracking. |
| `TELEGRAM_BOT_TOKEN` | None | String | Secret bot token issued by Telegram BotFather. |
| `TELEGRAM_CHAT_ID` | None | String / Int | Personal or channel/group chat ID. |
| `ALERT_NEGATIVE_ONLY` | `false` | `true` / `false` | If enabled, skips Telegram message when return is positive or zero. |
| `DRY_RUN` | `false` | `true` / `false` | Prints output to console without making Telegram API calls. |

---

## Local Execution & Development

Run directly on your local workstation without installing third-party packages:

```bash
# Clone the repository
git clone https://github.com/SS2Genji/tefas-telegram-alert.git
cd tefas-telegram-alert

# Test in dry-run mode (no Telegram credentials required)
DRY_RUN=true FUND_CODE=KTV python3 tefas_alert.py

# Run unit test suite
python3 test_alert.py
```

---


## FAQ & Market Hours

### When are TEFAS prices updated?
TEFAS publishes fund clearing prices once per business day, usually between 08:30 and 09:15 Istanbul Time (TSI). The automated GitHub Actions workflow is scheduled for **09:15 TSI (06:15 UTC)** to ensure prices have cleared.

### What happens on weekends and official holidays?
Trading sessions do not occur on weekends or Turkish national holidays. When TEFAS returns unchanged prices, the system reports the session as neutral (`⚪`) and will not trigger false negative alerts.

### Can I send notifications to a Telegram Channel or Group?
Yes. Add your bot to the group or channel as an Administrator, obtain the group/channel Chat ID (typically starting with a minus `-100...`), and set `TELEGRAM_CHAT_ID` accordingly.

---

## License

MIT License. Free for personal and commercial use.
