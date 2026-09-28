#!/usr/bin/env python3
"""
tefas-telegram-alert Setup Wizard (configure.py)
Interactive CLI to configure alert schedules, tracked funds, and GitHub Actions cron.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

WORKFLOW_FILE = os.path.join(".github", "workflows", "daily_alert.yml")


def tsi_to_utc_cron(time_str: str) -> tuple[str, int, int]:
    """Convert Istanbul Time (TSI, UTC+3) string (HH:MM) to GitHub Actions cron expression."""
    clean = time_str.strip()
    match = re.match(r"^(\d{1,2})[:.](\d{2})$", clean)
    if not match:
        raise ValueError(f"Geçersiz saat formatı: '{time_str}'. Örnek format: 10:00 veya 09:15")

    tr_hour = int(match.group(1))
    minute = int(match.group(2))

    if not (0 <= tr_hour <= 23 and 0 <= minute <= 59):
        raise ValueError("Saat 00-23, dakika 00-59 arasında olmalıdır.")

    # Turkey is UTC+3 all year round
    utc_hour = (tr_hour - 3) % 24
    cron_expr = f"{minute} {utc_hour} * * 1-5"
    return cron_expr, tr_hour, minute


def update_workflow_cron(cron_expr: str, tr_hour: int, tr_min: int) -> bool:
    """Update cron schedule inside .github/workflows/daily_alert.yml."""
    if not os.path.exists(WORKFLOW_FILE):
        print(f"Hata: {WORKFLOW_FILE} bulunamadı.", file=sys.stderr)
        return False

    with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    new_comment = f"# Runs Monday through Friday at {cron_expr.split()[1]}:{cron_expr.split()[0]} UTC ({tr_hour:02d}:{tr_min:02d} TSI)"
    pattern = r"- cron:\s*['\"][^'\"]+['\"]"
    replacement = f"- cron: '{cron_expr}'"

    updated = re.sub(pattern, replacement, content)
    if updated == content:
        print("Uyarı: cron satırı güncellenemedi veya zaten aynı.", file=sys.stderr)
        return False

    with open(WORKFLOW_FILE, "w", encoding="utf-8") as f:
        f.write(updated)

    return True


def run_interactive():
    print("=" * 55)
    print("    tefas-telegram-alert Kurulum & Ayar Sihirbazı")
    print("=" * 55)
    print()

    # 1. Fund Selection
    curr_fund = os.getenv("FUND_CODE", "KTV")
    fund_input = input(f"1. Takip edilecek fon kodu [Varsayılan: {curr_fund}]: ").strip()
    target_funds = fund_input.upper() if fund_input else curr_fund

    # 2. Time Selection
    print("\n2. Bildirim Saati Seçin (TSİ - Türkiye Saati):")
    print("   [1] 10:00 (BIST Açılışı & Hisse Senedi Fonları için önerilen)")
    print("   [2] 09:15 (Kira Sertifikası & Para Piyasası Fonları açılışı)")
    print("   [3] 10:30 (Tüm TEFAS fonlarının kesinleştiği saat)")
    print("   [4] 18:30 (Piyasa Kapanışı)")
    print("   [5] Özel Saat Gir (Örn: 11:00, 14:15)")

    choice = input("Seçiminiz [1-5, Varsayılan: 1]: ").strip() or "1"

    if choice == "1":
        selected_time = "10:00"
    elif choice == "2":
        selected_time = "09:15"
    elif choice == "3":
        selected_time = "10:30"
    elif choice == "4":
        selected_time = "18:30"
    elif choice == "5":
        selected_time = input("Lütfen saati girin (Örn: 10:00): ").strip()
    else:
        selected_time = "10:00"

    try:
        cron_expr, tr_h, tr_m = tsi_to_utc_cron(selected_time)
    except ValueError as e:
        print(f"Hata: {e}", file=sys.stderr)
        return 1

    print(f"\n-> Seçilen Saat: {tr_h:02d}:{tr_m:02d} TSİ (GitHub Cron: '{cron_expr}')")

    # Update workflow
    if update_workflow_cron(cron_expr, tr_h, tr_m):
        print(f"✓ {WORKFLOW_FILE} dosyası {tr_h:02d}:{tr_m:02d} TSİ olarak güncellendi.")

    # Update FUND_CODE in workflow default as well
    with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
        wf = f.read()
    wf = re.sub(r"FUND_CODE:\s*\${{\s*vars\.FUND_CODE\s*\|\|\s*'[^']+'\s*}}", f"FUND_CODE: ${{{{ vars.FUND_CODE || '{target_funds}' }}}}", wf)
    with open(WORKFLOW_FILE, "w", encoding="utf-8") as f:
        f.write(wf)
    print(f"✓ Varsayılan fon '{target_funds}' olarak ayarlandı.")

    # 3. Git Push Option
    push_choice = input("\nAyarları GitHub'a gönderip hemen aktifleştirmek ister misiniz? (E/h): ").strip().lower()
    if push_choice in ("", "e", "evet", "y", "yes"):
        print("\nGitHub'a gönderiliyor...")
        subprocess.run(["git", "add", WORKFLOW_FILE], check=False)
        subprocess.run(["git", "commit", "-m", f"chore: update schedule to {tr_h:02d}:{tr_m:02d} TSI and funds to {target_funds}"], check=False)
        res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
        if res.returncode == 0:
            print("✓ Değişiklikler başarıyla GitHub'a gönderildi!")
            print(f"✓ Artık her iş günü saat {tr_h:02d}:{tr_m:02d}'de bildiriminiz otomatik gelecek.")
        else:
            print(f"Push hatası: {res.stderr}")

    print("\nKurulum tamamlandı!")
    return 0


if __name__ == "__main__":
    sys.exit(run_interactive())
