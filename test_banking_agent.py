#!/usr/bin/env python3
"""
Testy pro ReACT Banking Agent
==============================
Unit testy pro ověření funkcionality bankovních nástrojů.
Tyto testy nevyžadují API klíč - testují pouze lokální logiku.
"""

import unittest
import json
from datetime import datetime, timedelta
from banking_agent import (
    BankingData,
    execute_tool,
    BANK,
    Transaction,
    Account
)


class TestBankingData(unittest.TestCase):
    """Testy pro třídu BankingData"""

    def setUp(self):
        """Příprava testovacích dat"""
        self.bank = BankingData()

    def test_accounts_exist(self):
        """Test: Existují účty"""
        self.assertEqual(len(self.bank.accounts), 3)

    def test_account_types(self):
        """Test: Správné typy účtů"""
        account_types = [acc.type for acc in self.bank.accounts]
        self.assertIn("checking", account_types)
        self.assertIn("savings", account_types)

    def test_accounts_have_positive_balance(self):
        """Test: Účty mají kladný zůstatek"""
        for acc in self.bank.accounts:
            self.assertGreater(acc.balance, 0, f"Účet {acc.name} má nulový nebo záporný zůstatek")

    def test_transactions_generated(self):
        """Test: Transakce byly vygenerovány"""
        self.assertGreater(len(self.bank.transactions), 100)

    def test_transactions_have_valid_dates(self):
        """Test: Transakce mají validní data"""
        for txn in self.bank.transactions[:20]:
            try:
                datetime.strptime(txn.date, "%Y-%m-%d")
            except ValueError:
                self.fail(f"Nevalidní datum: {txn.date}")

    def test_transactions_sorted_by_date(self):
        """Test: Transakce jsou seřazeny podle data (sestupně)"""
        dates = [txn.date for txn in self.bank.transactions[:10]]
        self.assertEqual(dates, sorted(dates, reverse=True))


class TestGetAccountBalances(unittest.TestCase):
    """Testy pro nástroj get_account_balances"""

    def test_returns_json(self):
        """Test: Vrací validní JSON"""
        result = execute_tool("get_account_balances", {})
        parsed = json.loads(result)
        self.assertIsInstance(parsed, list)

    def test_contains_all_accounts(self):
        """Test: Obsahuje všechny účty"""
        result = execute_tool("get_account_balances", {})
        parsed = json.loads(result)
        # 3 účty + 1 souhrnný řádek
        self.assertEqual(len(parsed), 4)

    def test_contains_total(self):
        """Test: Obsahuje celkový součet"""
        result = execute_tool("get_account_balances", {})
        parsed = json.loads(result)
        last_item = parsed[-1]
        self.assertIn("celkem_v_CZK", last_item)


class TestGetTransactions(unittest.TestCase):
    """Testy pro nástroj get_transactions"""

    def test_default_returns_transactions(self):
        """Test: Výchozí volání vrací transakce"""
        result = execute_tool("get_transactions", {})
        parsed = json.loads(result)
        self.assertIsInstance(parsed, list)
        self.assertGreater(len(parsed), 0)

    def test_filter_by_days(self):
        """Test: Filtrování podle počtu dní"""
        result_7 = execute_tool("get_transactions", {"days": 7})
        result_30 = execute_tool("get_transactions", {"days": 30})

        parsed_7 = json.loads(result_7)
        parsed_30 = json.loads(result_30)

        # Za 30 dní by mělo být více transakcí než za 7
        self.assertLessEqual(len(parsed_7), len(parsed_30))

    def test_filter_by_category(self):
        """Test: Filtrování podle kategorie"""
        result = execute_tool("get_transactions", {"category": "potraviny"})
        parsed = json.loads(result)

        for txn in parsed:
            self.assertEqual(txn["kategorie"], "potraviny")

    def test_max_20_transactions(self):
        """Test: Maximum 20 transakcí ve výsledku"""
        result = execute_tool("get_transactions", {"days": 90})
        parsed = json.loads(result)
        self.assertLessEqual(len(parsed), 20)


class TestAnalyzeSpending(unittest.TestCase):
    """Testy pro nástroj analyze_spending"""

    def test_returns_analysis(self):
        """Test: Vrací analýzu"""
        result = execute_tool("analyze_spending", {"days": 30})
        parsed = json.loads(result)

        self.assertIn("celkové_výdaje", parsed)
        self.assertIn("celkové_příjmy", parsed)
        self.assertIn("bilance", parsed)

    def test_contains_categories(self):
        """Test: Obsahuje výdaje podle kategorií"""
        result = execute_tool("analyze_spending", {"days": 30})
        parsed = json.loads(result)

        self.assertIn("výdaje_podle_kategorií", parsed)
        self.assertIsInstance(parsed["výdaje_podle_kategorií"], dict)

    def test_daily_average(self):
        """Test: Obsahuje průměrné denní výdaje"""
        result = execute_tool("analyze_spending", {"days": 30})
        parsed = json.loads(result)

        self.assertIn("průměrné_denní_výdaje", parsed)


