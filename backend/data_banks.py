"""
Datové banky pro Gender & Climate Intelligence Hub
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Any

# ═══════════════════════════════════════════════════════════════════════════════
# SPOLEČNÁ DATA - ZEMĚ
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

DIMENSIONS = {
    "economic_security": "Ekonomická bezpečnost",
    "unpaid_care": "Neplacená péče",
    "gender_based_violence": "Genderově založené násilí",
    "health": "Zdraví",
    "participation": "Účast a lídrovství",
    "gender_mainstreaming": "Gender mainstreaming"
}

def find_country(query: str):
    """Najde zemi podle názvu nebo kódu"""
    q = query.lower().strip()
    for code, data in COUNTRIES.items():
        if q in [code.lower(), data["name"].lower(), data["name_en"].lower()]:
            return code, data
    for code, data in COUNTRIES.items():
        if q in data["name"].lower() or q in data["name_en"].lower():
            return code, data
    return None, None


class UNWomenBank:
    name = "UN Women Climate Scorecard"
    icon = "🏛️"
    description = "Genderové dimenze klimatických politik - 6 dimenzí, 50+ indikátorů"

    def __init__(self):
        self.data = self._generate_data()

    def _generate_data(self):
        data = {}
        for code in COUNTRIES:
            base = {"high": 70, "upper_middle": 55, "lower_middle": 45, "low": 38}[COUNTRIES[code]["income"]]
            dims = {d: min(100, max(0, base + random.uniform(-15, 20))) for d in DIMENSIONS}
            data[code] = {
                "overall_score": round(sum(dims.values()) / len(dims), 1),
                "dimensions": {k: round(v, 1) for k, v in dims.items()},
                "women_in_delegation": round(random.uniform(18, 52), 1),
                "has_gender_focal_point": random.random() > 0.35,
                "ndc_gender_references": random.randint(5, 45),
            }
        return data

    def get_country_data(self, country_code: str):
        if country_code not in self.data:
            return {"error": "Country not found"}
        d = self.data[country_code]
        return {
            "source": self.name,
            "country": COUNTRIES[country_code]["name"],
            "overall_score": d['overall_score'],
            "dimensions": {DIMENSIONS[k]: v for k, v in d["dimensions"].items()},
            "women_in_climate_delegation": d['women_in_delegation'],
            "gender_focal_point": d["has_gender_focal_point"],
            "ndc_gender_references": d["ndc_gender_references"],
        }


class WorldBankGenderBank:
    name = "World Bank Gender Data"
    icon = "📊"
    description = "Ekonomické genderové indikátory - zaměstnanost, vzdělání, přístup k financím"

    def __init__(self):
        self.data = self._generate_data()

    def _generate_data(self):
        data = {}
        for code, info in COUNTRIES.items():
            base_female_labor = {"high": 65, "upper_middle": 52, "lower_middle": 35, "low": 28}[info["income"]]
            data[code] = {
                "female_labor_force_participation": round(base_female_labor + random.uniform(-10, 15), 1),
                "gender_wage_gap": round(random.uniform(10, 35), 1),
                "female_account_ownership": round(random.uniform(30, 90), 1),
                "female_secondary_education": round(random.uniform(40, 98), 1),
                "female_tertiary_education": round(random.uniform(15, 70), 1),
                "women_in_parliament": round(random.uniform(8, 48), 1),
                "female_land_ownership": round(random.uniform(5, 45), 1),
                "female_entrepreneurship": round(random.uniform(15, 40), 1),
            }
        return data

    def get_country_data(self, country_code: str):
        if country_code not in self.data:
            return {"error": "Country not found"}
        d = self.data[country_code]
        return {
            "source": self.name,
            "country": COUNTRIES[country_code]["name"],
            "labor_force": {
                "female_participation": d['female_labor_force_participation'],
                "gender_wage_gap": d['gender_wage_gap'],
            },
            "education": {
                "female_secondary": d['female_secondary_education'],
                "female_tertiary": d['female_tertiary_education'],
            },
            "economic_empowerment": {
                "account_ownership": d['female_account_ownership'],
                "land_ownership": d['female_land_ownership'],
                "entrepreneurship_rate": d['female_entrepreneurship'],
            },
            "political": {
                "women_in_parliament": d['women_in_parliament'],
            }
        }


class UNDPBank:
    name = "UNDP Human Development"
    icon = "🎯"
    description = "Human Development Index, Gender Inequality Index, Multidimensional Poverty"

    def __init__(self):
        self.data = self._generate_data()

    def _generate_data(self):
        data = {}
        for code, info in COUNTRIES.items():
            base_hdi = {"high": 0.92, "upper_middle": 0.76, "lower_middle": 0.62, "low": 0.48}[info["income"]]
            hdi = min(1.0, max(0.3, base_hdi + random.uniform(-0.08, 0.08)))
            gii = 1 - hdi + random.uniform(-0.1, 0.15)
            data[code] = {
                "hdi": round(hdi, 3),
                "hdi_rank": 0,
                "gender_inequality_index": round(max(0.05, min(0.7, gii)), 3),
                "gender_development_index": round(hdi * (1 - gii/2), 3),
                "mpi_headcount": round(max(0, (1 - hdi) * 60 + random.uniform(-10, 10)), 1),
                "life_expectancy_female": round(70 + hdi * 15 + random.uniform(-3, 3), 1),
                "expected_schooling_female": round(8 + hdi * 8 + random.uniform(-1, 1), 1),
                "gni_per_capita_female": round(5000 + hdi * 45000 + random.uniform(-5000, 5000), 0),
            }
        sorted_by_hdi = sorted(data.items(), key=lambda x: x[1]["hdi"], reverse=True)
        for i, (code, _) in enumerate(sorted_by_hdi):
            data[code]["hdi_rank"] = i + 1
        return data

    def get_country_data(self, country_code: str):
        if country_code not in self.data:
            return {"error": "Country not found"}
        d = self.data[country_code]
        return {
            "source": self.name,
            "country": COUNTRIES[country_code]["name"],
            "human_development": {
                "hdi": d["hdi"],
                "hdi_rank": d['hdi_rank'],
                "category": "Very High" if d["hdi"] >= 0.8 else "High" if d["hdi"] >= 0.7 else "Medium" if d["hdi"] >= 0.55 else "Low"
            },
            "gender_indices": {
                "gender_inequality_index": d["gender_inequality_index"],
                "gender_development_index": d["gender_development_index"],
            },
            "poverty": {
                "mpi_headcount": d['mpi_headcount'],
            },
            "female_indicators": {
                "life_expectancy": d['life_expectancy_female'],
                "expected_schooling": d['expected_schooling_female'],
                "gni_per_capita": d['gni_per_capita_female'],
            }
        }


class ClimateWatchBank:
    name = "Climate Watch"
    icon = "🌡️"
    description = "NDC commitments, emissions data, climate targets, adaptation plans"

    def __init__(self):
        self.data = self._generate_data()

    def _generate_data(self):
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

    def get_country_data(self, country_code: str):
        if country_code not in self.data:
            return {"error": "Country not found"}
        d = self.data[country_code]
        return {
            "source": self.name,
            "country": COUNTRIES[country_code]["name"],
            "emissions": {
                "total_mtco2": d['total_emissions_mtco2'],
                "per_capita": d['emissions_per_capita'],
            },
            "ndc_commitments": {
                "target_2030": d["ndc_target_2030"],
                "ndc_submission_year": d["ndc_year"],
                "net_zero_target": d["net_zero_year"] if d["has_net_zero_target"] else None,
            },
            "adaptation": {
                "national_adaptation_plan": d["adaptation_plan"],
                "vulnerability_index": d["climate_vulnerability_index"],
            },
            "energy_and_finance": {
                "renewable_share": d['renewable_energy_share'],
                "climate_finance_received": d["climate_finance_received_musd"],
            }
        }


class WHOBank:
    name = "WHO Health Data"
    icon = "🏥"
    description = "Zdravotní indikátory se zaměřením na ženy - mateřská úmrtnost, reprodukční zdraví"

    def __init__(self):
        self.data = self._generate_data()

    def _generate_data(self):
        data = {}
        for code, info in COUNTRIES.items():
            base_mmr = {"high": 8, "upper_middle": 45, "lower_middle": 150, "low": 400}[info["income"]]
            data[code] = {
                "maternal_mortality_ratio": round(base_mmr * random.uniform(0.6, 1.4)),
                "skilled_birth_attendance": round(min(100, 100 - base_mmr/5 + random.uniform(-5, 10)), 1),
                "contraceptive_prevalence": round(random.uniform(25, 80), 1),
                "antenatal_care_coverage": round(random.uniform(50, 98), 1),
                "adolescent_birth_rate": round(random.uniform(5, 120), 1),
                "female_hiv_prevalence": round(random.uniform(0.1, 8), 2) if info["region"] in ["East Africa", "Southern Africa", "West Africa"] else round(random.uniform(0.05, 0.5), 2),
                "uhc_service_coverage_index": round(random.uniform(35, 85), 0),
                "heat_wave_mortality_female": round(random.uniform(0.5, 15), 1),
            }
        return data

    def get_country_data(self, country_code: str):
        if country_code not in self.data:
            return {"error": "Country not found"}
        d = self.data[country_code]
        return {
            "source": self.name,
            "country": COUNTRIES[country_code]["name"],
            "maternal_health": {
                "maternal_mortality_ratio": d['maternal_mortality_ratio'],
                "skilled_birth_attendance": d['skilled_birth_attendance'],
                "antenatal_care": d['antenatal_care_coverage'],
            },
            "reproductive_health": {
                "contraceptive_prevalence": d['contraceptive_prevalence'],
                "adolescent_birth_rate": d['adolescent_birth_rate'],
            },
            "climate_health_nexus": {
                "heat_wave_mortality_female": d['heat_wave_mortality_female'],
            },
            "health_system": {
                "uhc_coverage_index": d["uhc_service_coverage_index"],
            }
        }


class ILOBank:
    name = "ILO Labour Statistics"
    icon = "👷"
    description = "Pracovní trh, neplacená práce, zelená zaměstnanost, pracovní podmínky"

    def __init__(self):
        self.data = self._generate_data()

    def _generate_data(self):
        data = {}
        for code, info in COUNTRIES.items():
            data[code] = {
                "female_unemployment": round(random.uniform(3, 25), 1),
                "youth_female_neet": round(random.uniform(8, 45), 1),
                "unpaid_care_hours_female": round(random.uniform(15, 45), 1),
                "unpaid_care_hours_male": round(random.uniform(3, 15), 1),
                "informal_employment_female": round(random.uniform(15, 85), 1),
                "green_jobs_female_share": round(random.uniform(15, 45), 1),
                "female_managers_share": round(random.uniform(15, 45), 1),
                "maternity_leave_weeks": random.randint(6, 26),
                "childcare_enrollment_0_3": round(random.uniform(5, 65), 1),
            }
        return data

    def get_country_data(self, country_code: str):
        if country_code not in self.data:
            return {"error": "Country not found"}
        d = self.data[country_code]
        care_gap = d["unpaid_care_hours_female"] - d["unpaid_care_hours_male"]
        return {
            "source": self.name,
            "country": COUNTRIES[country_code]["name"],
            "employment": {
                "female_unemployment": d['female_unemployment'],
                "youth_female_neet": d['youth_female_neet'],
                "informal_employment": d['informal_employment_female'],
            },
            "unpaid_care_work": {
                "female_hours_per_week": d["unpaid_care_hours_female"],
                "male_hours_per_week": d["unpaid_care_hours_male"],
                "gender_gap": round(care_gap, 1),
            },
            "green_economy": {
                "female_share_green_jobs": d['green_jobs_female_share'],
            },
            "work_family_balance": {
                "maternity_leave": d['maternity_leave_weeks'],
                "childcare_enrollment": d['childcare_enrollment_0_3'],
            },
            "leadership": {
                "female_managers": d['female_managers_share'],
            }
        }


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
            "unwomen": {"name": "UN Women Climate Scorecard", "icon": "🏛️", "color": "#E91E63"},
            "worldbank": {"name": "World Bank Gender Data", "icon": "📊", "color": "#2196F3"},
            "undp": {"name": "UNDP Human Development", "icon": "🎯", "color": "#00BCD4"},
            "climate": {"name": "Climate Watch", "icon": "🌡️", "color": "#4CAF50"},
            "who": {"name": "WHO Health Data", "icon": "🏥", "color": "#03A9F4"},
            "ilo": {"name": "ILO Labour Statistics", "icon": "👷", "color": "#FF9800"},
        }

    def get_all_sources(self):
        return [
            {
                "id": bank_id,
                "name": info["name"],
                "icon": info["icon"],
                "color": info["color"],
                "description": self.banks[bank_id].description
            }
            for bank_id, info in self.bank_info.items()
        ]

    def get_country_profile(self, country_code: str):
        result = {}
        for bank_id, bank in self.banks.items():
            result[bank_id] = bank.get_country_data(country_code)
        return result
