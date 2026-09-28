#!/usr/bin/env python3
"""
tefas-telegram-alert
Zero-dependency, automated TEFAS investment fund tracker & Telegram alert system.
Powered by pure Python 3 standard library.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

TEFAS_API_URL = "https://www.tefas.gov.tr/api/funds/fonGnlBlgSiraliGetir"

HTTP_HEADERS = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Origin": "https://www.tefas.gov.tr",
    "Referer": "https://www.tefas.gov.tr/tr/fon-verileri",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}


def fetch_fund_history(
    fund_code: str,
    days: int = 10,
    max_retries: int = 3,
    timeout: int = 15,
) -> List[Dict[str, Any]]:
    """Fetch fund historical price records from TEFAS official JSON API.

    Returns records sorted by date descending (latest session first).
    """
    code = fund_code.strip().upper()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    payload = {
        "fonTipi": "YAT",
        "fonKodu": code,
        "aramaMetni": None,
        "fonTurKod": None,
        "fonGrubu": None,
        "sfonTurKod": None,
        "fonTurAciklama": None,
        "kurucuKod": None,
        "basTarih": start_date.strftime("%Y%m%d"),
        "bitTarih": end_date.strftime("%Y%m%d"),
        "basSira": 1,
        "bitSira": 100000,
        "dil": "TR",
        "sFonTurKod": "",
        "fonKod": "",
        "fonGrup": "",
        "fonUnvanTip": "",
    }

    req_data = json.dumps(payload).encode("utf-8")

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                TEFAS_API_URL,
                data=req_data,
                headers=HTTP_HEADERS,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            err_code = data.get("errorCode")
            err_msg = data.get("errorMessage")
            if err_code or (err_msg and "veri bulunamadı" not in err_msg.lower()):
                raise RuntimeError(f"TEFAS API error: {err_msg} (code: {err_code})")

            rows = data.get("resultList") or []
            if not rows:
                return []

            # Sort descending by date (latest first)
            return sorted(rows, key=lambda r: r.get("tarih", ""), reverse=True)

        except (urllib.error.URLError, TimeoutError, RuntimeError) as e:
            if attempt == max_retries:
                raise RuntimeError(
                    f"Failed to fetch TEFAS data for '{code}' after {max_retries} attempts: {e}"
                ) from e
            time.sleep(2 * attempt)

    return []


def calculate_return(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate daily price difference and percentage return between the last 2 trading sessions."""
    if len(records) < 2:
        raise ValueError(
            f"Insufficient trading data: expected at least 2 sessions, got {len(records)}"
        )

    curr = records[0]
    prev = records[1]

    p_curr = float(curr["fiyat"])
    p_prev = float(prev["fiyat"])

    diff = p_curr - p_prev
    pct_change = (diff / p_prev) * 100 if p_prev > 0 else 0.0

    return {
        "fund_code": curr.get("fonKodu", ""),
        "fund_name": curr.get("fonUnvan", ""),
        "date_curr": curr.get("tarih", ""),
        "date_prev": prev.get("tarih", ""),
        "price_curr": p_curr,
        "price_prev": p_prev,
        "diff": diff,
        "pct_change": pct_change,
        "investors": curr.get("kisiSayisi"),
        "portfolio_size": curr.get("portfoyBuyukluk"),
    }


def format_currency_tr(val: Optional[float], decimals: int = 2) -> str:
    """Format float into Turkish readable format: 1.234.567,89"""
    if val is None:
        return "N/A"
    formatted = f"{val:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def format_compact_currency_tr(val: Optional[float]) -> str:
    """Format large currency values into compact readable units: 39,37 Milyar ₺, 45,50 Milyon ₺, etc."""
    if val is None:
        return "N/A"
    abs_val = abs(val)
    if abs_val >= 1_000_000_000:
        num_str = f"{val / 1_000_000_000:.2f}".replace(".", ",")
        return f"{num_str} Milyar ₺"
    elif abs_val >= 1_000_000:
        num_str = f"{val / 1_000_000:.2f}".replace(".", ",")
        return f"{num_str} Milyon ₺"
    elif abs_val >= 1_000:
        num_str = f"{val / 1_000:.2f}".replace(".", ",")
        return f"{num_str} Bin ₺"
    else:
        num_str = f"{val:.2f}".replace(".", ",")
        return f"{num_str} ₺"


