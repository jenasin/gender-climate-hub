#!/usr/bin/env python3
"""
🌍 Gender & Climate Scorecard Agent
====================================
ReACT agent pro analýzu genderově responzivních klimatických politik
na základě UN Women Climate Scorecard metodologie.

6 dimenzí | 50+ indikátorů | 32+ zemí

Pro článek o AI agentech v oblasti udržitelnosti a gender equality.
"""

import anthropic
import json
from dataclasses import dataclass, field
from typing import Any
import random

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 BAREVNÝ VÝSTUP
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[35m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'═' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}  {text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'═' * 70}{Colors.ENDC}\n")

def print_thought(text: str):
    print(f"{Colors.YELLOW}💭 MYŠLENÍ:{Colors.ENDC} {text}")

def print_action(tool: str, params: str):
    print(f"{Colors.CYAN}⚡ AKCE:{Colors.ENDC} {tool}")
    print(f"{Colors.DIM}   └─ parametry: {params}{Colors.ENDC}")

def print_observation(text: str):
    print(f"{Colors.GREEN}👁️ POZOROVÁNÍ:{Colors.ENDC}")
    for line in text.split('\n')[:15]:
        print(f"   {line}")
    if text.count('\n') > 15:
        print(f"   {Colors.DIM}... (zkráceno){Colors.ENDC}")

def print_answer(text: str):
    print(f"\n{Colors.BOLD}{Colors.GREEN}✅ ODPOVĚĎ:{Colors.ENDC}")
    print(f"{Colors.GREEN}{text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.RED}❌ CHYBA: {text}{Colors.ENDC}")

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 DATOVÉ STRUKTURY - UN WOMEN CLIMATE SCORECARD
# ═══════════════════════════════════════════════════════════════════════════════

# 6 genderových dimenzí podle UN Women metodologie
DIMENSIONS = {
    "economic_security": {
        "name": "Ekonomická bezpečnost",
        "name_en": "Economic Security",
        "icon": "💰",
        "description": "Řeší ekonomickou zranitelnost žen v kontextu klimatické změny, včetně chudoby a přístupu k zdrojům",
        "indicators": [
            "Přístup žen k půdě a majetku",
            "Genderová mezera v příjmech v zelených sektorech",
            "Přístup žen k mikrofinancím pro klimatickou adaptaci",
            "Zaměstnanost žen v obnovitelné energetice",
            "Ochrana živobytí žen při klimatických katastrofách",
            "Přístup k pojištění proti klimatickým rizikům",
            "Účast žen v programech zeleného zaměstnávání",
            "Genderově citlivé sociální záchranné sítě"
        ]
    },
    "unpaid_care": {
        "name": "Neplacená péče",
        "name_en": "Unpaid Care Work",
        "icon": "🏠",
        "description": "Zaměřuje se na nepřiměřenou zátěž žen v péči o domácnost, sběru vody a paliva",
        "indicators": [
            "Čas strávený sběrem vody (% rozdíl muži/ženy)",
            "Přístup k čisté pitné vodě",
            "Přístup k čistému vaření",
            "Infrastruktura pro snížení domácí práce",
            "Redistribuce péče v klimatických politikách",
            "Investice do časově úsporných technologií",
            "Zapojení mužů do domácí péče",
            "Veřejné služby péče o děti"
        ]
    },
    "gender_based_violence": {
        "name": "Genderově založené násilí",
        "name_en": "Gender-Based Violence",
        "icon": "🛡️",
        "description": "Sleduje spojitost mezi klimatickými šoky a násilím na ženách, včetně dětských sňatků",
        "indicators": [
            "GBV protokoly v klimatických krizích",
            "Prevence dětských sňatků při suchu",
            "Bezpečné útočiště při katastrofách",
            "Školení humanitárních pracovníků",
            "Reporting mechanismy v krizích",
            "Ochrana žen v táborech pro vysídlené",
            "Právní ochrana při klimatické migraci",
            "Psychosociální podpora"
        ]
    },
    "health": {
        "name": "Zdraví",
        "name_en": "Health",
        "icon": "🏥",
        "description": "Měří dopady klimatu na zdraví žen, včetně reprodukčního zdraví a vln horka",
        "indicators": [
            "Přístup k reprodukčnímu zdraví při krizích",
            "Ochrana těhotných při vlnách horka",
            "Mateřská úmrtnost v klimaticky zranitelných oblastech",
            "Přístup k čisté vodě pro hygienické potřeby",
            "Mentální zdraví žen po katastrofách",
            "Nutriční bezpečnost matek",
            "Zdravotní infrastruktura odolná vůči klimatu",
            "Genderově specifická zdravotní data"
        ]
    },
    "participation": {
        "name": "Účast a lídrovství",
        "name_en": "Participation & Leadership",
        "icon": "👩‍💼",
        "description": "Měří zastoupení žen v klimatickém rozhodování na všech úrovních",
        "indicators": [
            "Ženy v národních klimatických delegacích",
            "Ženy v klimatických ministerstvech",
            "Účast žen na COP jednáních",
            "Ženy ve vedení klimatických fondů",
            "Lokální lídryně v komunitní adaptaci",
            "Ženy v technických klimatických pozicích",
            "Genderová kvóta v klimatických orgánech",
            "Hlas žen v NDC konzultacích"
        ]
    },
    "gender_mainstreaming": {
        "name": "Gender mainstreaming",
        "name_en": "Gender Mainstreaming",
        "icon": "⚖️",
        "description": "Hodnotí institucionální zakotvení genderu v klimatických politikách",
        "indicators": [
            "Gender zmíněn v NDC",
            "Genderový akční plán pro klima",
            "Genderové rozpočtování v klimatu",
            "Focal point pro gender a klima",
            "Genderově disagregovaná data",
            "Intersekcionální přístup",
            "Monitoring genderových indikátorů",
            "Kapacity pro genderovou analýzu"
        ]
    }
}

