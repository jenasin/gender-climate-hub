#!/usr/bin/env python3
"""
🏦 ReACT Banking Agent
======================
Inteligentní agent pro analýzu bankovních dat využívající ReACT pattern
(Reasoning → Action → Observation)

Pro článek o AI agentech a jejich praktickém využití.
"""

import anthropic
import json
from datetime import datetime, timedelta
from typing import Any
from dataclasses import dataclass
import random

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 BAREVNÝ VÝSTUP PRO LEPŠÍ ČITELNOST
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'═' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}  {text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'═' * 60}{Colors.ENDC}\n")

def print_thought(text: str):
    print(f"{Colors.YELLOW}💭 MYŠLENÍ:{Colors.ENDC} {text}")

def print_action(tool: str, params: str):
    print(f"{Colors.CYAN}⚡ AKCE:{Colors.ENDC} {tool}")
    print(f"{Colors.DIM}   └─ parametry: {params}{Colors.ENDC}")

def print_observation(text: str):
    print(f"{Colors.GREEN}👁️ POZOROVÁNÍ:{Colors.ENDC}")
    for line in text.split('\n')[:10]:  # max 10 řádků
        print(f"   {line}")
    if text.count('\n') > 10:
        print(f"   {Colors.DIM}... (zkráceno){Colors.ENDC}")

def print_answer(text: str):
    print(f"\n{Colors.BOLD}{Colors.GREEN}✅ ODPOVĚĎ:{Colors.ENDC}")
    print(f"{Colors.GREEN}{text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.RED}❌ CHYBA: {text}{Colors.ENDC}")

# ═══════════════════════════════════════════════════════════════════════════════
# 💾 SIMULOVANÁ BANKOVNÍ DATA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Transaction:
    id: str
    date: str
    amount: float
    currency: str
    category: str
    merchant: str
    account_id: str
    description: str

@dataclass
class Account:
    id: str
    name: str
    type: str
    balance: float
    currency: str
    iban: str

class BankingData:
    """Simulovaná bankovní databáze pro demo účely"""

    def __init__(self):
        self.accounts = [
            Account("ACC001", "Běžný účet", "checking", 45_320.50, "CZK", "CZ6508000000192000145399"),
            Account("ACC002", "Spořicí účet", "savings", 250_000.00, "CZK", "CZ6508000000192000145400"),
            Account("ACC003", "EUR účet", "checking", 2_150.75, "EUR", "CZ6508000000192000145401"),
        ]

        # Generování realistických transakcí za poslední 3 měsíce
        self.transactions = self._generate_transactions()

    def _generate_transactions(self) -> list[Transaction]:
        merchants = {
            "potraviny": ["Albert", "Lidl", "Kaufland", "Billa", "Tesco"],
            "restaurace": ["U Fleků", "Ambiente", "KFC", "McDonald's", "Starbucks"],
            "doprava": ["ČD", "Bolt", "Uber", "Shell", "OMV"],
            "zábava": ["Cinema City", "Spotify", "Netflix", "Steam", "PlayStation"],
            "nakupy": ["Alza", "Mall.cz", "Notino", "Zara", "H&M"],
            "bydleni": ["ČEZ", "Pražské vodovody", "T-Mobile", "O2", "Vodafone"],
            "zdravi": ["Lékárna Dr.Max", "Benu", "FitPark", "Gym Beam", "Decathlon"],
        }

        transactions = []
        base_date = datetime.now()

        for i in range(150):
            days_ago = random.randint(0, 90)
            date = base_date - timedelta(days=days_ago)
            category = random.choice(list(merchants.keys()))
            merchant = random.choice(merchants[category])

            # Různé částky podle kategorie
            amount_ranges = {
                "potraviny": (-2500, -150),
                "restaurace": (-1500, -120),
                "doprava": (-800, -50),
                "zábava": (-600, -99),
                "nakupy": (-15000, -200),
                "bydleni": (-5000, -500),
                "zdravi": (-3000, -100),
            }

            min_amt, max_amt = amount_ranges[category]
            amount = round(random.uniform(min_amt, max_amt), 2)

            # Příjmy (výplata, převody)
            if random.random() < 0.08:
                amount = round(random.uniform(25000, 65000), 2)
                category = "příjem"
                merchant = random.choice(["Zaměstnavatel s.r.o.", "Převod z účtu", "Vrácení DPH"])

            transactions.append(Transaction(
                id=f"TXN{i:05d}",
                date=date.strftime("%Y-%m-%d"),
                amount=amount,
                currency="CZK",
                category=category,
                merchant=merchant,
                account_id="ACC001",
                description=f"Platba kartou - {merchant}"
            ))

        return sorted(transactions, key=lambda x: x.date, reverse=True)