def format_telegram_message(metrics: Dict[str, Any]) -> str:
    """Format metrics into a clean, minimal HTML Telegram alert message."""
    pct = metrics["pct_change"]
    diff = metrics["diff"]

    if pct > 0:
        header = "🟢 <b>GÜNLÜK GETİRİ: POZİTİF</b>"
        pct_sign = "+"
    elif pct < 0:
        header = "🔴 <b>GÜNLÜK GETİRİ: NEGATİF</b>"
        pct_sign = ""
    else:
        header = "⚪ <b>GÜNLÜK GETİRİ: DEĞİŞİM YOK (NÖTR)</b>"
        pct_sign = ""

    fund_code = metrics["fund_code"]
    fund_name = metrics["fund_name"]
    date_curr = metrics["date_curr"]
    date_prev = metrics["date_prev"]
    price_curr = format_currency_tr(metrics["price_curr"], decimals=6)
    diff_str = f"{pct_sign}{format_currency_tr(diff, decimals=6)}"
    pct_str = f"{pct_sign}{pct:.2f}%"

    investors_str = (
        f"{metrics['investors']:,}".replace(",", ".")
        if metrics.get("investors") is not None
        else "N/A"
    )
    portfolio_str = format_compact_currency_tr(metrics.get("portfolio_size"))

    return (
        f"{header}\n\n"
        f"<b>Fon:</b> <code>{fund_code}</code> - {fund_name}\n"
        f"<b>Tarih:</b> {date_curr} <i>(Önceki seans: {date_prev})</i>\n\n"
        f"<b>Güncel Fiyat:</b> <code>{price_curr} ₺</code>\n"
        f"<b>Günlük Fark:</b> <code>{diff_str} ₺</code>\n"
        f"<b>Getiri Oranı:</b> <b>{pct_str}</b>\n\n"
        f"<b>Yatırımcı Sayısı:</b> {investors_str}\n"
        f"<b>Portföy Büyüklüğü:</b> {portfolio_str}"
    )


def send_telegram_message(
    bot_token: str,
    chat_id: str,
    text: str,
    timeout: int = 15,
) -> bool:
    """Send HTML message via Telegram Bot API using urllib."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=req_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return bool(data.get("ok"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"Telegram API HTTP error {e.code}: {err_body}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Telegram send error: {e}", file=sys.stderr)
        return False


def run_tracker() -> int:
    """Main execution orchestrator."""
    fund_codes_env = os.getenv("FUND_CODE", "KTV")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    alert_negative_only = (
        os.getenv("ALERT_NEGATIVE_ONLY", "false").lower() in ("true", "1", "yes")
    )
    dry_run = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")

    funds = [c.strip().upper() for c in fund_codes_env.split(",") if c.strip()]
    if not funds:
        print("Error: No fund codes specified.", file=sys.stderr)
        return 1

    if not dry_run and (not bot_token or not chat_id):
        print(
            "Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set (or set DRY_RUN=true).",
            file=sys.stderr,
        )
        return 1

    total_funds = len(funds)
    print(f"Tracking {total_funds} fund(s): {', '.join(funds)} (DryRun={dry_run})")

    has_error = False

    for code in funds:
        print(f"\n--- Checking {code} ---")
        try:
            records = fetch_fund_history(code, days=12)
            if len(records) < 2:
                print(
                    f"Warning: Not enough trading records found for {code} (got {len(records)}). "
                    "Skipping...",
                    file=sys.stderr,
                )
                continue

            metrics = calculate_return(records)
            msg = format_telegram_message(metrics)

            pct = metrics["pct_change"]
            print(
                f"{code} -> Current: {metrics['price_curr']} | Prev: {metrics['price_prev']} | "
                f"Change: {pct:+.4f}%"
            )

            # Check if user only requested alerts on negative drops
            if alert_negative_only and pct >= 0:
                print(f"Skipping notification for {code} (ALERT_NEGATIVE_ONLY=true and return >= 0).")
                continue

            if dry_run:
                print("\n[DRY RUN - Message Preview]:")
                print(msg)
                print("[DRY RUN - End Preview]\n")
            else:
                success = send_telegram_message(bot_token, chat_id, msg)
                if success:
                    print(f"Successfully delivered Telegram alert for {code}.")
                else:
                    print(f"Failed to deliver Telegram alert for {code}.", file=sys.stderr)
                    has_error = True

        except Exception as e:
            print(f"Error processing fund '{code}': {e}", file=sys.stderr)
            has_error = True

    return 1 if has_error else 0


if __name__ == "__main__":
    sys.exit(run_tracker())