# Klimatické oblasti
CLIMATE_AREAS = ["adaptation", "mitigation", "loss_and_damage", "cross_cutting"]

# Sektory
SECTORS = ["agriculture", "energy", "water", "health", "transport", "tourism", "forestry", "urban"]

@dataclass
class CountryData:
    """Data jedné země v Climate Scorecard"""
    code: str
    name: str
    name_en: str
    region: str
    income_level: str
    ndc_year: int
    overall_score: float  # 0-100
    dimension_scores: dict  # skóre pro každou dimenzi
    sector_coverage: list  # které sektory jsou pokryty
    climate_areas: list  # které klimatické oblasti
    highlights: list  # pozitivní příklady
    gaps: list  # mezery a výzvy
    women_in_delegation: float  # % žen v klimatické delegaci
    has_gender_focal_point: bool
    gender_budget_allocated: bool

class ClimateGenderData:
    """Simulovaná databáze UN Women Climate Scorecard"""

    def __init__(self):
        self.countries = self._generate_countries()
        self.global_stats = self._calculate_global_stats()

    def _generate_countries(self) -> list[CountryData]:
        """Generuje realistická data pro 32 zemí"""

        countries_info = [
            # (kód, název CZ, název EN, region, income)
            ("BRB", "Barbados", "Barbados", "Caribbean", "high"),
            ("BLZ", "Belize", "Belize", "Central America", "upper_middle"),
            ("BWA", "Botswana", "Botswana", "Southern Africa", "upper_middle"),
            ("BRA", "Brazílie", "Brazil", "South America", "upper_middle"),
            ("KHM", "Kambodža", "Cambodia", "Southeast Asia", "lower_middle"),
            ("CAN", "Kanada", "Canada", "North America", "high"),
            ("CHL", "Chile", "Chile", "South America", "high"),
            ("COL", "Kolumbie", "Colombia", "South America", "upper_middle"),
            ("CRI", "Kostarika", "Costa Rica", "Central America", "upper_middle"),
            ("CUB", "Kuba", "Cuba", "Caribbean", "upper_middle"),
            ("ECU", "Ekvádor", "Ecuador", "South America", "upper_middle"),
            ("ETH", "Etiopie", "Ethiopia", "East Africa", "low"),
            ("FJI", "Fidži", "Fiji", "Pacific", "upper_middle"),
            ("DEU", "Německo", "Germany", "Europe", "high"),
            ("GHA", "Ghana", "Ghana", "West Africa", "lower_middle"),
            ("IND", "Indie", "India", "South Asia", "lower_middle"),
            ("IDN", "Indonésie", "Indonesia", "Southeast Asia", "upper_middle"),
            ("JPN", "Japonsko", "Japan", "East Asia", "high"),
            ("KEN", "Keňa", "Kenya", "East Africa", "lower_middle"),
            ("MDG", "Madagaskar", "Madagascar", "East Africa", "low"),
            ("MWI", "Malawi", "Malawi", "Southern Africa", "low"),
            ("MEX", "Mexiko", "Mexico", "North America", "upper_middle"),
            ("NPL", "Nepál", "Nepal", "South Asia", "lower_middle"),
            ("NZL", "Nový Zéland", "New Zealand", "Pacific", "high"),
            ("NGA", "Nigérie", "Nigeria", "West Africa", "lower_middle"),
            ("PER", "Peru", "Peru", "South America", "upper_middle"),
            ("PHL", "Filipíny", "Philippines", "Southeast Asia", "lower_middle"),
            ("RWA", "Rwanda", "Rwanda", "East Africa", "low"),
            ("ZAF", "Jihoafrická republika", "South Africa", "Southern Africa", "upper_middle"),
            ("SWE", "Švédsko", "Sweden", "Europe", "high"),
            ("UGA", "Uganda", "Uganda", "East Africa", "low"),
            ("VNM", "Vietnam", "Vietnam", "Southeast Asia", "lower_middle"),
        ]

        countries = []
        for code, name_cz, name_en, region, income in countries_info:
            # Generování realistických skóre podle regionu a příjmu
            base_score = {"high": 70, "upper_middle": 55, "lower_middle": 45, "low": 35}[income]
            variance = random.uniform(-15, 20)

            dimension_scores = {}
            for dim_key in DIMENSIONS.keys():
                dim_variance = random.uniform(-10, 15)
                dimension_scores[dim_key] = min(100, max(0, base_score + dim_variance))

            overall = sum(dimension_scores.values()) / len(dimension_scores)

            # Sektory a klimatické oblasti
            num_sectors = random.randint(3, 7)
            num_areas = random.randint(2, 4)

            # Highlights a gaps
            all_highlights = [
                "Genderový akční plán pro klima schválen",
                "40%+ žen v klimatické delegaci",
                "Genderově citlivé klimatické financování",
                "Komunitní programy pro ženy farmářky",
                "Ochrana žen při klimatických katastrofách",
                "Investice do čisté energie pro domácnosti",
                "Školení žen v zelených technologiích",
                "Genderově disagregovaná klimatická data",
            ]

            all_gaps = [
                "Chybí genderové rozpočtování",
                "Nízká účast žen v rozhodování",
                "Nedostatečná ochrana při katastrofách",
                "Chybí data o genderových dopadech",
                "Omezený přístup žen k půdě",
                "Nedostatek žen v technických pozicích",
                "Slabá koordinace gender-klima",
                "Nedostatečné financování genderových opatření",
            ]

            countries.append(CountryData(
                code=code,
                name=name_cz,
                name_en=name_en,
                region=region,
                income_level=income,
                ndc_year=random.choice([2021, 2022, 2023, 2024, 2025]),
                overall_score=round(overall, 1),
                dimension_scores={k: round(v, 1) for k, v in dimension_scores.items()},
                sector_coverage=random.sample(SECTORS, num_sectors),
                climate_areas=random.sample(CLIMATE_AREAS, num_areas),
                highlights=random.sample(all_highlights, random.randint(2, 4)),
                gaps=random.sample(all_gaps, random.randint(2, 4)),
                women_in_delegation=round(random.uniform(15, 55), 1),
                has_gender_focal_point=random.random() > 0.3,
                gender_budget_allocated=random.random() > 0.5,
            ))

        return sorted(countries, key=lambda x: x.overall_score, reverse=True)

    def _calculate_global_stats(self) -> dict:
        """Vypočítá globální statistiky"""
        scores = [c.overall_score for c in self.countries]
        women_rep = [c.women_in_delegation for c in self.countries]

        return {
            "total_countries": len(self.countries),
            "average_score": round(sum(scores) / len(scores), 1),
            "median_score": round(sorted(scores)[len(scores)//2], 1),
            "top_performer": self.countries[0].name,
            "average_women_delegation": round(sum(women_rep) / len(women_rep), 1),
            "countries_with_focal_point": sum(1 for c in self.countries if c.has_gender_focal_point),
            "countries_with_gender_budget": sum(1 for c in self.countries if c.gender_budget_allocated),
        }

# Globální instance
DATA = ClimateGenderData()

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 STATICKÉ NÁSTROJE (TOOLS)
# ═══════════════════════════════════════════════════════════════════════════════

TOOLS = [
    {
        "name": "get_global_overview",
        "description": "Získá globální přehled Climate Scorecard - celkové statistiky, průměry, top země. Ideální pro začátek analýzy.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_country_profile",
        "description": "Získá detailní profil konkrétní země včetně skóre ve všech 6 dimenzích, silných stránek a mezer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "Název země (česky nebo anglicky) nebo kód země (např. CZE, BRA, KEN)"
                }
            },
            "required": ["country"]
        }
    },
    {
        "name": "compare_countries",
        "description": "Porovná dvě nebo více zemí podle skóre, dimenzí a specifických indikátorů.",
        "input_schema": {
            "type": "object",
            "properties": {
                "countries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Seznam zemí k porovnání (názvy nebo kódy)"
                }
            },
            "required": ["countries"]
        }
    },
    {
        "name": "analyze_dimension",
        "description": "Hloubková analýza jedné z 6 genderových dimenzí napříč všemi zeměmi.",
        "input_schema": {
            "type": "object",
            "properties": {
                "dimension": {
                    "type": "string",
                    "enum": ["economic_security", "unpaid_care", "gender_based_violence", "health", "participation", "gender_mainstreaming"],
                    "description": "Dimenze k analýze"
                }
            },
            "required": ["dimension"]
        }
    },
    {
        "name": "filter_countries",
        "description": "Filtruje země podle regionu, příjmové kategorie nebo minimálního skóre.",
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "description": "Region (např. 'Africa', 'Europe', 'Asia', 'Caribbean')"
                },
                "income_level": {
                    "type": "string",
                    "enum": ["high", "upper_middle", "lower_middle", "low"],
                    "description": "Příjmová kategorie"
                },
                "min_score": {
                    "type": "number",
                    "description": "Minimální celkové skóre (0-100)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_top_performers",
        "description": "Zobrazí nejlepší země celkově nebo v konkrétní dimenzi.",
        "input_schema": {
            "type": "object",
            "properties": {
                "dimension": {
                    "type": "string",
                    "description": "Konkrétní dimenze, nebo prázdné pro celkové skóre"
                },
                "limit": {
                    "type": "integer",
                    "description": "Počet zemí (výchozí 10)"
                }
            },
            "required": []
        }
    },
    {
        "name": "identify_gaps",
        "description": "Identifikuje nejčastější mezery a výzvy napříč zeměmi nebo v konkrétním regionu.",
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "description": "Filtr podle regionu (volitelné)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_recommendations",
        "description": "Generuje doporučení pro zlepšení genderově responzivní klimatické politiky pro konkrétní zemi.",
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "Název nebo kód země"
                }
            },
            "required": ["country"]
        }
    },
    {
        "name": "sector_analysis",
        "description": "Analyzuje pokrytí genderových aspektů podle ekonomických sektorů (zemědělství, energie, voda, atd.).",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector": {
                    "type": "string",
                    "enum": ["agriculture", "energy", "water", "health", "transport", "tourism", "forestry", "urban"],
                    "description": "Sektor k analýze"
                }
            },
            "required": ["sector"]
        }
    },
    {
        "name": "women_leadership_stats",
        "description": "Statistiky o zastoupení žen v klimatickém lídrovství - delegace, focal points, rozpočty.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# ═══════════════════════════════════════════════════════════════════════════════
# ⚙️ IMPLEMENTACE NÁSTROJŮ
# ═══════════════════════════════════════════════════════════════════════════════

def find_country(query: str) -> CountryData | None:
    """Najde zemi podle názvu nebo kódu"""
    query_lower = query.lower()
    for c in DATA.countries:
        if query_lower in [c.code.lower(), c.name.lower(), c.name_en.lower()]:
            return c
    # Částečná shoda
    for c in DATA.countries:
        if query_lower in c.name.lower() or query_lower in c.name_en.lower():
            return c
    return None

def execute_tool(name: str, params: dict) -> str:
    """Spustí nástroj a vrátí výsledek"""

    if name == "get_global_overview":
        stats = DATA.global_stats
        result = {
            "📊 GLOBÁLNÍ PŘEHLED CLIMATE SCORECARD": {
                "počet_zemí": stats["total_countries"],
                "průměrné_skóre": f"{stats['average_score']}/100",
                "mediánové_skóre": f"{stats['median_score']}/100",
                "nejlepší_země": stats["top_performer"],
            },
            "👩‍💼 ZASTOUPENÍ ŽEN": {
                "průměr_žen_v_delegacích": f"{stats['average_women_delegation']}%",
                "cíl_UN_Women": "50% do 2027",
                "zemí_s_gender_focal_point": f"{stats['countries_with_focal_point']}/{stats['total_countries']}",
                "zemí_s_genderovým_rozpočtem": f"{stats['countries_with_gender_budget']}/{stats['total_countries']}",
            },
            "📈 6 GENDEROVÝCH DIMENZÍ": [
                f"{d['icon']} {d['name']}" for d in DIMENSIONS.values()
            ]
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "get_country_profile":
        country = find_country(params["country"])
        if not country:
            return json.dumps({"error": f"Země '{params['country']}' nenalezena"}, ensure_ascii=False)

        result = {
            f"🌍 {country.name} ({country.code})": {
                "region": country.region,
                "příjmová_kategorie": country.income_level,
                "rok_NDC": country.ndc_year,
                "celkové_skóre": f"{country.overall_score}/100",
            },
            "📊 SKÓRE PODLE DIMENZÍ": {
                f"{DIMENSIONS[k]['icon']} {DIMENSIONS[k]['name']}": f"{v}/100"
                for k, v in country.dimension_scores.items()
            },
            "👩‍💼 LÍDROVSTVÍ": {
                "ženy_v_delegaci": f"{country.women_in_delegation}%",
                "gender_focal_point": "✅ Ano" if country.has_gender_focal_point else "❌ Ne",
                "genderový_rozpočet": "✅ Ano" if country.gender_budget_allocated else "❌ Ne",
            },
            "✨ SILNÉ STRÁNKY": country.highlights,
            "⚠️ MEZERY A VÝZVY": country.gaps,
            "🏭 POKRYTÉ SEKTORY": country.sector_coverage,
            "🌡️ KLIMATICKÉ OBLASTI": country.climate_areas,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "compare_countries":
        countries = [find_country(c) for c in params["countries"]]
        countries = [c for c in countries if c]  # filtr None

        if len(countries) < 2:
            return json.dumps({"error": "Potřeba alespoň 2 platné země pro porovnání"}, ensure_ascii=False)

        comparison = {"🔄 POROVNÁNÍ ZEMÍ": {}}
        for c in countries:
            comparison["🔄 POROVNÁNÍ ZEMÍ"][c.name] = {
                "celkové_skóre": f"{c.overall_score}/100",
                "nejsilnější_dimenze": max(c.dimension_scores.items(), key=lambda x: x[1])[0],
                "nejslabší_dimenze": min(c.dimension_scores.items(), key=lambda x: x[1])[0],
                "ženy_v_delegaci": f"{c.women_in_delegation}%",
            }

        # Detailní porovnání dimenzí
        comparison["📊 DIMENZE"] = {}
        for dim_key, dim_info in DIMENSIONS.items():
            comparison["📊 DIMENZE"][dim_info["name"]] = {
                c.name: f"{c.dimension_scores[dim_key]}/100" for c in countries
            }

        return json.dumps(comparison, ensure_ascii=False, indent=2)

    elif name == "analyze_dimension":
        dim_key = params["dimension"]
        dim = DIMENSIONS[dim_key]

        # Seřadit země podle této dimenze
        sorted_countries = sorted(DATA.countries, key=lambda x: x.dimension_scores[dim_key], reverse=True)

        scores = [c.dimension_scores[dim_key] for c in DATA.countries]
        avg_score = sum(scores) / len(scores)

        result = {
            f"{dim['icon']} ANALÝZA: {dim['name'].upper()}": {
                "popis": dim["description"],
                "průměrné_skóre": f"{avg_score:.1f}/100",
            },
            "📈 TOP 5 ZEMÍ": [
                f"{c.name}: {c.dimension_scores[dim_key]}/100"
                for c in sorted_countries[:5]
            ],
            "📉 NEJSLABŠÍCH 5": [
                f"{c.name}: {c.dimension_scores[dim_key]}/100"
                for c in sorted_countries[-5:]
            ],
            "📋 INDIKÁTORY TÉTO DIMENZE": dim["indicators"],
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "filter_countries":
        filtered = DATA.countries

        if params.get("region"):
            region = params["region"].lower()
            filtered = [c for c in filtered if region in c.region.lower()]

        if params.get("income_level"):
            filtered = [c for c in filtered if c.income_level == params["income_level"]]

        if params.get("min_score"):
            filtered = [c for c in filtered if c.overall_score >= params["min_score"]]

        result = {
            "🔍 FILTROVANÉ ZEMĚ": f"Nalezeno {len(filtered)} zemí",
            "📋 SEZNAM": [
                {
                    "země": c.name,
                    "region": c.region,
                    "skóre": f"{c.overall_score}/100"
                }
                for c in filtered[:15]
            ]
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "get_top_performers":
        limit = params.get("limit", 10)
        dimension = params.get("dimension")

        if dimension and dimension in DIMENSIONS:
            sorted_c = sorted(DATA.countries, key=lambda x: x.dimension_scores[dimension], reverse=True)
            dim_name = DIMENSIONS[dimension]["name"]
            result = {
                f"🏆 TOP {limit} V DIMENZI: {dim_name}": [
                    {
                        "pořadí": i+1,
                        "země": c.name,
                        "skóre": f"{c.dimension_scores[dimension]}/100"
                    }
                    for i, c in enumerate(sorted_c[:limit])
                ]
            }
        else:
            result = {
                f"🏆 TOP {limit} CELKOVĚ": [
                    {
                        "pořadí": i+1,
                        "země": c.name,
                        "skóre": f"{c.overall_score}/100",
                        "region": c.region
                    }
                    for i, c in enumerate(DATA.countries[:limit])
                ]
            }
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "identify_gaps":
        region = params.get("region")
        countries = DATA.countries

        if region:
            countries = [c for c in countries if region.lower() in c.region.lower()]

        # Agregace mezer
        gap_counts = {}
        for c in countries:
            for gap in c.gaps:
                gap_counts[gap] = gap_counts.get(gap, 0) + 1

        sorted_gaps = sorted(gap_counts.items(), key=lambda x: x[1], reverse=True)

        result = {
            "⚠️ NEJČASTĚJŠÍ MEZERY": [
                {"mezera": gap, "počet_zemí": count}
                for gap, count in sorted_gaps
            ],
            "📊 DIMENZE S NEJNIŽŠÍM SKÓRE": {},
        }

        # Najít nejslabší dimenze
        for dim_key in DIMENSIONS:
            avg = sum(c.dimension_scores[dim_key] for c in countries) / len(countries)
            result["📊 DIMENZE S NEJNIŽŠÍM SKÓRE"][DIMENSIONS[dim_key]["name"]] = f"{avg:.1f}/100"

        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "get_recommendations":
        country = find_country(params["country"])
        if not country:
            return json.dumps({"error": f"Země '{params['country']}' nenalezena"}, ensure_ascii=False)

        # Najít nejslabší dimenze
        weak_dims = sorted(country.dimension_scores.items(), key=lambda x: x[1])[:3]

        recommendations = {
            f"💡 DOPORUČENÍ PRO: {country.name}": {
                "aktuální_skóre": f"{country.overall_score}/100",
                "cílové_skóre": f"{min(100, country.overall_score + 15)}/100",
            },
            "🎯 PRIORITNÍ OBLASTI": [
                f"{DIMENSIONS[dim]['icon']} {DIMENSIONS[dim]['name']}: aktuálně {score}/100"
                for dim, score in weak_dims
            ],
            "📋 KONKRÉTNÍ KROKY": [],
            "🌟 INSPIRACE Z BEST PRACTICE": [],
        }

        # Generování doporučení podle slabých dimenzí
        for dim, score in weak_dims:
            if dim == "economic_security":
                recommendations["📋 KONKRÉTNÍ KROKY"].append("Zavést genderově citlivé klimatické financování")
                recommendations["📋 KONKRÉTNÍ KROKY"].append("Podpora žen v zelených profesích")
            elif dim == "participation":
                recommendations["📋 KONKRÉTNÍ KROKY"].append("Stanovit 40% kvótu pro ženy v klimatických orgánech")
                recommendations["📋 KONKRÉTNÍ KROKY"].append("Školení žen pro technické klimatické pozice")
            elif dim == "gender_mainstreaming":
                recommendations["📋 KONKRÉTNÍ KROKY"].append("Vytvořit genderový akční plán pro klima")
                recommendations["📋 KONKRÉTNÍ KROKY"].append("Zavést genderově disagregovaný monitoring")

        # Best practice z top zemí
        top_countries = DATA.countries[:3]
        for tc in top_countries:
            if tc.code != country.code:
                recommendations["🌟 INSPIRACE Z BEST PRACTICE"].append(
                    f"{tc.name}: {random.choice(tc.highlights)}"
                )

        return json.dumps(recommendations, ensure_ascii=False, indent=2)

    elif name == "sector_analysis":
        sector = params["sector"]
        sector_names = {
            "agriculture": "Zemědělství",
            "energy": "Energie",
            "water": "Voda",
            "health": "Zdravotnictví",
            "transport": "Doprava",
            "tourism": "Cestovní ruch",
            "forestry": "Lesnictví",
            "urban": "Městské plánování"
        }

        countries_with_sector = [c for c in DATA.countries if sector in c.sector_coverage]

        result = {
            f"🏭 SEKTOROVÁ ANALÝZA: {sector_names[sector].upper()}": {
                "počet_zemí_s_pokrytím": len(countries_with_sector),
                "procento_pokrytí": f"{100*len(countries_with_sector)/len(DATA.countries):.1f}%",
            },
            "📋 ZEMĚ S TÍMTO SEKTOREM": [c.name for c in countries_with_sector[:10]],
            "💡 GENDEROVÉ ASPEKTY V SEKTORU": {
                "agriculture": ["Přístup žen k půdě", "Klimaticky odolné zemědělství", "Ženské kooperativy"],
                "energy": ["Čistá energie pro domácnosti", "Ženy v obnovitelných zdrojích", "Energetická chudoba"],
                "water": ["Sběr vody - časová zátěž žen", "Přístup k čisté vodě", "Sanitace a hygiena"],
                "health": ["Reprodukční zdraví při krizích", "Vlny horka a těhotenství", "Mentální zdraví"],
            }.get(sector, ["Data nejsou k dispozici"])
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    elif name == "women_leadership_stats":
        high_rep = [c for c in DATA.countries if c.women_in_delegation >= 40]
        with_focal = [c for c in DATA.countries if c.has_gender_focal_point]

        result = {
            "👩‍💼 STATISTIKY ŽENSKÉHO LÍDROVSTVÍ": {
                "průměr_žen_v_delegacích": f"{DATA.global_stats['average_women_delegation']}%",
                "cíl_2027": "50%",
                "gap_k_cíli": f"{50 - DATA.global_stats['average_women_delegation']:.1f} p.b.",
            },
            "🌟 ZEMĚ S 40%+ ŽENAMI V DELEGACI": [
                f"{c.name}: {c.women_in_delegation}%" for c in high_rep
            ],
            "📋 INSTITUCIONÁLNÍ KAPACITA": {
                "zemí_s_gender_focal_point": f"{len(with_focal)}/{len(DATA.countries)}",
                "zemí_s_genderovým_rozpočtem": f"{DATA.global_stats['countries_with_gender_budget']}/{len(DATA.countries)}",
            },
            "📈 COP29 STATISTIKA": {
                "ženy_v_delegacích": "24%",
                "meziroční_změna": "+2 p.b.",
                "cíl_COP30": "30%"
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    return json.dumps({"error": f"Neznámý nástroj: {name}"}, ensure_ascii=False)

# ═══════════════════════════════════════════════════════════════════════════════
# 🤖 ReACT AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class ClimateGenderAgent:
    """
    ReACT Agent pro analýzu Gender & Climate Scorecard

    Reasoning → Action → Observation → ... → Answer
    """

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.max_iterations = 10

    def run(self, user_query: str) -> str:
        """Spustí ReACT loop"""

        print_header("🌍 Gender & Climate Agent - ReACT")
        print(f"{Colors.BOLD}Dotaz:{Colors.ENDC} {user_query}\n")
        print(f"{Colors.DIM}{'─' * 70}{Colors.ENDC}")

        messages = [{"role": "user", "content": user_query}]

        system_prompt = """Jsi expertní analytik UN Women Gender & Climate Scorecard. Analyzuješ genderově responzivní klimatické politiky zemí světa.

Tvůj postup (ReACT pattern):
1. MYŠLENÍ: Rozmysli si, jaká data potřebuješ
2. AKCE: Zavolej vhodný nástroj
3. POZOROVÁNÍ: Analyzuj výsledky
4. Opakuj nebo odpověz

KONTEXT:
- Climate Scorecard měří 6 dimenzí: ekonomická bezpečnost, neplacená péče, genderově založené násilí, zdraví, účast/lídrovství, gender mainstreaming
- Hodnotí 32+ zemí pomocí 50+ indikátorů
- Cíl: podpora genderově spravedlivé klimatické akce

Odpovídej česky. Buď konkrétní, cituj čísla. Nabízej insights a doporučení."""

        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n{Colors.DIM}[Iterace {iteration}/{self.max_iterations}]{Colors.ENDC}")

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
                        print_thought(block.text[:200] + "..." if len(block.text) > 200 else block.text)
                    assistant_content.append({"type": "text", "text": block.text})

                elif block.type == "tool_use":
                    has_tool_use = True
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id

                    print_action(tool_name, json.dumps(tool_input, ensure_ascii=False))

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

        return "Dosažen maximální počet iterací."

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 HLAVNÍ PROGRAM
# ═══════════════════════════════════════════════════════════════════════════════

def print_tools_sidebar():
    """Zobrazí boční panel s nástroji"""
    print(f"""
{Colors.BOLD}{Colors.MAGENTA}╔════════════════════════════════════════════════════════╗
║          🔧 DOSTUPNÉ NÁSTROJE                          ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  🌍 get_global_overview                                ║
║     └─ Globální statistiky scorecard                   ║
║                                                        ║
║  🏳️ get_country_profile                                ║
║     └─ Detailní profil země                            ║
║                                                        ║
║  🔄 compare_countries                                  ║
║     └─ Porovnání více zemí                             ║
║                                                        ║
║  📊 analyze_dimension                                  ║
║     └─ Analýza 1 ze 6 genderových dimenzí              ║
║                                                        ║
║  🔍 filter_countries                                   ║
║     └─ Filtr podle regionu/příjmu/skóre               ║
║                                                        ║
║  🏆 get_top_performers                                 ║
║     └─ Nejlepší země                                   ║
║                                                        ║
║  ⚠️ identify_gaps                                      ║
║     └─ Identifikace mezer a výzev                      ║
║                                                        ║
║  💡 get_recommendations                                ║
║     └─ Doporučení pro zemi                             ║
║                                                        ║
║  🏭 sector_analysis                                    ║
║     └─ Analýza podle sektorů                           ║
║                                                        ║
║  👩‍💼 women_leadership_stats                            ║
║     └─ Statistiky ženského lídrovství                  ║
║                                                        ║
╚════════════════════════════════════════════════════════╝{Colors.ENDC}

{Colors.BOLD}{Colors.CYAN}📋 6 GENDEROVÝCH DIMENZÍ:{Colors.ENDC}
  💰 Ekonomická bezpečnost    🏠 Neplacená péče
  🛡️ Genderově založené násilí 🏥 Zdraví
  👩‍💼 Účast a lídrovství       ⚖️ Gender mainstreaming
""")

def main():
    API_KEY = "VLOŽTE_VÁŠ_API_KLÍČ"

    if API_KEY == "VLOŽTE_VÁŠ_API_KLÍČ":
        print_error("Prosím vložte svůj Anthropic API klíč do proměnné API_KEY")
        print(f"\n{Colors.DIM}Otevřete soubor climate_gender_agent.py a nahraďte VLOŽTE_VÁŠ_API_KLÍČ{Colors.ENDC}")
        return

    print_tools_sidebar()

    agent = ClimateGenderAgent(API_KEY)

    demo_queries = [
        "Jaký je globální přehled a které země jsou na tom nejlépe?",
        "Porovnej Keňu, Brazílii a Švédsko - kde jsou největší rozdíly?",
        "Jak je na tom Afrika v oblasti účasti žen na klimatickém rozhodování?",
        "Jaká jsou doporučení pro zlepšení genderové klimatické politiky v Indii?",
        "Která dimenze je globálně nejslabší a proč?",
    ]

    print(f"\n{Colors.BOLD}Ukázkové dotazy:{Colors.ENDC}")
    for i, q in enumerate(demo_queries, 1):
        print(f"  {i}. {q}")

    print(f"\n{Colors.BOLD}Zadejte dotaz (číslo ukázky, vlastní dotaz, nebo 'q'):{Colors.ENDC}")

    while True:
        try:
            user_input = input(f"\n{Colors.CYAN}> {Colors.ENDC}").strip()

            if user_input.lower() == 'q':
                print("Nashledanou! 🌍")
                break

            if user_input in ['1', '2', '3', '4', '5']:
                query = demo_queries[int(user_input) - 1]
            else:
                query = user_input

            if query:
                agent.run(query)

        except KeyboardInterrupt:
            print("\n\nPřerušeno.")
            break
        except Exception as e:
            print_error(str(e))

if __name__ == "__main__":
    main()