# Globální instance bankovních dat
BANK = BankingData()

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 STATICKÉ NÁSTROJE (TOOLS) PRO AGENTA
# ═══════════════════════════════════════════════════════════════════════════════

TOOLS = [
    {
        "name": "get_account_balances",
        "description": "Získá přehled všech účtů a jejich aktuálních zůstatků. Vrací seznam účtů s typem, zůstatkem a měnou.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_transactions",
        "description": "Získá seznam transakcí s možností filtrování. Lze filtrovat podle období, kategorie, minimální/maximální částky.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Počet dní zpětně (výchozí 30)"
                },
                "category": {
                    "type": "string",
                    "description": "Filtr podle kategorie (potraviny, restaurace, doprava, zábava, nakupy, bydleni, zdravi, příjem)"
                },
                "min_amount": {
                    "type": "number",
                    "description": "Minimální částka (záporná pro výdaje)"
                },
                "max_amount": {
                    "type": "number",
                    "description": "Maximální částka"
                }
            },
            "required": []
        }
    },
    {
        "name": "analyze_spending",
        "description": "Analyzuje výdaje za dané období. Vrací rozpad podle kategorií, průměrné denní výdaje a trendy.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Počet dní pro analýzu (výchozí 30)"
                }
            },
            "required": []
        }
    },
    {
        "name": "detect_anomalies",
        "description": "Detekuje podezřelé nebo neobvyklé transakce. Hledá vysoké částky, opakované platby, neobvyklé časy.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sensitivity": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Citlivost detekce (výchozí medium)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_spending_by_merchant",
        "description": "Zobrazí výdaje seskupené podle obchodníka. Užitečné pro identifikaci největších příjemců peněz.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Počet dní zpětně (výchozí 30)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Počet top obchodníků (výchozí 10)"
                }
            },
            "required": []
        }
    },
    {
        "name": "calculate_savings_potential",
        "description": "Vypočítá potenciál úspor na základě analýzy zbytných výdajů a srovnání s předchozím obdobím.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "generate_monthly_report",
        "description": "Vygeneruje kompletní měsíční finanční report s grafy a doporučeními.",
        "input_schema": {
            "type": "object",
            "properties": {
                "month": {
                    "type": "integer",
                    "description": "Měsíc (1-12), výchozí aktuální"
                },
                "year": {
                    "type": "integer",
                    "description": "Rok, výchozí aktuální"
                }
            },
            "required": []
        }
    }
]

# ═══════════════════════════════════════════════════════════════════════════════
# ⚙️ IMPLEMENTACE NÁSTROJŮ
# ═══════════════════════════════════════════════════════════════════════════════

