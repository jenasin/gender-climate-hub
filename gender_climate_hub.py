#!/usr/bin/env python3
"""
🌍 Gender & Climate Intelligence Hub
=====================================
Komplexní ReACT agent s napojením na více datových zdrojů (bank)
pro holistickou analýzu genderově responzivních klimatických politik.

DATOVÉ ZDROJE (BANKY):
━━━━━━━━━━━━━━━━━━━━━━
🏛️ UN Women Climate Scorecard  - Genderové dimenze klimatických politik
📊 World Bank Gender Data       - Ekonomické indikátory, zaměstnanost, vzdělání
🎯 UNDP Human Development       - HDI, Gender Inequality Index, MPI
🌡️ Climate Watch               - NDC, emise, klimatické závazky
🏥 WHO Health Data             - Zdravotní indikátory, mateřská úmrtnost
👷 ILO Labour Statistics       - Pracovní trh, neplacená práce, mzdy

Pro článek o AI agentech využívajících multiple data sources.
"""

import anthropic
import json
import os
from dataclasses import dataclass, field
from typing import Any, Optional
from abc import ABC, abstractmethod
import random
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 UI KOMPONENTY
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[35m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Barvy pro jednotlivé banky
    UNWOMEN = '\033[38;5;205m'    # Růžová
    WORLDBANK = '\033[38;5;33m'   # Modrá
    UNDP = '\033[38;5;39m'        # Světle modrá
    CLIMATE = '\033[38;5;34m'     # Zelená
    WHO = '\033[38;5;75m'         # Světle modrá
    ILO = '\033[38;5;208m'        # Oranžová

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'═' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}  {text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'═' * 80}{Colors.ENDC}\n")

def print_bank_badge(bank_name: str, color: str):
    print(f"{color}[{bank_name}]{Colors.ENDC}", end=" ")

def print_thought(text: str):
    print(f"{Colors.YELLOW}💭 REASONING:{Colors.ENDC} {text}")

def print_action(tool: str, params: str, bank: str = None):
    bank_colors = {
        "UN Women": Colors.UNWOMEN,
        "World Bank": Colors.WORLDBANK,
        "UNDP": Colors.UNDP,
        "Climate Watch": Colors.CLIMATE,
        "WHO": Colors.WHO,
        "ILO": Colors.ILO,
    }
    if bank:
        color = bank_colors.get(bank, Colors.CYAN)
        print(f"{Colors.CYAN}⚡ ACTION:{Colors.ENDC} {color}[{bank}]{Colors.ENDC} {tool}")
    else:
        print(f"{Colors.CYAN}⚡ ACTION:{Colors.ENDC} {tool}")
    print(f"{Colors.DIM}   └─ params: {params}{Colors.ENDC}")

def print_observation(text: str):
    print(f"{Colors.GREEN}👁️ OBSERVATION:{Colors.ENDC}")
    lines = text.split('\n')
    for line in lines[:12]:
        print(f"   {line}")
    if len(lines) > 12:
        print(f"   {Colors.DIM}... (+{len(lines)-12} lines){Colors.ENDC}")

def print_answer(text: str):
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'─' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}✅ FINAL ANSWER:{Colors.ENDC}")
    print(f"{Colors.GREEN}{'─' * 80}{Colors.ENDC}")
    print(f"{text}")

def print_error(text: str):
    print(f"{Colors.RED}❌ ERROR: {text}{Colors.ENDC}")

# ═══════════════════════════════════════════════════════════════════════════════
# 🏛️ DATOVÉ BANKY - ABSTRAKTNÍ VRSTVA
# ═══════════════════════════════════════════════════════════════════════════════

