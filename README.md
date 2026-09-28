# tefas-telegram-alert

Automated TEFAS investment fund tracker and Telegram notifier. Runs on Python 3 standard library with no external dependencies, scheduled through GitHub Actions.

---

## Overview

`tefas-telegram-alert` queries the TEFAS JSON API, calculates day-over-day price differences and percentage returns, and sends a Telegram message every business morning. By default, it runs at 10:00 Istanbul time (07:00 UTC), coinciding with the Borsa Istanbul market open.

Positive returns are marked with `🟢`, negative returns with `🔴`, and sessions with unchanged prices with `⚪`.

---

## Features

- **Standard library only:** Uses Python's native `urllib.request`, `json`, `datetime`, and `os`. No `pip install` required.
- **Direct JSON API:** Queries `tefas.gov.tr/api/funds/fonGnlBlgSiraliGetir` directly instead of scraping HTML pages.
- **Serverless:** Runs on GitHub Actions scheduled cron. Does not require a personal server or computer left running.
- **Return tracking:** Distinguishes gains (`🟢`), losses (`🔴`), and neutral sessions (`⚪`).
- **Multi-fund support:** Track one fund (`KTV`) or multiple funds in one run (`KTV,TI1,MAC`).
- **Negative-only filter:** Optional `ALERT_NEGATIVE_ONLY` setting to receive messages only when a fund loses value.
- **Local dry run:** Test output and formatting locally with `DRY_RUN=true`.

---

## Message format

### Positive session
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

### Negative session
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

## Setup

### 1. Create a Telegram bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Send `/newbot` and follow the prompts to choose a display name and username. The username must end in `bot` or `_bot`.
3. Copy the HTTP API token BotFather gives you.
4. Open the chat with your new bot and click **Start** (or send `/start`). Telegram bots cannot send you messages until you start the conversation.

### 2. Find your Chat ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot).
2. Click **Start** or send any message.
3. Note the numerical `Id` in the reply.

### 3. Add GitHub repository secrets

1. Fork this repository.
2. In your fork, go to **Settings** > **Secrets and variables** > **Actions**.
3. Under **Repository secrets**, click **New repository secret** and add:

| Secret Name | Value | Required | Description |
| :--- | :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | `...` | Yes | Token from `@BotFather` |
| `TELEGRAM_CHAT_ID` | `...` | Yes | Numerical ID from `@userinfobot`. Supports comma-separated IDs (`ID1,ID2`) or group/channel IDs. |

4. Optional repository variables can be added under the **Variables** tab:

| Variable Name | Default | Example | Description |
| :--- | :--- | :--- | :--- |
| `FUND_CODE` | `KTV` | `KTV,TI1,MAC` | Comma-separated fund codes |
| `ALERT_NEGATIVE_ONLY` | `false` | `true` | Send notifications only on negative days |

### 4. Test run

1. Go to the **Actions** tab in your repository.
2. Select **Daily TEFAS Fund Alert** in the left sidebar.
3. Click **Run workflow** > **Run workflow**.
4. Check your Telegram chat for the notification.

---

## Changing schedule and funds

### Option A: Setup wizard

Clone the repository and run the setup script:

```bash
python3 configure.py
```

The script asks for your target funds and delivery time (such as `10:00` for stock market open, `09:15` for money market/debt funds, or a custom hour). It updates `.github/workflows/daily_alert.yml` with the correct UTC cron and can commit the change directly.

### Option B: Manual workflow edit

You can also change the schedule by editing line 6 of `.github/workflows/daily_alert.yml`:

```yaml
on:
  schedule:
    # 10:00 TSI (07:00 UTC) - BIST and equity funds
    - cron: '0 7 * * 1-5'

    # 09:15 TSI (06:15 UTC) - Money market and lease certificate funds
    # - cron: '15 6 * * 1-5'

    # 10:30 TSI (07:30 UTC) - After all fund prices settle
    # - cron: '30 7 * * 1-5'
```

---

## Configuration reference

| Environment Variable | Default | Allowed Values | Description |
| :--- | :--- | :--- | :--- |
| `FUND_CODE` | `KTV` | String (e.g. `KTV`, `TI1,ZKP`) | Target TEFAS fund code. Supports comma-separated lists. |
| `TELEGRAM_BOT_TOKEN` | None | String | Bot token from Telegram BotFather. |
| `TELEGRAM_CHAT_ID` | None | String / Int | Personal, group, or comma-separated chat IDs (`ID1,ID2`). |
| `ALERT_NEGATIVE_ONLY` | `false` | `true` / `false` | When true, skips messages on positive or neutral days. |
| `DRY_RUN` | `false` | `true` / `false` | Prints output to stdout without calling the Telegram API. |

---

## Local development

Run locally without third-party packages:

```bash
git clone https://github.com/SS2Genji/tefas-telegram-alert.git
cd tefas-telegram-alert

# Test with console output only
DRY_RUN=true FUND_CODE=KTV python3 tefas_alert.py

# Run unit tests
python3 test_alert.py
```

---

## FAQ

### When do TEFAS prices update?
Most fund prices are posted between 08:30 and 09:30 Istanbul time. Equity funds usually settle closer to 10:00. The default schedule runs at 10:00 TSI (07:00 UTC) on weekdays.

### What happens on weekends and holidays?
Markets are closed on weekends and Turkish national holidays. When prices are unchanged, the script marks the session as neutral (`⚪`) and will not trigger a negative alert.

### Can notifications be sent to a channel or group?
Yes. Add the bot to the group or channel, make sure it has permission to post, and use the group chat ID (which usually begins with `-100`).

---

## License

MIT License (c) 2026 [Ahmet Emir Şimşek](https://github.com/SS2Genji)