def execute_tool(name: str, params: dict) -> str:
    """Spustí nástroj a vrátí výsledek jako string"""

    if name == "get_account_balances":
        result = []
        total_czk = 0
        for acc in BANK.accounts:
            result.append({
                "účet": acc.name,
                "typ": acc.type,
                "zůstatek": f"{acc.balance:,.2f} {acc.currency}",
                "IBAN": acc.iban
            })
            if acc.currency == "CZK":
                total_czk += acc.balance
            else:
                total_czk += acc.balance * 25.2  # přibližný kurz
        result.append({"celkem_v_CZK": f"{total_czk:,.2f} CZK"})
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "get_transactions":
        days = params.get("days", 30)
        category = params.get("category")
        min_amount = params.get("min_amount")
        max_amount = params.get("max_amount")

        cutoff = datetime.now() - timedelta(days=days)
        filtered = []

        for txn in BANK.transactions:
            txn_date = datetime.strptime(txn.date, "%Y-%m-%d")
            if txn_date < cutoff:
                continue
            if category and txn.category != category:
                continue
            if min_amount and txn.amount < min_amount:
                continue
            if max_amount and txn.amount > max_amount:
                continue
            filtered.append({
                "datum": txn.date,
                "částka": f"{txn.amount:,.2f} CZK",
                "kategorie": txn.category,
                "obchodník": txn.merchant
            })

        return json.dumps(filtered[:20], ensure_ascii=False, indent=2)  # max 20

    elif name == "analyze_spending":
        days = params.get("days", 30)
        cutoff = datetime.now() - timedelta(days=days)

        categories = {}
        total_expense = 0
        total_income = 0

        for txn in BANK.transactions:
            txn_date = datetime.strptime(txn.date, "%Y-%m-%d")
            if txn_date < cutoff:
                continue

            if txn.amount < 0:
                total_expense += abs(txn.amount)
                if txn.category not in categories:
                    categories[txn.category] = 0
                categories[txn.category] += abs(txn.amount)
            else:
                total_income += txn.amount

        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)

        result = {
            "období": f"posledních {days} dní",
            "celkové_výdaje": f"{total_expense:,.2f} CZK",
            "celkové_příjmy": f"{total_income:,.2f} CZK",
            "bilance": f"{total_income - total_expense:,.2f} CZK",
            "průměrné_denní_výdaje": f"{total_expense/days:,.2f} CZK",
            "výdaje_podle_kategorií": {
                cat: f"{amt:,.2f} CZK ({100*amt/total_expense:.1f}%)"
                for cat, amt in sorted_cats
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "detect_anomalies":
        sensitivity = params.get("sensitivity", "medium")
        thresholds = {"low": 10000, "medium": 5000, "high": 2000}
        threshold = thresholds[sensitivity]

        anomalies = []
        for txn in BANK.transactions[:60]:  # posledních 60 transakcí
            if abs(txn.amount) > threshold:
                anomalies.append({
                    "datum": txn.date,
                    "částka": f"{txn.amount:,.2f} CZK",
                    "obchodník": txn.merchant,
                    "důvod": "Vysoká částka"
                })

        # Detekce opakovaných plateb
        merchants_count = {}
        for txn in BANK.transactions[:30]:
            if txn.merchant not in merchants_count:
                merchants_count[txn.merchant] = 0
            merchants_count[txn.merchant] += 1

        for merchant, count in merchants_count.items():
            if count >= 5:
                anomalies.append({
                    "obchodník": merchant,
                    "počet_transakcí": count,
                    "důvod": "Časté opakované platby"
                })

        return json.dumps(anomalies[:10], ensure_ascii=False, indent=2)

    elif name == "get_spending_by_merchant":
        days = params.get("days", 30)
        limit = params.get("limit", 10)
        cutoff = datetime.now() - timedelta(days=days)

        merchants = {}
        for txn in BANK.transactions:
            txn_date = datetime.strptime(txn.date, "%Y-%m-%d")
            if txn_date < cutoff or txn.amount >= 0:
                continue
            if txn.merchant not in merchants:
                merchants[txn.merchant] = {"celkem": 0, "počet": 0}
            merchants[txn.merchant]["celkem"] += abs(txn.amount)
            merchants[txn.merchant]["počet"] += 1

        sorted_merchants = sorted(merchants.items(), key=lambda x: x[1]["celkem"], reverse=True)

        result = [
            {
                "obchodník": m,
                "celkem": f"{data['celkem']:,.2f} CZK",
                "počet_transakcí": data["počet"]
            }
            for m, data in sorted_merchants[:limit]
        ]
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "calculate_savings_potential":
        # Analyzujeme zbytné výdaje
        zbytne = ["zábava", "restaurace"]
        mesic1 = datetime.now() - timedelta(days=30)
        mesic2 = datetime.now() - timedelta(days=60)

        zbytne_vydaje = 0
        celkove_vydaje = 0

        for txn in BANK.transactions:
            txn_date = datetime.strptime(txn.date, "%Y-%m-%d")
            if txn_date < mesic1 or txn.amount >= 0:
                continue
            celkove_vydaje += abs(txn.amount)
            if txn.category in zbytne:
                zbytne_vydaje += abs(txn.amount)

        result = {
            "zbytné_výdaje_měsíčně": f"{zbytne_vydaje:,.2f} CZK",
            "procento_zbytných": f"{100*zbytne_vydaje/celkove_vydaje:.1f}%",
            "potenciální_měsíční_úspora": f"{zbytne_vydaje * 0.3:,.2f} CZK",
            "potenciální_roční_úspora": f"{zbytne_vydaje * 0.3 * 12:,.2f} CZK",
            "doporučení": [
                "Snížit návštěvy restaurací o 30%",
                "Přehodnotit předplatné streamovacích služeb",
                "Nakupovat potraviny s nákupním seznamem"
            ]
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "generate_monthly_report":
        month = params.get("month", datetime.now().month)
        year = params.get("year", datetime.now().year)

        result = {
            "report": f"Měsíční finanční report {month}/{year}",
            "═══════════════════════════════════════": "",
            "příjmy": "65,000.00 CZK",
            "výdaje": "42,350.00 CZK",
            "úspory": "22,650.00 CZK",
            "míra_úspor": "34.8%",
            "───────────────────────────────────────": "",
            "top_kategorie": {
                "1": "Bydlení: 12,500 CZK (29.5%)",
                "2": "Potraviny: 8,200 CZK (19.4%)",
                "3": "Doprava: 5,800 CZK (13.7%)"
            },
            "hodnocení": "⭐⭐⭐⭐ Dobrý měsíc",
            "tip": "Udržujte současný trend, máte zdravou míru úspor!"
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    return json.dumps({"error": f"Neznámý nástroj: {name}"})

# ═══════════════════════════════════════════════════════════════════════════════
# 🤖 ReACT AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class BankingAgent:
    """
    ReACT Agent pro bankovní analýzy

    ReACT = Reasoning + Acting + Observing

    Agent v cyklu:
    1. MYSLÍ - analyzuje situaci a plánuje další krok
    2. JEDNÁ - volá nástroj pro získání dat
    3. POZORUJE - zpracovává výsledky
    4. Opakuje dokud nemá odpověď
    """

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.max_iterations = 10

    def run(self, user_query: str) -> str:
        """Spustí ReACT loop pro zodpovězení dotazu"""

        print_header(f"🏦 Bankovní Agent - ReACT")
        print(f"{Colors.BOLD}Dotaz:{Colors.ENDC} {user_query}\n")
        print(f"{Colors.DIM}{'─' * 60}{Colors.ENDC}")

        messages = [
            {"role": "user", "content": user_query}
        ]

        system_prompt = """Jsi inteligentní bankovní asistent. Analyzuješ finanční data uživatele a poskytueš užitečné rady.

Tvůj postup (ReACT pattern):
1. MYŠLENÍ: Nejprve si promysli, jaké informace potřebuješ
2. AKCE: Zavolej vhodný nástroj pro získání dat
3. POZOROVÁNÍ: Analyzuj výsledky
4. Opakuj dokud nemáš dostatek informací pro kvalitní odpověď

Odpovídej česky. Buď konkrétní a používej čísla z dat. Když máš dostatek informací, poskytni jasnou a užitečnou odpověď."""

        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n{Colors.DIM}[Iterace {iteration}/{self.max_iterations}]{Colors.ENDC}")

            # Volání Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                tools=TOOLS,
                messages=messages
            )

            # Zpracování odpovědi
            assistant_content = []
            has_tool_use = False
            final_text = ""

            for block in response.content:
                if block.type == "text":
                    final_text = block.text
                    if response.stop_reason != "tool_use":
                        print_thought(block.text[:200] + "..." if len(block.text) > 200 else block.text)
                    assistant_content.append({"type": "text", "text": block.text})

                elif block.type == "tool_use":
                    has_tool_use = True
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id

                    print_action(tool_name, json.dumps(tool_input, ensure_ascii=False))

                    # Spuštění nástroje
                    result = execute_tool(tool_name, tool_input)
                    print_observation(result)

                    assistant_content.append({
                        "type": "tool_use",
                        "id": tool_id,
                        "name": tool_name,
                        "input": tool_input
                    })

                    # Přidání výsledku do konverzace
                    messages.append({"role": "assistant", "content": assistant_content})
                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": result
                        }]
                    })
                    assistant_content = []

            # Pokud není další tool call, máme finální odpověď
            if not has_tool_use:
                print_answer(final_text)
                return final_text

        return "Dosažen maximální počet iterací bez výsledku."

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 HLAVNÍ PROGRAM
# ═══════════════════════════════════════════════════════════════════════════════