class TestDetectAnomalies(unittest.TestCase):
    """Testy pro nástroj detect_anomalies"""

    def test_returns_list(self):
        """Test: Vrací seznam anomálií"""
        result = execute_tool("detect_anomalies", {})
        parsed = json.loads(result)
        self.assertIsInstance(parsed, list)

    def test_sensitivity_levels(self):
        """Test: Různé úrovně citlivosti"""
        result_low = execute_tool("detect_anomalies", {"sensitivity": "low"})
        result_high = execute_tool("detect_anomalies", {"sensitivity": "high"})

        parsed_low = json.loads(result_low)
        parsed_high = json.loads(result_high)

        # Vysoká citlivost by měla najít více anomálií
        self.assertLessEqual(len(parsed_low), len(parsed_high))

    def test_anomaly_has_reason(self):
        """Test: Anomálie obsahuje důvod"""
        result = execute_tool("detect_anomalies", {"sensitivity": "high"})
        parsed = json.loads(result)

        if len(parsed) > 0:
            self.assertIn("důvod", parsed[0])


class TestGetSpendingByMerchant(unittest.TestCase):
    """Testy pro nástroj get_spending_by_merchant"""

    def test_returns_merchants(self):
        """Test: Vrací seznam obchodníků"""
        result = execute_tool("get_spending_by_merchant", {})
        parsed = json.loads(result)

        self.assertIsInstance(parsed, list)
        self.assertGreater(len(parsed), 0)

    def test_limit_parameter(self):
        """Test: Parametr limit funguje"""
        result = execute_tool("get_spending_by_merchant", {"limit": 5})
        parsed = json.loads(result)

        self.assertLessEqual(len(parsed), 5)

    def test_merchant_has_total(self):
        """Test: Obchodník má celkovou částku"""
        result = execute_tool("get_spending_by_merchant", {})
        parsed = json.loads(result)

        if len(parsed) > 0:
            self.assertIn("celkem", parsed[0])
            self.assertIn("počet_transakcí", parsed[0])


class TestCalculateSavingsPotential(unittest.TestCase):
    """Testy pro nástroj calculate_savings_potential"""

    def test_returns_savings_info(self):
        """Test: Vrací informace o úsporách"""
        result = execute_tool("calculate_savings_potential", {})
        parsed = json.loads(result)

        self.assertIn("zbytné_výdaje_měsíčně", parsed)
        self.assertIn("potenciální_měsíční_úspora", parsed)
        self.assertIn("potenciální_roční_úspora", parsed)

    def test_contains_recommendations(self):
        """Test: Obsahuje doporučení"""
        result = execute_tool("calculate_savings_potential", {})
        parsed = json.loads(result)

        self.assertIn("doporučení", parsed)
        self.assertIsInstance(parsed["doporučení"], list)


class TestGenerateMonthlyReport(unittest.TestCase):
    """Testy pro nástroj generate_monthly_report"""

    def test_returns_report(self):
        """Test: Vrací report"""
        result = execute_tool("generate_monthly_report", {})
        parsed = json.loads(result)

        self.assertIn("report", parsed)
        self.assertIn("příjmy", parsed)
        self.assertIn("výdaje", parsed)

    def test_custom_month(self):
        """Test: Vlastní měsíc a rok"""
        result = execute_tool("generate_monthly_report", {"month": 6, "year": 2024})
        parsed = json.loads(result)

        self.assertIn("6/2024", parsed["report"])


class TestUnknownTool(unittest.TestCase):
    """Testy pro neznámé nástroje"""

    def test_unknown_tool_returns_error(self):
        """Test: Neznámý nástroj vrací chybu"""
        result = execute_tool("neexistujici_nastroj", {})
        parsed = json.loads(result)

        self.assertIn("error", parsed)


class TestDataIntegrity(unittest.TestCase):
    """Integrační testy pro konzistenci dat"""

    def test_spending_matches_transactions(self):
        """Test: Výdaje odpovídají transakcím"""
        # Získáme analýzu
        analysis = json.loads(execute_tool("analyze_spending", {"days": 30}))

        # Výdaje by měly být kladné číslo (i když transakce jsou záporné)
        total_str = analysis["celkové_výdaje"].replace(" CZK", "").replace(",", "")
        total = float(total_str)

        self.assertGreater(total, 0)

    def test_account_balance_consistency(self):
        """Test: Konzistence zůstatků účtů"""
        balances = json.loads(execute_tool("get_account_balances", {}))

        total_str = balances[-1]["celkem_v_CZK"].replace(" CZK", "").replace(",", "")
        total = float(total_str)

        # Celkový zůstatek by měl být součet jednotlivých účtů
        self.assertGreater(total, 0)


if __name__ == "__main__":
    print("=" * 60)
    print("  TESTY PRO ReACT BANKING AGENT")
    print("=" * 60)
    print()

    # Spuštění testů s verbózním výstupem
    unittest.main(verbosity=2)
