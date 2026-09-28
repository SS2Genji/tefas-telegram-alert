#!/usr/bin/env python3
"""
Unit and integration tests for tefas-telegram-alert.
Pure Python standard library (unittest).
"""

import unittest
from unittest.mock import MagicMock, patch

from tefas_alert import (
    calculate_return,
    format_currency_tr,
    format_telegram_message,
    send_telegram_message,
)


class TestTefasAlert(unittest.TestCase):
    def setUp(self):
        self.mock_positive_records = [
            {
                "fonKodu": "KTV",
                "fonUnvan": "KUVEYT TURK KIRA SERTIFIKASI",
                "tarih": "2026-09-28",
                "fiyat": 7.973047,
                "kisiSayisi": 47000,
                "portfoyBuyukluk": 39000000000.0,
            },
            {
                "fonKodu": "KTV",
                "fonUnvan": "KUVEYT TURK KIRA SERTIFIKASI",
                "tarih": "2026-09-25",
                "fiyat": 7.950762,
                "kisiSayisi": 46900,
                "portfoyBuyukluk": 38900000000.0,
            },
        ]

        self.mock_negative_records = [
            {
                "fonKodu": "KTV",
                "fonUnvan": "KUVEYT TURK KIRA SERTIFIKASI",
                "tarih": "2026-09-28",
                "fiyat": 7.940000,
                "kisiSayisi": 47000,
                "portfoyBuyukluk": 39000000000.0,
            },
            {
                "fonKodu": "KTV",
                "fonUnvan": "KUVEYT TURK KIRA SERTIFIKASI",
                "tarih": "2026-09-25",
                "fiyat": 7.950000,
                "kisiSayisi": 46900,
                "portfoyBuyukluk": 38900000000.0,
            },
        ]

    def test_calculate_return_positive(self):
        res = calculate_return(self.mock_positive_records)
        self.assertEqual(res["fund_code"], "KTV")
        self.assertAlmostEqual(res["diff"], 0.022285, places=6)
        self.assertGreater(res["pct_change"], 0)
        self.assertAlmostEqual(res["pct_change"], 0.280287, places=4)

    def test_calculate_return_negative(self):
        res = calculate_return(self.mock_negative_records)
        self.assertLess(res["diff"], 0)
        self.assertLess(res["pct_change"], 0)
        self.assertAlmostEqual(res["pct_change"], -0.125786, places=4)

    def test_calculate_return_insufficient_records(self):
        with self.assertRaises(ValueError):
            calculate_return([self.mock_positive_records[0]])

    def test_format_currency_tr(self):
        self.assertEqual(format_currency_tr(1234567.89, decimals=2), "1.234.567,89")
        self.assertEqual(format_currency_tr(7.973047, decimals=6), "7,973047")
        self.assertEqual(format_currency_tr(None), "N/A")

    def test_format_message_positive(self):
        metrics = calculate_return(self.mock_positive_records)
        msg = format_telegram_message(metrics)
        self.assertIn("🟢 <b>GÜNLÜK GETİRİ: POZİTİF</b>", msg)
        self.assertIn("<code>KTV</code>", msg)
        self.assertIn("+0.2803%", msg)

    def test_format_message_negative(self):
        metrics = calculate_return(self.mock_negative_records)
        msg = format_telegram_message(metrics)
        self.assertIn("🚨 <b>DİKKAT: NEGATİF GETİRİ!</b>", msg)
        self.assertIn("-0.1258%", msg)

    @patch("urllib.request.urlopen")
    def test_send_telegram_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"ok": true, "result": {}}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        success = send_telegram_message("test_token", "123456", "Test message")
        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