class DataBank(ABC):
    """Abstraktní třída pro datovou banku"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def icon(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def get_country_data(self, country_code: str) -> dict:
        pass

    @abstractmethod
    def get_indicator(self, indicator: str, country_code: str = None) -> dict:
        pass

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 SPOLEČNÁ DATA - ZEMĚ
# ═══════════════════════════════════════════════════════════════════════════════

COUNTRIES = {
    "BRA": {"name": "Brazílie", "name_en": "Brazil", "region": "South America", "income": "upper_middle", "population": 215},
    "IND": {"name": "Indie", "name_en": "India", "region": "South Asia", "income": "lower_middle", "population": 1420},
    "KEN": {"name": "Keňa", "name_en": "Kenya", "region": "East Africa", "income": "lower_middle", "population": 54},
    "SWE": {"name": "Švédsko", "name_en": "Sweden", "region": "Europe", "income": "high", "population": 10},
    "DEU": {"name": "Německo", "name_en": "Germany", "region": "Europe", "income": "high", "population": 84},
    "JPN": {"name": "Japonsko", "name_en": "Japan", "region": "East Asia", "income": "high", "population": 125},
    "NGA": {"name": "Nigérie", "name_en": "Nigeria", "region": "West Africa", "income": "lower_middle", "population": 218},
    "ZAF": {"name": "JAR", "name_en": "South Africa", "region": "Southern Africa", "income": "upper_middle", "population": 60},
    "MEX": {"name": "Mexiko", "name_en": "Mexico", "region": "North America", "income": "upper_middle", "population": 128},
    "IDN": {"name": "Indonésie", "name_en": "Indonesia", "region": "Southeast Asia", "income": "upper_middle", "population": 275},
    "BGD": {"name": "Bangladéš", "name_en": "Bangladesh", "region": "South Asia", "income": "lower_middle", "population": 170},
    "ETH": {"name": "Etiopie", "name_en": "Ethiopia", "region": "East Africa", "income": "low", "population": 120},
    "PHL": {"name": "Filipíny", "name_en": "Philippines", "region": "Southeast Asia", "income": "lower_middle", "population": 115},
    "VNM": {"name": "Vietnam", "name_en": "Vietnam", "region": "Southeast Asia", "income": "lower_middle", "population": 98},
    "COL": {"name": "Kolumbie", "name_en": "Colombia", "region": "South America", "income": "upper_middle", "population": 52},
    "CAN": {"name": "Kanada", "name_en": "Canada", "region": "North America", "income": "high", "population": 39},
    "NZL": {"name": "Nový Zéland", "name_en": "New Zealand", "region": "Pacific", "income": "high", "population": 5},
    "CHL": {"name": "Chile", "name_en": "Chile", "region": "South America", "income": "high", "population": 19},
    "RWA": {"name": "Rwanda", "name_en": "Rwanda", "region": "East Africa", "income": "low", "population": 13},
    "NPL": {"name": "Nepál", "name_en": "Nepal", "region": "South Asia", "income": "lower_middle", "population": 30},
    "GHA": {"name": "Ghana", "name_en": "Ghana", "region": "West Africa", "income": "lower_middle", "population": 33},
    "PER": {"name": "Peru", "name_en": "Peru", "region": "South America", "income": "upper_middle", "population": 34},
    "CRI": {"name": "Kostarika", "name_en": "Costa Rica", "region": "Central America", "income": "upper_middle", "population": 5},
    "FJI": {"name": "Fidži", "name_en": "Fiji", "region": "Pacific", "income": "upper_middle", "population": 0.9},
    "MWI": {"name": "Malawi", "name_en": "Malawi", "region": "Southern Africa", "income": "low", "population": 20},
}

def find_country(query: str) -> tuple[str, dict] | tuple[None, None]:
    """Najde zemi podle názvu nebo kódu"""
    q = query.lower().strip()
    for code, data in COUNTRIES.items():
        if q in [code.lower(), data["name"].lower(), data["name_en"].lower()]:
            return code, data
    # Částečná shoda
    for code, data in COUNTRIES.items():
        if q in data["name"].lower() or q in data["name_en"].lower():
            return code, data
    return None, None

# ═══════════════════════════════════════════════════════════════════════════════
# 🏛️ BANKA 1: UN WOMEN CLIMATE SCORECARD
# ═══════════════════════════════════════════════════════════════════════════════

class UNWomenBank(DataBank):
    name = "UN Women Climate Scorecard"
    icon = "🏛️"
    description = "Genderové dimenze klimatických politik - 6 dimenzí, 50+ indikátorů"

    DIMENSIONS = {
        "economic_security": "Ekonomická bezpečnost",
        "unpaid_care": "Neplacená péče",
        "gender_based_violence": "Genderově založené násilí",
        "health": "Zdraví",
        "participation": "Účast a lídrovství",
        "gender_mainstreaming": "Gender mainstreaming"
    }

    def __init__(self):
        self.data = self._generate_data()

    def _generate_data(self) -> dict:
        data = {}
        for code in COUNTRIES:
            base = {"high": 70, "upper_middle": 55, "lower_middle": 45, "low": 38}[COUNTRIES[code]["income"]]
            dims = {d: min(100, max(0, base + random.uniform(-15, 20))) for d in self.DIMENSIONS}
            data[code] = {
                "overall_score": round(sum(dims.values()) / len(dims), 1),
                "dimensions": {k: round(v, 1) for k, v in dims.items()},
                "women_in_delegation": round(random.uniform(18, 52), 1),
                "has_gender_focal_point": random.random() > 0.35,
                "ndc_gender_references": random.randint(5, 45),
            }
        return data

    def get_country_data(self, country_code: str) -> dict:
        if country_code not in self.data:
            return {"error": "Country not found"}
        d = self.data[country_code]
        return {
            "source": self.name,
            "country": COUNTRIES[country_code]["name"],
            "overall_score": f"{d['overall_score']}/100",
            "dimensions": {self.DIMENSIONS[k]: f"{v}/100" for k, v in d["dimensions"].items()},
            "women_in_climate_delegation": f"{d['women_in_delegation']}%",
            "gender_focal_point": "✅" if d["has_gender_focal_point"] else "❌",
            "ndc_gender_references": d["ndc_gender_references"],
        }

    def get_indicator(self, indicator: str, country_code: str = None) -> dict:
        if indicator == "dimension_ranking":
            rankings = {}
            for dim in self.DIMENSIONS:
                sorted_c = sorted(self.data.items(), key=lambda x: x[1]["dimensions"][dim], reverse=True)
                rankings[self.DIMENSIONS[dim]] = [
                    {"rank": i+1, "country": COUNTRIES[c]["name"], "score": f"{d['dimensions'][dim]}/100"}
                    for i, (c, d) in enumerate(sorted_c[:5])
                ]
            return {"source": self.name, "dimension_rankings": rankings}

        if indicator == "global_average":
            avgs = {dim: sum(d["dimensions"][dim] for d in self.data.values()) / len(self.data)
                   for dim in self.DIMENSIONS}
            return {
                "source": self.name,
                "global_averages": {self.DIMENSIONS[k]: f"{v:.1f}/100" for k, v in avgs.items()}
            }

        return {"error": f"Indicator '{indicator}' not found"}

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 BANKA 2: WORLD BANK GENDER DATA
# ═══════════════════════════════════════════════════════════════════════════════

class WorldBankGenderBank(DataBank):
    name = "World Bank Gender Data"
    icon = "📊"
    description = "Ekonomické genderové indikátory - zaměstnanost, vzdělání, přístup k financím"

    def __init__(self):
        self.data = self._generate_data()

    def _generate_data(self) -> dict:
        data = {}
        for code, info in COUNTRIES.items():
            base_female_labor = {"high": 65, "upper_middle": 52, "lower_middle": 35, "low": 28}[info["income"]]
            data[code] = {
                "female_labor_force_participation": round(base_female_labor + random.uniform(-10, 15), 1),
                "gender_wage_gap": round(random.uniform(10, 35), 1),  # %
                "female_account_ownership": round(random.uniform(30, 90), 1),  # %
                "female_secondary_education": round(random.uniform(40, 98), 1),  # %
                "female_tertiary_education": round(random.uniform(15, 70), 1),  # %
                "women_in_parliament": round(random.uniform(8, 48), 1),  # %
                "female_land_ownership": round(random.uniform(5, 45), 1),  # %
                "female_entrepreneurship": round(random.uniform(15, 40), 1),  # %
            }
        return data

    def get_country_data(self, country_code: str) -> dict:
        if country_code not in self.data:
            return {"error": "Country not found"}
        d = self.data[country_code]
        return {
            "source": self.name,
            "country": COUNTRIES[country_code]["name"],
            "labor_force": {
                "female_participation": f"{d['female_labor_force_participation']}%",
                "gender_wage_gap": f"{d['gender_wage_gap']}%",
            },
            "education": {
                "female_secondary": f"{d['female_secondary_education']}%",
                "female_tertiary": f"{d['female_tertiary_education']}%",
            },
            "economic_empowerment": {
                "account_ownership": f"{d['female_account_ownership']}%",
                "land_ownership": f"{d['female_land_ownership']}%",
                "entrepreneurship_rate": f"{d['female_entrepreneurship']}%",
            },
            "political": {
                "women_in_parliament": f"{d['women_in_parliament']}%",
            }
        }

    def get_indicator(self, indicator: str, country_code: str = None) -> dict:
        valid_indicators = list(self.data[list(self.data.keys())[0]].keys())
        if indicator not in valid_indicators:
            return {"error": f"Invalid indicator. Valid: {valid_indicators}"}

        sorted_data = sorted(self.data.items(), key=lambda x: x[1][indicator], reverse=True)
        return {
            "source": self.name,
            "indicator": indicator,
            "ranking": [
                {"rank": i+1, "country": COUNTRIES[c]["name"], "value": f"{d[indicator]}%"}
                for i, (c, d) in enumerate(sorted_data[:10])
            ],
            "global_average": f"{sum(d[indicator] for d in self.data.values()) / len(self.data):.1f}%"
        }

# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 BANKA 3: UNDP HUMAN DEVELOPMENT
# ═══════════════════════════════════════════════════════════════════════════════

class UNDPBank(DataBank):
    name = "UNDP Human Development"
    icon = "🎯"
    description = "Human Development Index, Gender Inequality Index, Multidimensional Poverty"

    def __init__(self):
        self.data = self._generate_data()

    def _generate_data(self) -> dict:
        data = {}
        for code, info in COUNTRIES.items():
            base_hdi = {"high": 0.92, "upper_middle": 0.76, "lower_middle": 0.62, "low": 0.48}[info["income"]]
            hdi = min(1.0, max(0.3, base_hdi + random.uniform(-0.08, 0.08)))
            gii = 1 - hdi + random.uniform(-0.1, 0.15)  # Higher HDI → lower inequality
            data[code] = {
                "hdi": round(hdi, 3),
                "hdi_rank": 0,  # Will be calculated
                "gender_inequality_index": round(max(0.05, min(0.7, gii)), 3),
                "gender_development_index": round(hdi * (1 - gii/2), 3),
                "mpi_headcount": round(max(0, (1 - hdi) * 60 + random.uniform(-10, 10)), 1),  # %
                "life_expectancy_female": round(70 + hdi * 15 + random.uniform(-3, 3), 1),
                "expected_schooling_female": round(8 + hdi * 8 + random.uniform(-1, 1), 1),
                "gni_per_capita_female": round(5000 + hdi * 45000 + random.uniform(-5000, 5000), 0),
            }

        # Calculate HDI ranks
        sorted_by_hdi = sorted(data.items(), key=lambda x: x[1]["hdi"], reverse=True)
        for i, (code, _) in enumerate(sorted_by_hdi):
            data[code]["hdi_rank"] = i + 1

        return data

    def get_country_data(self, country_code: str) -> dict:
        if country_code not in self.data:
            return {"error": "Country not found"}
        d = self.data[country_code]
        return {
            "source": self.name,
            "country": COUNTRIES[country_code]["name"],
            "human_development": {
                "hdi": d["hdi"],
                "hdi_rank": f"#{d['hdi_rank']} of {len(self.data)}",
                "category": "Very High" if d["hdi"] >= 0.8 else "High" if d["hdi"] >= 0.7 else "Medium" if d["hdi"] >= 0.55 else "Low"
            },
            "gender_indices": {
                "gender_inequality_index": d["gender_inequality_index"],
                "gender_development_index": d["gender_development_index"],
            },
            "poverty": {
                "mpi_headcount": f"{d['mpi_headcount']}%",
            },
            "female_indicators": {
                "life_expectancy": f"{d['life_expectancy_female']} years",
                "expected_schooling": f"{d['expected_schooling_female']} years",
                "gni_per_capita": f"${d['gni_per_capita_female']:,.0f}",
            }
        }

    def get_indicator(self, indicator: str, country_code: str = None) -> dict:
        if indicator == "gii_ranking":
            sorted_data = sorted(self.data.items(), key=lambda x: x[1]["gender_inequality_index"])
            return {
                "source": self.name,
                "indicator": "Gender Inequality Index (lower is better)",
                "ranking": [
                    {"rank": i+1, "country": COUNTRIES[c]["name"], "gii": d["gender_inequality_index"]}
                    for i, (c, d) in enumerate(sorted_data[:10])
                ]
            }
        return {"error": "Invalid indicator"}

# ═══════════════════════════════════════════════════════════════════════════════
# 🌡️ BANKA 4: CLIMATE WATCH
# ═══════════════════════════════════════════════════════════════════════════════

class ClimateWatchBank(DataBank):
    name = "Climate Watch"
    icon = "🌡️"
    description = "NDC commitments, emissions data, climate targets, adaptation plans"

    def __init__(self):
        self.data = self._generate_data()

    def _generate_data(self) -> dict:
        data = {}
        for code, info in COUNTRIES.items():
            pop = info["population"]
            base_emissions = {"high": 8, "upper_middle": 5, "lower_middle": 2, "low": 0.5}[info["income"]]
            data[code] = {
                "total_emissions_mtco2": round(pop * base_emissions * random.uniform(0.7, 1.3), 1),
                "emissions_per_capita": round(base_emissions * random.uniform(0.8, 1.2), 2),
                "ndc_target_2030": f"-{random.randint(25, 55)}%",
                "ndc_year": random.choice([2021, 2022, 2023, 2024]),
                "has_net_zero_target": random.random() > 0.4,
                "net_zero_year": random.choice([2050, 2060, 2070]) if random.random() > 0.4 else None,
                "adaptation_plan": random.random() > 0.5,
                "climate_vulnerability_index": round(random.uniform(0.2, 0.8), 2),
                "renewable_energy_share": round(random.uniform(5, 65), 1),
                "climate_finance_received_musd": round(random.uniform(10, 2000), 0) if info["income"] != "high" else 0,
            }
        return data

    def get_country_data(self, country_code: str) -> dict:
        if country_code not in self.data:
            return {"error": "Country not found"}
        d = self.data[country_code]
        return {
            "source": self.name,
            "country": COUNTRIES[country_code]["name"],
            "emissions": {
                "total_mtco2": f"{d['total_emissions_mtco2']} Mt CO2e",
                "per_capita": f"{d['emissions_per_capita']} t CO2e",
            },
            "ndc_commitments": {
                "2030_target": d["ndc_target_2030"],
                "ndc_submission_year": d["ndc_year"],
                "net_zero_target": f"Yes ({d['net_zero_year']})" if d["has_net_zero_target"] else "No",
            },
            "adaptation": {
                "national_adaptation_plan": "✅" if d["adaptation_plan"] else "❌",
                "vulnerability_index": d["climate_vulnerability_index"],
            },
            "energy_and_finance": {
                "renewable_share": f"{d['renewable_energy_share']}%",
                "climate_finance_received": f"${d['climate_finance_received_musd']}M" if d["climate_finance_received_musd"] > 0 else "N/A (donor)",
            }
        }

    def get_indicator(self, indicator: str, country_code: str = None) -> dict:
        if indicator == "emissions_ranking":
            sorted_data = sorted(self.data.items(), key=lambda x: x[1]["total_emissions_mtco2"], reverse=True)
            return {
                "source": self.name,
                "indicator": "Total Emissions (highest first)",
                "ranking": [
                    {"rank": i+1, "country": COUNTRIES[c]["name"], "emissions": f"{d['total_emissions_mtco2']} Mt CO2e"}
                    for i, (c, d) in enumerate(sorted_data[:10])
                ]
            }
        if indicator == "vulnerability_ranking":
            sorted_data = sorted(self.data.items(), key=lambda x: x[1]["climate_vulnerability_index"], reverse=True)
            return {
                "source": self.name,
                "indicator": "Climate Vulnerability (most vulnerable first)",
                "ranking": [
                    {"rank": i+1, "country": COUNTRIES[c]["name"], "vulnerability": d["climate_vulnerability_index"]}
                    for i, (c, d) in enumerate(sorted_data[:10])
                ]
            }
        return {"error": "Invalid indicator"}

# ═══════════════════════════════════════════════════════════════════════════════
# 🏥 BANKA 5: WHO HEALTH DATA
# ═══════════════════════════════════════════════════════════════════════════════

class WHOBank(DataBank):
    name = "WHO Health Data"
    icon = "🏥"
    description = "Zdravotní indikátory se zaměřením na ženy - mateřská úmrtnost, reprodukční zdraví"

    def __init__(self):
        self.data = self._generate_data()

    def _generate_data(self) -> dict:
        data = {}
        for code, info in COUNTRIES.items():
            base_mmr = {"high": 8, "upper_middle": 45, "lower_middle": 150, "low": 400}[info["income"]]
            data[code] = {
                "maternal_mortality_ratio": round(base_mmr * random.uniform(0.6, 1.4)),  # per 100k
                "skilled_birth_attendance": round(min(100, 100 - base_mmr/5 + random.uniform(-5, 10)), 1),
                "contraceptive_prevalence": round(random.uniform(25, 80), 1),
                "antenatal_care_coverage": round(random.uniform(50, 98), 1),
                "adolescent_birth_rate": round(random.uniform(5, 120), 1),  # per 1000
                "female_hiv_prevalence": round(random.uniform(0.1, 8), 2) if info["region"] in ["East Africa", "Southern Africa", "West Africa"] else round(random.uniform(0.05, 0.5), 2),
                "uhc_service_coverage_index": round(random.uniform(35, 85), 0),
                "heat_wave_mortality_female": round(random.uniform(0.5, 15), 1),  # per 100k
            }
        return data

    def get_country_data(self, country_code: str) -> dict:
        if country_code not in self.data:
            return {"error": "Country not found"}
        d = self.data[country_code]
        return {
            "source": self.name,
            "country": COUNTRIES[country_code]["name"],
            "maternal_health": {
                "maternal_mortality_ratio": f"{d['maternal_mortality_ratio']} per 100,000 live births",
                "skilled_birth_attendance": f"{d['skilled_birth_attendance']}%",
                "antenatal_care": f"{d['antenatal_care_coverage']}%",
            },
            "reproductive_health": {
                "contraceptive_prevalence": f"{d['contraceptive_prevalence']}%",
                "adolescent_birth_rate": f"{d['adolescent_birth_rate']} per 1,000",
            },
            "climate_health_nexus": {
                "heat_wave_mortality_female": f"{d['heat_wave_mortality_female']} per 100,000",
            },
            "health_system": {
                "uhc_coverage_index": d["uhc_service_coverage_index"],
            }
        }

    def get_indicator(self, indicator: str, country_code: str = None) -> dict:
        if indicator == "maternal_mortality_ranking":
            sorted_data = sorted(self.data.items(), key=lambda x: x[1]["maternal_mortality_ratio"])
            return {
                "source": self.name,
                "indicator": "Maternal Mortality Ratio (best first)",
                "ranking": [
                    {"rank": i+1, "country": COUNTRIES[c]["name"], "mmr": f"{d['maternal_mortality_ratio']} per 100k"}
                    for i, (c, d) in enumerate(sorted_data[:10])
                ]
            }
        return {"error": "Invalid indicator"}

# ═══════════════════════════════════════════════════════════════════════════════
# 👷 BANKA 6: ILO LABOUR STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

class ILOBank(DataBank):
    name = "ILO Labour Statistics"
    icon = "👷"
    description = "Pracovní trh, neplacená práce, zelená zaměstnanost, pracovní podmínky"

    def __init__(self):
        self.data = self._generate_data()

    def _generate_data(self) -> dict:
        data = {}
        for code, info in COUNTRIES.items():
            data[code] = {
                "female_unemployment": round(random.uniform(3, 25), 1),
                "youth_female_neet": round(random.uniform(8, 45), 1),  # Not in Education, Employment, Training
                "unpaid_care_hours_female": round(random.uniform(15, 45), 1),  # hours/week
                "unpaid_care_hours_male": round(random.uniform(3, 15), 1),
                "informal_employment_female": round(random.uniform(15, 85), 1),
                "green_jobs_female_share": round(random.uniform(15, 45), 1),
                "female_managers_share": round(random.uniform(15, 45), 1),
                "maternity_leave_weeks": random.randint(6, 26),
                "childcare_enrollment_0_3": round(random.uniform(5, 65), 1),
            }
        return data

    def get_country_data(self, country_code: str) -> dict:
        if country_code not in self.data:
            return {"error": "Country not found"}
        d = self.data[country_code]
        care_gap = d["unpaid_care_hours_female"] - d["unpaid_care_hours_male"]
        return {
            "source": self.name,
            "country": COUNTRIES[country_code]["name"],
            "employment": {
                "female_unemployment": f"{d['female_unemployment']}%",
                "youth_female_neet": f"{d['youth_female_neet']}%",
                "informal_employment": f"{d['informal_employment_female']}%",
            },
            "unpaid_care_work": {
                "female_hours_per_week": d["unpaid_care_hours_female"],
                "male_hours_per_week": d["unpaid_care_hours_male"],
                "gender_gap": f"{care_gap:.1f} hours",
            },
            "green_economy": {
                "female_share_green_jobs": f"{d['green_jobs_female_share']}%",
            },
            "work_family_balance": {
                "maternity_leave": f"{d['maternity_leave_weeks']} weeks",
                "childcare_enrollment": f"{d['childcare_enrollment_0_3']}%",
            },
            "leadership": {
                "female_managers": f"{d['female_managers_share']}%",
            }
        }

    def get_indicator(self, indicator: str, country_code: str = None) -> dict:
        if indicator == "care_gap_ranking":
            gaps = {c: d["unpaid_care_hours_female"] - d["unpaid_care_hours_male"] for c, d in self.data.items()}
            sorted_gaps = sorted(gaps.items(), key=lambda x: x[1], reverse=True)
            return {
                "source": self.name,
                "indicator": "Unpaid Care Gap (largest first)",
                "ranking": [
                    {"rank": i+1, "country": COUNTRIES[c]["name"], "gap": f"{gap:.1f} hours/week"}
                    for i, (c, gap) in enumerate(sorted_gaps[:10])
                ]
            }
        if indicator == "green_jobs_ranking":
            sorted_data = sorted(self.data.items(), key=lambda x: x[1]["green_jobs_female_share"], reverse=True)
            return {
                "source": self.name,
                "indicator": "Female Share in Green Jobs",
                "ranking": [
                    {"rank": i+1, "country": COUNTRIES[c]["name"], "share": f"{d['green_jobs_female_share']}%"}
                    for i, (c, d) in enumerate(sorted_data[:10])
                ]
            }
        return {"error": "Invalid indicator"}

# ═══════════════════════════════════════════════════════════════════════════════
# 🔗 DATA HUB - AGREGÁTOR VŠECH BANK
# ═══════════════════════════════════════════════════════════════════════════════

class DataHub:
    """Centrální hub pro všechny datové banky"""

    def __init__(self):
        self.banks = {
            "unwomen": UNWomenBank(),
            "worldbank": WorldBankGenderBank(),
            "undp": UNDPBank(),
            "climate": ClimateWatchBank(),
            "who": WHOBank(),
            "ilo": ILOBank(),
        }

        self.bank_info = {
            "unwomen": {"name": "UN Women Climate Scorecard", "icon": "🏛️", "color": Colors.UNWOMEN},
            "worldbank": {"name": "World Bank Gender Data", "icon": "📊", "color": Colors.WORLDBANK},
            "undp": {"name": "UNDP Human Development", "icon": "🎯", "color": Colors.UNDP},
            "climate": {"name": "Climate Watch", "icon": "🌡️", "color": Colors.CLIMATE},
            "who": {"name": "WHO Health Data", "icon": "🏥", "color": Colors.WHO},
            "ilo": {"name": "ILO Labour Statistics", "icon": "👷", "color": Colors.ILO},
        }

HUB = DataHub()

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 NÁSTROJE PRO AGENTA
# ═══════════════════════════════════════════════════════════════════════════════

TOOLS = [
    {
        "name": "list_data_sources",
        "description": "Zobrazí seznam všech dostupných datových zdrojů (bank) a jejich popis. Volej jako první pro orientaci.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "get_country_profile",
        "description": "Získá kompletní profil země ze VŠECH datových zdrojů najednou. Ideální pro holistický pohled.",
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "Název nebo kód země"}
            },
            "required": ["country"]
        }
    },
    {
        "name": "query_bank",
        "description": "Dotaz na konkrétní datovou banku pro specifická data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bank": {
                    "type": "string",
                    "enum": ["unwomen", "worldbank", "undp", "climate", "who", "ilo"],
                    "description": "ID banky"
                },
                "country": {"type": "string", "description": "Název nebo kód země"},
            },
            "required": ["bank", "country"]
        }
    },
    {
        "name": "get_indicator_ranking",
        "description": "Získá žebříček zemí podle konkrétního indikátoru z vybrané banky.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bank": {
                    "type": "string",
                    "enum": ["unwomen", "worldbank", "undp", "climate", "who", "ilo"]
                },
                "indicator": {
                    "type": "string",
                    "description": "Název indikátoru (např. 'dimension_ranking', 'gii_ranking', 'emissions_ranking', 'maternal_mortality_ranking', 'care_gap_ranking')"
                }
            },
            "required": ["bank", "indicator"]
        }
    },
    {
        "name": "compare_countries",
        "description": "Porovná dvě nebo více zemí napříč vybranými datovými zdroji.",
        "input_schema": {
            "type": "object",
            "properties": {
                "countries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Seznam zemí k porovnání"
                },
                "banks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Seznam bank (nebo prázdné pro všechny)"
                }
            },
            "required": ["countries"]
        }
    },
    {
        "name": "cross_reference_analysis",
        "description": "Provede křížovou analýzu - hledá korelace mezi indikátory z různých bank.",
        "input_schema": {
            "type": "object",
            "properties": {
                "analysis_type": {
                    "type": "string",
                    "enum": ["climate_gender_nexus", "economic_health_link", "care_climate_burden", "vulnerability_inequality"],
                    "description": "Typ křížové analýzy"
                },
                "region": {"type": "string", "description": "Volitelný filtr podle regionu"}
            },
            "required": ["analysis_type"]
        }
    },
    {
        "name": "get_regional_summary",
        "description": "Souhrn indikátorů pro celý region (Afrika, Asie, Latinská Amerika, atd.)",
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "description": "Region (např. 'Africa', 'South Asia', 'Europe', 'South America')"
                }
            },
            "required": ["region"]
        }
    },
    {
        "name": "generate_policy_brief",
        "description": "Vygeneruje policy brief s doporučeními pro konkrétní zemi na základě dat ze všech zdrojů.",
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "Země pro policy brief"}
            },
            "required": ["country"]
        }
    },
    {
        "name": "search_best_practices",
        "description": "Najde země s nejlepšími výsledky v konkrétní oblasti jako inspiraci.",
        "input_schema": {
            "type": "object",
            "properties": {
                "area": {
                    "type": "string",
                    "enum": ["gender_climate_policy", "women_leadership", "care_economy", "green_jobs", "maternal_health", "economic_empowerment"],
                    "description": "Oblast pro hledání best practices"
                }
            },
            "required": ["area"]
        }
    },
    {
        "name": "get_sdg_alignment",
        "description": "Analyzuje soulad země s relevantními SDGs (5, 13, 3, 8).",
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {"type": "string"}
            },
            "required": ["country"]
        }
    }
]

# ═══════════════════════════════════════════════════════════════════════════════
# ⚙️ IMPLEMENTACE NÁSTROJŮ
# ═══════════════════════════════════════════════════════════════════════════════

def execute_tool(name: str, params: dict) -> str:

    if name == "list_data_sources":
        result = {"📚 DOSTUPNÉ DATOVÉ ZDROJE": {}}
        for bank_id, info in HUB.bank_info.items():
            bank = HUB.banks[bank_id]
            result["📚 DOSTUPNÉ DATOVÉ ZDROJE"][f"{info['icon']} {info['name']}"] = {
                "id": bank_id,
                "popis": bank.description
            }
        result["📊 POKRYTÍ"] = f"{len(COUNTRIES)} zemí"
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "get_country_profile":
        code, info = find_country(params["country"])
        if not code:
            return json.dumps({"error": f"Země '{params['country']}' nenalezena"}, ensure_ascii=False)

        result = {
            f"🌍 KOMPLETNÍ PROFIL: {info['name']} ({code})": {
                "region": info["region"],
                "income": info["income"],
                "population": f"{info['population']}M"
            }
        }

        for bank_id, bank in HUB.banks.items():
            bank_info = HUB.bank_info[bank_id]
            result[f"{bank_info['icon']} {bank_info['name']}"] = bank.get_country_data(code)

        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "query_bank":
        bank_id = params["bank"]
        if bank_id not in HUB.banks:
            return json.dumps({"error": f"Neplatná banka: {bank_id}"}, ensure_ascii=False)

        code, _ = find_country(params["country"])
        if not code:
            return json.dumps({"error": f"Země '{params['country']}' nenalezena"}, ensure_ascii=False)

        bank = HUB.banks[bank_id]
        return json.dumps(bank.get_country_data(code), ensure_ascii=False, indent=2)

    elif name == "get_indicator_ranking":
        bank_id = params["bank"]
        if bank_id not in HUB.banks:
            return json.dumps({"error": f"Neplatná banka: {bank_id}"}, ensure_ascii=False)

        bank = HUB.banks[bank_id]
        return json.dumps(bank.get_indicator(params["indicator"]), ensure_ascii=False, indent=2)

    elif name == "compare_countries":
        countries = params["countries"]
        banks_to_use = params.get("banks", list(HUB.banks.keys()))

        codes = []
        for c in countries:
            code, _ = find_country(c)
            if code:
                codes.append(code)

        if len(codes) < 2:
            return json.dumps({"error": "Potřeba alespoň 2 platné země"}, ensure_ascii=False)

        result = {"🔄 POROVNÁNÍ ZEMÍ": [COUNTRIES[c]["name"] for c in codes]}

        for bank_id in banks_to_use:
            if bank_id not in HUB.banks:
                continue
            bank = HUB.banks[bank_id]
            bank_info = HUB.bank_info[bank_id]
            result[f"{bank_info['icon']} {bank_info['name']}"] = {
                COUNTRIES[code]["name"]: bank.get_country_data(code)
                for code in codes
            }

        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "cross_reference_analysis":
        analysis_type = params["analysis_type"]
        region_filter = params.get("region", "").lower()

        countries_to_analyze = COUNTRIES.keys()
        if region_filter:
            countries_to_analyze = [c for c in countries_to_analyze if region_filter in COUNTRIES[c]["region"].lower()]

        if analysis_type == "climate_gender_nexus":
            # Korelace mezi klimatickou zranitelností a gender inequality
            data_points = []
            for code in countries_to_analyze:
                climate_vuln = HUB.banks["climate"].data[code]["climate_vulnerability_index"]
                gender_score = HUB.banks["unwomen"].data[code]["overall_score"]
                data_points.append({
                    "country": COUNTRIES[code]["name"],
                    "climate_vulnerability": climate_vuln,
                    "gender_climate_score": gender_score,
                    "correlation_note": "High vulnerability + Low score = Critical"
                })

            # Sort by vulnerability
            data_points.sort(key=lambda x: x["climate_vulnerability"], reverse=True)

            result = {
                "🔗 KŘÍŽOVÁ ANALÝZA: Climate-Gender Nexus": {
                    "metodologie": "Korelace klimatické zranitelnosti a genderového klimatického skóre",
                    "počet_zemí": len(data_points),
                },
                "🚨 KRITICKÉ ZEMĚ (vysoká zranitelnost + nízké skóre)": data_points[:5],
                "✅ POZITIVNÍ PŘÍKLADY": sorted(data_points, key=lambda x: x["gender_climate_score"], reverse=True)[:3]
            }

        elif analysis_type == "care_climate_burden":
            # Zátěž neplacené péče vs klimatická zranitelnost
            data_points = []
            for code in countries_to_analyze:
                care_gap = HUB.banks["ilo"].data[code]["unpaid_care_hours_female"] - HUB.banks["ilo"].data[code]["unpaid_care_hours_male"]
                climate_vuln = HUB.banks["climate"].data[code]["climate_vulnerability_index"]
                data_points.append({
                    "country": COUNTRIES[code]["name"],
                    "care_gap_hours": round(care_gap, 1),
                    "climate_vulnerability": climate_vuln,
                    "double_burden_score": round(care_gap * climate_vuln, 2)
                })

            data_points.sort(key=lambda x: x["double_burden_score"], reverse=True)

            result = {
                "🔗 KŘÍŽOVÁ ANALÝZA: Care-Climate Burden": {
                    "metodologie": "Double burden = péče × klimatická zranitelnost",
                },
                "🚨 NEJVYŠŠÍ DOUBLE BURDEN": data_points[:5],
            }

        elif analysis_type == "vulnerability_inequality":
            data_points = []
            for code in countries_to_analyze:
                gii = HUB.banks["undp"].data[code]["gender_inequality_index"]
                vuln = HUB.banks["climate"].data[code]["climate_vulnerability_index"]
                data_points.append({
                    "country": COUNTRIES[code]["name"],
                    "gender_inequality_index": gii,
                    "climate_vulnerability": vuln,
                    "compound_risk": round(gii * vuln, 3)
                })
            data_points.sort(key=lambda x: x["compound_risk"], reverse=True)
            result = {
                "🔗 KŘÍŽOVÁ ANALÝZA: Vulnerability × Inequality": data_points[:8]
            }

        else:
            result = {"error": f"Neznámý typ analýzy: {analysis_type}"}

        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "get_regional_summary":
        region = params["region"].lower()
        matching = [c for c in COUNTRIES if region in COUNTRIES[c]["region"].lower()]

        if not matching:
            return json.dumps({"error": f"Region '{params['region']}' nenalezen"}, ensure_ascii=False)

        # Agregace dat
        avg_gender_score = sum(HUB.banks["unwomen"].data[c]["overall_score"] for c in matching) / len(matching)
        avg_gii = sum(HUB.banks["undp"].data[c]["gender_inequality_index"] for c in matching) / len(matching)
        avg_care_gap = sum(HUB.banks["ilo"].data[c]["unpaid_care_hours_female"] - HUB.banks["ilo"].data[c]["unpaid_care_hours_male"] for c in matching) / len(matching)
        avg_mmr = sum(HUB.banks["who"].data[c]["maternal_mortality_ratio"] for c in matching) / len(matching)

        result = {
            f"🌍 REGIONÁLNÍ SOUHRN: {params['region'].upper()}": {
                "počet_zemí": len(matching),
                "země": [COUNTRIES[c]["name"] for c in matching],
            },
            "📊 PRŮMĚRNÉ HODNOTY": {
                "gender_climate_score": f"{avg_gender_score:.1f}/100",
                "gender_inequality_index": f"{avg_gii:.3f}",
                "care_gap": f"{avg_care_gap:.1f} hodin/týden",
                "maternal_mortality": f"{avg_mmr:.0f} per 100k",
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "generate_policy_brief":
        code, info = find_country(params["country"])
        if not code:
            return json.dumps({"error": f"Země '{params['country']}' nenalezena"}, ensure_ascii=False)

        # Shromáždit data
        unwomen = HUB.banks["unwomen"].data[code]
        undp = HUB.banks["undp"].data[code]
        ilo = HUB.banks["ilo"].data[code]
        climate = HUB.banks["climate"].data[code]
        who = HUB.banks["who"].data[code]
        wb = HUB.banks["worldbank"].data[code]

        # Identifikovat slabé stránky
        weak_dims = sorted(unwomen["dimensions"].items(), key=lambda x: x[1])[:2]

        result = {
            f"📋 POLICY BRIEF: {info['name']}": {
                "datum": datetime.now().strftime("%Y-%m-%d"),
                "typ": "Gender-Responsive Climate Policy Assessment"
            },
            "📊 KLÍČOVÉ INDIKÁTORY": {
                "Gender Climate Score": f"{unwomen['overall_score']}/100",
                "Gender Inequality Index": undp["gender_inequality_index"],
                "Climate Vulnerability": climate["climate_vulnerability_index"],
                "Maternal Mortality": f"{who['maternal_mortality_ratio']} per 100k",
                "Care Gap": f"{ilo['unpaid_care_hours_female'] - ilo['unpaid_care_hours_male']:.1f}h/week",
            },
            "🚨 PRIORITNÍ OBLASTI": [
                UNWomenBank.DIMENSIONS[dim] for dim, _ in weak_dims
            ],
            "💡 DOPORUČENÍ": [
                f"Posílit {UNWomenBank.DIMENSIONS[weak_dims[0][0]]} - aktuálně {weak_dims[0][1]}/100",
                f"Zvýšit zastoupení žen v klimatických delegacích (nyní {unwomen['women_in_delegation']}%)",
                f"Řešit nerovnost v neplacené péči ({ilo['unpaid_care_hours_female'] - ilo['unpaid_care_hours_male']:.1f}h rozdíl)",
                f"Integrovat genderovou perspektivu do NDC (nyní {unwomen['ndc_gender_references']} referencí)",
            ],
            "🌟 SILNÉ STRÁNKY K VYUŽITÍ": [],
            "📈 SDG ALIGNMENT": ["SDG 5 (Gender)", "SDG 13 (Climate)", "SDG 3 (Health)", "SDG 8 (Work)"]
        }

        # Najít silné stránky
        if unwomen["has_gender_focal_point"]:
            result["🌟 SILNÉ STRÁNKY K VYUŽITÍ"].append("Existující gender focal point")
        if climate["renewable_energy_share"] > 30:
            result["🌟 SILNÉ STRÁNKY K VYUŽITÍ"].append(f"Vysoký podíl OZE ({climate['renewable_energy_share']}%)")
        if wb["women_in_parliament"] > 30:
            result["🌟 SILNÉ STRÁNKY K VYUŽITÍ"].append(f"Dobré politické zastoupení žen ({wb['women_in_parliament']}%)")

        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "search_best_practices":
        area = params["area"]

        if area == "gender_climate_policy":
            sorted_c = sorted(HUB.banks["unwomen"].data.items(), key=lambda x: x[1]["overall_score"], reverse=True)[:5]
            result = {
                "🌟 BEST PRACTICES: Gender-Climate Policy": [
                    {"country": COUNTRIES[c]["name"], "score": f"{d['overall_score']}/100",
                     "highlights": [f"{d['ndc_gender_references']} gender references in NDC"]}
                    for c, d in sorted_c
                ]
            }

        elif area == "women_leadership":
            data = [(c, HUB.banks["unwomen"].data[c]["women_in_delegation"]) for c in COUNTRIES]
            sorted_data = sorted(data, key=lambda x: x[1], reverse=True)[:5]
            result = {
                "🌟 BEST PRACTICES: Women in Climate Leadership": [
                    {"country": COUNTRIES[c]["name"], "women_in_delegation": f"{pct}%"}
                    for c, pct in sorted_data
                ]
            }

        elif area == "care_economy":
            data = [(c, HUB.banks["ilo"].data[c]["unpaid_care_hours_female"] - HUB.banks["ilo"].data[c]["unpaid_care_hours_male"]) for c in COUNTRIES]
            sorted_data = sorted(data, key=lambda x: x[1])[:5]  # Lowest gap = best
            result = {
                "🌟 BEST PRACTICES: Care Economy (lowest gap)": [
                    {"country": COUNTRIES[c]["name"], "care_gap": f"{gap:.1f}h/week"}
                    for c, gap in sorted_data
                ]
            }

        elif area == "green_jobs":
            sorted_c = sorted(HUB.banks["ilo"].data.items(), key=lambda x: x[1]["green_jobs_female_share"], reverse=True)[:5]
            result = {
                "🌟 BEST PRACTICES: Women in Green Jobs": [
                    {"country": COUNTRIES[c]["name"], "female_share": f"{d['green_jobs_female_share']}%"}
                    for c, d in sorted_c
                ]
            }

        elif area == "maternal_health":
            sorted_c = sorted(HUB.banks["who"].data.items(), key=lambda x: x[1]["maternal_mortality_ratio"])[:5]
            result = {
                "🌟 BEST PRACTICES: Maternal Health": [
                    {"country": COUNTRIES[c]["name"], "mmr": f"{d['maternal_mortality_ratio']} per 100k"}
                    for c, d in sorted_c
                ]
            }

        else:
            result = {"error": f"Unknown area: {area}"}

        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "get_sdg_alignment":
        code, info = find_country(params["country"])
        if not code:
            return json.dumps({"error": f"Země '{params['country']}' nenalezena"}, ensure_ascii=False)

        # SDG skóre na základě dat
        unwomen = HUB.banks["unwomen"].data[code]
        undp = HUB.banks["undp"].data[code]
        who = HUB.banks["who"].data[code]
        climate = HUB.banks["climate"].data[code]
        ilo = HUB.banks["ilo"].data[code]
        wb = HUB.banks["worldbank"].data[code]

        result = {
            f"🎯 SDG ALIGNMENT: {info['name']}": {},
            "SDG 5 - Gender Equality": {
                "score": f"{(100 - undp['gender_inequality_index']*100):.0f}/100",
                "indikátory": {
                    "women_in_parliament": f"{wb['women_in_parliament']}%",
                    "female_labor_participation": f"{wb['female_labor_force_participation']}%",
                }
            },
            "SDG 13 - Climate Action": {
                "score": f"{(100 - climate['climate_vulnerability_index']*100):.0f}/100",
                "indikátory": {
                    "ndc_target": climate["ndc_target_2030"],
                    "renewable_share": f"{climate['renewable_energy_share']}%",
                }
            },
            "SDG 3 - Good Health": {
                "score": f"{min(100, 100 - who['maternal_mortality_ratio']/5):.0f}/100",
                "indikátory": {
                    "maternal_mortality": f"{who['maternal_mortality_ratio']} per 100k",
                    "skilled_birth_attendance": f"{who['skilled_birth_attendance']}%",
                }
            },
            "SDG 8 - Decent Work": {
                "score": f"{100 - ilo['female_unemployment']*2:.0f}/100",
                "indikátory": {
                    "female_unemployment": f"{ilo['female_unemployment']}%",
                    "green_jobs_female": f"{ilo['green_jobs_female_share']}%",
                }
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    return json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False)

# ═══════════════════════════════════════════════════════════════════════════════
# 🤖 ReACT AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class GenderClimateAgent:
    """Multi-source ReACT Agent pro Gender & Climate Intelligence"""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.max_iterations = 12

    def run(self, query: str) -> str:
        print_header("🌍 Gender & Climate Intelligence Hub")
        print(f"{Colors.BOLD}Query:{Colors.ENDC} {query}\n")
        print(f"{Colors.DIM}{'─' * 80}{Colors.ENDC}")

        messages = [{"role": "user", "content": query}]

        system_prompt = """Jsi expertní analytik Gender & Climate Intelligence Hub - systému propojujícího 6 datových zdrojů:

🏛️ UN Women Climate Scorecard - genderové dimenze klimatických politik
📊 World Bank Gender Data - ekonomické indikátory, zaměstnanost, vzdělání
🎯 UNDP Human Development - HDI, Gender Inequality Index
🌡️ Climate Watch - NDC, emise, klimatické cíle
🏥 WHO Health Data - zdravotní indikátory, mateřská úmrtnost
👷 ILO Labour Statistics - pracovní trh, neplacená práce

TVŮJ POSTUP (ReACT):
1. REASONING: Analyzuj dotaz, rozhodni které zdroje potřebuješ
2. ACTION: Zavolej nástroje pro získání dat
3. OBSERVATION: Zpracuj výsledky, hledej souvislosti mezi zdroji
4. Opakuj nebo odpověz

PRINCIPY:
- Využívej křížové analýzy mezi zdroji pro hlubší insights
- Identifikuj korelace (např. klimatická zranitelnost × genderová nerovnost)
- Nabízej konkrétní policy doporučení založená na datech
- Cituj čísla a zdroje

Odpovídej česky, profesionálně, s důrazem na actionable insights."""

        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n{Colors.DIM}[Iteration {iteration}/{self.max_iterations}]{Colors.ENDC}")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                tools=TOOLS,
                messages=messages
            )

            assistant_content = []
            has_tool_use = False
            final_text = ""

            for block in response.content:
                if block.type == "text":
                    final_text = block.text
                    if response.stop_reason != "tool_use":
                        print_thought(block.text[:300] + "..." if len(block.text) > 300 else block.text)
                    assistant_content.append({"type": "text", "text": block.text})

                elif block.type == "tool_use":
                    has_tool_use = True
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id

                    # Identifikuj banku pro vizuální označení
                    bank = None
                    if "bank" in tool_input:
                        bank_id = tool_input["bank"]
                        if bank_id in HUB.bank_info:
                            bank = HUB.bank_info[bank_id]["name"]

                    print_action(tool_name, json.dumps(tool_input, ensure_ascii=False), bank)

                    result = execute_tool(tool_name, tool_input)
                    print_observation(result)

                    assistant_content.append({
                        "type": "tool_use",
                        "id": tool_id,
                        "name": tool_name,
                        "input": tool_input
                    })

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

            if not has_tool_use:
                print_answer(final_text)
                return final_text

        return "Max iterations reached."

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 HLAVNÍ PROGRAM
# ═══════════════════════════════════════════════════════════════════════════════

def print_dashboard():
    print(f"""
{Colors.BOLD}{Colors.MAGENTA}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     🌍  GENDER & CLIMATE INTELLIGENCE HUB                                    ║
║         Multi-Source ReACT Agent                                             ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  {Colors.UNWOMEN}🏛️ UN Women{Colors.MAGENTA}        {Colors.WORLDBANK}📊 World Bank{Colors.MAGENTA}       {Colors.UNDP}🎯 UNDP{Colors.MAGENTA}                       ║
║     Climate            Gender Data          Human Dev                        ║
║     Scorecard          Portal               Index                            ║
║                                                                              ║
║  {Colors.CLIMATE}🌡️ Climate Watch{Colors.MAGENTA}   {Colors.WHO}🏥 WHO Health{Colors.MAGENTA}       {Colors.ILO}👷 ILO Labour{Colors.MAGENTA}                   ║
║     NDC & Emissions    Women's Health       Statistics                       ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📊 COVERAGE: 25 countries │ 6 data sources │ 50+ indicators                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}