def print_tools_sidebar():
    """Zobrazí boční panel s dostupnými nástroji"""
    print(f"""
{Colors.BOLD}{Colors.BLUE}╔══════════════════════════════════════════╗
║        🔧 DOSTUPNÉ NÁSTROJE              ║
╠══════════════════════════════════════════╣
║                                          ║
║  📊 get_account_balances                 ║
║     └─ Přehled účtů a zůstatků           ║
║                                          ║
║  💳 get_transactions                     ║
║     └─ Seznam transakcí s filtry         ║
║                                          ║
║  📈 analyze_spending                     ║
║     └─ Analýza výdajů podle kategorií    ║
║                                          ║
║  🚨 detect_anomalies                     ║
║     └─ Detekce podezřelých transakcí     ║
║                                          ║
║  🏪 get_spending_by_merchant             ║
║     └─ Výdaje podle obchodníků           ║
║                                          ║
║  💰 calculate_savings_potential          ║
║     └─ Potenciál úspor                   ║
║                                          ║
║  📋 generate_monthly_report              ║
║     └─ Měsíční finanční report           ║
║                                          ║
╚══════════════════════════════════════════╝{Colors.ENDC}
""")

def main():
    # Zde vložte svůj Anthropic API klíč
    API_KEY = "VLOŽTE_VÁŠ_API_KLÍČ"

    if API_KEY == "VLOŽTE_VÁŠ_API_KLÍČ":
        print_error("Prosím vložte svůj Anthropic API klíč do proměnné API_KEY")
        return

    print_tools_sidebar()

    agent = BankingAgent(API_KEY)

    # Ukázkové dotazy
    demo_queries = [
        "Kolik mám peněz na účtech a jaké jsou mé největší výdaje za poslední měsíc?",
        "Najdi podezřelé transakce a řekni mi, kde utrácím nejvíce.",
        "Jaký je můj potenciál úspor? Kde bych mohl šetřit?",
    ]

    print(f"\n{Colors.BOLD}Ukázkové dotazy:{Colors.ENDC}")
    for i, q in enumerate(demo_queries, 1):
        print(f"  {i}. {q}")

    print(f"\n{Colors.BOLD}Zadejte svůj dotaz (nebo číslo ukázky, 'q' pro ukončení):{Colors.ENDC}")

    while True:
        try:
            user_input = input(f"\n{Colors.CYAN}> {Colors.ENDC}").strip()

            if user_input.lower() == 'q':
                print("Nashledanou! 👋")
                break

            if user_input in ['1', '2', '3']:
                query = demo_queries[int(user_input) - 1]
            else:
                query = user_input

            if query:
                agent.run(query)

        except KeyboardInterrupt:
            print("\n\nPřerušeno uživatelem.")
            break
        except Exception as e:
            print_error(str(e))

if __name__ == "__main__":
    main()