{Colors.BOLD}🔧 AVAILABLE TOOLS:{Colors.ENDC}
  • list_data_sources      • get_country_profile     • query_bank
  • compare_countries      • cross_reference_analysis • get_regional_summary
  • generate_policy_brief  • search_best_practices   • get_sdg_alignment
  • get_indicator_ranking
""")

def main():
    API_KEY = os.environ.get("ANTHROPIC_API_KEY")

    if not API_KEY:
        print_error("Nenalezen ANTHROPIC_API_KEY v environment proměnných")
        return

    print_dashboard()

    agent = GenderClimateAgent(API_KEY)

    demos = [
        "Jaké datové zdroje máš k dispozici a co obsahují?",
        "Dej mi kompletní profil Keni ze všech zdrojů",
        "Porovnej Švédsko, Indii a Brazílii - kde jsou největší rozdíly?",
        "Proveď cross-reference analýzu climate-gender nexus pro Afriku",
        "Vygeneruj policy brief pro Indonésii",
        "Které země mají nejlepší praxi v zelených pracovních místech pro ženy?",
    ]

    print(f"{Colors.BOLD}Demo queries:{Colors.ENDC}")
    for i, q in enumerate(demos, 1):
        print(f"  {i}. {q}")

    print(f"\n{Colors.BOLD}Enter query (number, custom, or 'q'):{Colors.ENDC}")

    while True:
        try:
            inp = input(f"\n{Colors.CYAN}> {Colors.ENDC}").strip()
            if inp.lower() == 'q':
                print("Goodbye! 🌍")
                break
            if inp in [str(i) for i in range(1, len(demos)+1)]:
                query = demos[int(inp)-1]
            else:
                query = inp
            if query:
                agent.run(query)
        except KeyboardInterrupt:
            print("\n\nInterrupted.")
            break
        except Exception as e:
            print_error(str(e))

if __name__ == "__main__":
    main()
