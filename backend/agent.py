"""
ReACT Agent s plánováním, výpočetními nástroji a historií
"""

import anthropic
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from data_banks import DataHub, COUNTRIES, DIMENSIONS, find_country
import statistics
import math

# ═══════════════════════════════════════════════════════════════════════════════
# DATOVÉ STRUKTURY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ThoughtStep:
    """Jeden krok v chain of thought"""
    id: str
    type: str  # "thinking", "action", "observation", "plan", "result"
    content: str
    tool_name: Optional[str] = None
    tool_input: Optional[dict] = None
    tool_output: Optional[Any] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)

@dataclass
class Plan:
    """Plán analýzy"""
    id: str
    goal: str
    steps: List[str]
    current_step: int = 0
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)

@dataclass
class Analysis:
    """Kompletní analýza s historií"""
    id: str
    query: str
    plan: Optional[Plan]
    thoughts: List[ThoughtStep]
    result: Optional[str]
    status: str  # running, completed, error
    created_at: str
    completed_at: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "query": self.query,
            "plan": self.plan.to_dict() if self.plan else None,
            "thoughts": [t.to_dict() for t in self.thoughts],
            "result": self.result,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }

# ═══════════════════════════════════════════════════════════════════════════════
# VÝPOČETNÍ NÁSTROJE
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_statistics(values: List[float]) -> dict:
    """Statistické výpočty"""
    if not values:
        return {"error": "No values provided"}

    return {
        "count": len(values),
        "sum": round(sum(values), 2),
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "range": round(max(values) - min(values), 2),
        "std_dev": round(statistics.stdev(values), 2) if len(values) > 1 else 0,
        "variance": round(statistics.variance(values), 2) if len(values) > 1 else 0
    }

def calculate_correlation(x_values: List[float], y_values: List[float]) -> dict:
    """Výpočet korelace mezi dvěma řadami"""
    if len(x_values) != len(y_values) or len(x_values) < 2:
        return {"error": "Invalid input - need equal length arrays with at least 2 values"}

    n = len(x_values)
    mean_x = sum(x_values) / n
    mean_y = sum(y_values) / n

    covariance = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, y_values)) / n
    std_x = math.sqrt(sum((x - mean_x) ** 2 for x in x_values) / n)
    std_y = math.sqrt(sum((y - mean_y) ** 2 for y in y_values) / n)

    if std_x == 0 or std_y == 0:
        return {"error": "Cannot calculate correlation - zero standard deviation"}

    correlation = covariance / (std_x * std_y)

    # Interpretace
    strength = "weak"
    if abs(correlation) > 0.7:
        strength = "strong"
    elif abs(correlation) > 0.4:
        strength = "moderate"

    direction = "positive" if correlation > 0 else "negative"

    return {
        "correlation_coefficient": round(correlation, 4),
        "strength": strength,
        "direction": direction,
        "interpretation": f"{strength.capitalize()} {direction} correlation",
        "r_squared": round(correlation ** 2, 4),
        "sample_size": n
    }

def calculate_index(indicators: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> dict:
    """Výpočet váženého indexu"""
    if not indicators:
        return {"error": "No indicators provided"}

    if weights is None:
        weights = {k: 1.0 for k in indicators}

    # Normalizace vah
    total_weight = sum(weights.values())
    normalized_weights = {k: v / total_weight for k, v in weights.items()}

    # Výpočet váženého průměru
    weighted_sum = sum(indicators[k] * normalized_weights.get(k, 0) for k in indicators)

    return {
        "composite_index": round(weighted_sum, 2),
        "indicators": indicators,
        "weights_used": {k: round(v, 3) for k, v in normalized_weights.items()},
        "components": {
            k: {"value": v, "weight": round(normalized_weights.get(k, 0), 3), "contribution": round(v * normalized_weights.get(k, 0), 2)}
            for k, v in indicators.items()
        }
    }

def calculate_gap_analysis(current: float, target: float, baseline: Optional[float] = None) -> dict:
    """Analýza mezery mezi aktuálním stavem a cílem"""
    gap = target - current
    gap_percent = (gap / target * 100) if target != 0 else 0

    result = {
        "current_value": current,
        "target_value": target,
        "absolute_gap": round(gap, 2),
        "gap_percentage": round(gap_percent, 2),
        "achievement_rate": round((current / target * 100) if target != 0 else 0, 2)
    }

    if baseline is not None:
        progress = current - baseline
        total_needed = target - baseline
        result["baseline"] = baseline
        result["progress_from_baseline"] = round(progress, 2)
        result["progress_percentage"] = round((progress / total_needed * 100) if total_needed != 0 else 0, 2)

    return result

def calculate_trend(values: List[float], years: List[int]) -> dict:
    """Výpočet trendu pomocí lineární regrese"""
    if len(values) != len(years) or len(values) < 2:
        return {"error": "Invalid input"}

    n = len(values)
    mean_x = sum(years) / n
    mean_y = sum(values) / n

    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(years, values))
    denominator = sum((x - mean_x) ** 2 for x in years)

    if denominator == 0:
        return {"error": "Cannot calculate trend"}

    slope = numerator / denominator
    intercept = mean_y - slope * mean_x

    # Predikce
    last_year = max(years)
    predictions = {
        last_year + 5: round(intercept + slope * (last_year + 5), 2),
        last_year + 10: round(intercept + slope * (last_year + 10), 2)
    }

    # Interpretace
    if abs(slope) < 0.1:
        trend_type = "stable"
    elif slope > 0:
        trend_type = "increasing"
    else:
        trend_type = "decreasing"

    return {
        "slope": round(slope, 4),
        "intercept": round(intercept, 2),
        "trend_type": trend_type,
        "annual_change": round(slope, 2),
        "predictions": predictions,
        "data_points": n
    }

# ═══════════════════════════════════════════════════════════════════════════════
# NÁSTROJE PRO AGENTA
# ═══════════════════════════════════════════════════════════════════════════════

HUB = DataHub()

TOOLS = [
    # Plánovací nástroje
    {
        "name": "create_analysis_plan",
        "description": "Vytvoří strukturovaný plán pro analýzu. VŽDY volej na začátku komplexní analýzy.",
        "input_schema": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "Hlavní cíl analýzy"},
                "steps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Kroky k dosažení cíle"
                }
            },
            "required": ["goal", "steps"]
        }
    },
    {
        "name": "update_plan_progress",
        "description": "Aktualizuje postup v plánu - označ krok jako dokončený.",
        "input_schema": {
            "type": "object",
            "properties": {
                "step_completed": {"type": "integer", "description": "Index dokončeného kroku (0-based)"}
            },
            "required": ["step_completed"]
        }
    },

    # Datové nástroje
    {
        "name": "list_data_sources",
        "description": "Seznam všech dostupných datových zdrojů.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "get_country_profile",
        "description": "Kompletní profil země ze všech zdrojů.",
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
        "description": "Dotaz na konkrétní datovou banku.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bank": {"type": "string", "enum": ["unwomen", "worldbank", "undp", "climate", "who", "ilo"]},
                "country": {"type": "string"}
            },
            "required": ["bank", "country"]
        }
    },
    {
        "name": "compare_countries",
        "description": "Porovnání více zemí.",
        "input_schema": {
            "type": "object",
            "properties": {
                "countries": {"type": "array", "items": {"type": "string"}},
                "banks": {"type": "array", "items": {"type": "string"}, "description": "Volitelně konkrétní banky"}
            },
            "required": ["countries"]
        }
    },
    {
        "name": "get_regional_data",
        "description": "Data pro celý region.",
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "Název regionu (Africa, Europe, Asia...)"}
            },
            "required": ["region"]
        }
    },

    # Výpočetní nástroje
    {
        "name": "compute_statistics",
        "description": "Statistické výpočty - průměr, medián, směrodatná odchylka atd.",
        "input_schema": {
            "type": "object",
            "properties": {
                "values": {"type": "array", "items": {"type": "number"}, "description": "Seznam hodnot"},
                "label": {"type": "string", "description": "Popis dat"}
            },
            "required": ["values"]
        }
    },
    {
        "name": "compute_correlation",
        "description": "Výpočet korelace mezi dvěma proměnnými.",
        "input_schema": {
            "type": "object",
            "properties": {
                "x_values": {"type": "array", "items": {"type": "number"}},
                "y_values": {"type": "array", "items": {"type": "number"}},
                "x_label": {"type": "string"},
                "y_label": {"type": "string"}
            },
            "required": ["x_values", "y_values"]
        }
    },
    {
        "name": "compute_composite_index",
        "description": "Výpočet váženého kompozitního indexu z více indikátorů.",
        "input_schema": {
            "type": "object",
            "properties": {
                "indicators": {"type": "object", "description": "Slovník indikátor: hodnota"},
                "weights": {"type": "object", "description": "Volitelné váhy"}
            },
            "required": ["indicators"]
        }
    },
    {
        "name": "compute_gap_analysis",
        "description": "Analýza mezery mezi aktuálním stavem a cílem.",
        "input_schema": {
            "type": "object",
            "properties": {
                "current": {"type": "number"},
                "target": {"type": "number"},
                "baseline": {"type": "number", "description": "Volitelná výchozí hodnota"}
            },
            "required": ["current", "target"]
        }
    },
    {
        "name": "compute_trend",
        "description": "Výpočet trendu a predikce do budoucnosti.",
        "input_schema": {
            "type": "object",
            "properties": {
                "values": {"type": "array", "items": {"type": "number"}},
                "years": {"type": "array", "items": {"type": "integer"}}
            },
            "required": ["values", "years"]
        }
    },

    # Cross-reference
    {
        "name": "cross_reference_analysis",
        "description": "Křížová analýza mezi datovými zdroji.",
        "input_schema": {
            "type": "object",
            "properties": {
                "analysis_type": {
                    "type": "string",
                    "enum": ["climate_gender_nexus", "economic_health_link", "care_climate_burden", "vulnerability_inequality"]
                },
                "region": {"type": "string", "description": "Volitelný filtr"}
            },
            "required": ["analysis_type"]
        }
    },

    # Report nástroje
    {
        "name": "generate_policy_brief",
        "description": "Vygeneruje policy brief s doporučeními.",
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {"type": "string"}
            },
            "required": ["country"]
        }
    }
]

def execute_tool(name: str, params: dict, current_plan: Optional[Plan] = None) -> tuple[Any, Optional[Plan]]:
    """Spustí nástroj a vrátí výsledek"""

    if name == "create_analysis_plan":
        plan = Plan(
            id=str(uuid.uuid4())[:8],
            goal=params["goal"],
            steps=params["steps"],
            status="in_progress"
        )
        return {
            "status": "Plan created",
            "plan_id": plan.id,
            "goal": plan.goal,
            "steps": [{"index": i, "step": s, "status": "pending"} for i, s in enumerate(plan.steps)]
        }, plan

    if name == "update_plan_progress":
        if current_plan:
            step_idx = params["step_completed"]
            if 0 <= step_idx < len(current_plan.steps):
                current_plan.current_step = step_idx + 1
                if current_plan.current_step >= len(current_plan.steps):
                    current_plan.status = "completed"
                return {
                    "status": "Progress updated",
                    "completed_step": step_idx,
                    "step_description": current_plan.steps[step_idx],
                    "remaining_steps": len(current_plan.steps) - current_plan.current_step
                }, current_plan
        return {"error": "No active plan"}, current_plan

    if name == "list_data_sources":
        return HUB.get_all_sources(), current_plan

    if name == "get_country_profile":
        code, info = find_country(params["country"])
        if not code:
            return {"error": f"Country '{params['country']}' not found"}, current_plan

        profile = {
            "country": info["name"],
            "code": code,
            "region": info["region"],
            "income_level": info["income"],
            "population_millions": info["population"],
            "data_sources": {}
        }

        for bank_id, bank in HUB.banks.items():
            profile["data_sources"][bank_id] = bank.get_country_data(code)

        return profile, current_plan

    if name == "query_bank":
        bank_id = params["bank"]
        if bank_id not in HUB.banks:
            return {"error": f"Invalid bank: {bank_id}"}, current_plan

        code, _ = find_country(params["country"])
        if not code:
            return {"error": f"Country '{params['country']}' not found"}, current_plan

        return HUB.banks[bank_id].get_country_data(code), current_plan

    if name == "compare_countries":
        countries = params["countries"]
        banks_to_use = params.get("banks", list(HUB.banks.keys()))

        result = {"comparison": {}}
        for c in countries:
            code, info = find_country(c)
            if code:
                result["comparison"][info["name"]] = {
                    "code": code,
                    "data": {}
                }
                for bank_id in banks_to_use:
                    if bank_id in HUB.banks:
                        result["comparison"][info["name"]]["data"][bank_id] = HUB.banks[bank_id].get_country_data(code)

        return result, current_plan

    if name == "get_regional_data":
        region = params["region"].lower()
        matching = [c for c in COUNTRIES if region in COUNTRIES[c]["region"].lower()]

        if not matching:
            return {"error": f"Region '{params['region']}' not found"}, current_plan

        result = {
            "region": params["region"],
            "countries_count": len(matching),
            "countries": [COUNTRIES[c]["name"] for c in matching],
            "aggregated_data": {}
        }

        # Agregace některých klíčových metrik
        for bank_id, bank in HUB.banks.items():
            bank_data = [bank.get_country_data(c) for c in matching]
            result["aggregated_data"][bank_id] = {
                "sample_size": len(bank_data),
                "sample_countries": matching[:5]
            }

        return result, current_plan

    # Výpočetní nástroje
    if name == "compute_statistics":
        result = calculate_statistics(params["values"])
        if "label" in params:
            result["label"] = params["label"]
        return result, current_plan

    if name == "compute_correlation":
        result = calculate_correlation(params["x_values"], params["y_values"])
        if "x_label" in params:
            result["x_variable"] = params["x_label"]
        if "y_label" in params:
            result["y_variable"] = params["y_label"]
        return result, current_plan

    if name == "compute_composite_index":
        return calculate_index(params["indicators"], params.get("weights")), current_plan

    if name == "compute_gap_analysis":
        return calculate_gap_analysis(
            params["current"],
            params["target"],
            params.get("baseline")
        ), current_plan

    if name == "compute_trend":
        return calculate_trend(params["values"], params["years"]), current_plan

    if name == "cross_reference_analysis":
        analysis_type = params["analysis_type"]
        region_filter = params.get("region", "").lower()

        countries_to_analyze = list(COUNTRIES.keys())
        if region_filter:
            countries_to_analyze = [c for c in countries_to_analyze if region_filter in COUNTRIES[c]["region"].lower()]

        if analysis_type == "climate_gender_nexus":
            data_points = []
            for code in countries_to_analyze:
                climate_vuln = HUB.banks["climate"].data[code]["climate_vulnerability_index"]
                gender_score = HUB.banks["unwomen"].data[code]["overall_score"]
                data_points.append({
                    "country": COUNTRIES[code]["name"],
                    "climate_vulnerability": climate_vuln,
                    "gender_climate_score": gender_score,
                })

            # Korelace
            x_vals = [d["climate_vulnerability"] for d in data_points]
            y_vals = [d["gender_climate_score"] for d in data_points]
            correlation = calculate_correlation(x_vals, y_vals)

            data_points.sort(key=lambda x: x["climate_vulnerability"], reverse=True)

            return {
                "analysis_type": "Climate-Gender Nexus",
                "countries_analyzed": len(data_points),
                "correlation": correlation,
                "most_vulnerable": data_points[:5],
                "best_performers": sorted(data_points, key=lambda x: x["gender_climate_score"], reverse=True)[:5]
            }, current_plan

        elif analysis_type == "care_climate_burden":
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

            return {
                "analysis_type": "Care-Climate Double Burden",
                "countries_analyzed": len(data_points),
                "highest_burden": data_points[:5],
                "lowest_burden": data_points[-5:]
            }, current_plan

        return {"error": f"Unknown analysis type: {analysis_type}"}, current_plan

    if name == "generate_policy_brief":
        code, info = find_country(params["country"])
        if not code:
            return {"error": f"Country '{params['country']}' not found"}, current_plan

        # Shromáždit data
        unwomen = HUB.banks["unwomen"].data[code]
        undp = HUB.banks["undp"].data[code]
        ilo = HUB.banks["ilo"].data[code]
        climate = HUB.banks["climate"].data[code]

        weak_dims = sorted(unwomen["dimensions"].items(), key=lambda x: x[1])[:2]

        return {
            "title": f"Policy Brief: {info['name']}",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "key_indicators": {
                "gender_climate_score": unwomen["overall_score"],
                "gender_inequality_index": undp["gender_inequality_index"],
                "climate_vulnerability": climate["climate_vulnerability_index"],
                "care_gap": round(ilo["unpaid_care_hours_female"] - ilo["unpaid_care_hours_male"], 1)
            },
            "priority_dimensions": [DIMENSIONS.get(dim, dim) for dim, _ in weak_dims],
            "recommendations": [
                f"Strengthen {DIMENSIONS.get(weak_dims[0][0], weak_dims[0][0])} - current score {weak_dims[0][1]}/100",
                f"Increase women's representation in climate delegations (currently {unwomen['women_in_delegation']}%)",
                f"Address unpaid care inequality ({ilo['unpaid_care_hours_female'] - ilo['unpaid_care_hours_male']:.1f}h gap)",
                f"Integrate gender perspective into NDC (currently {unwomen['ndc_gender_references']} references)"
            ],
            "sdg_alignment": ["SDG 5 (Gender)", "SDG 13 (Climate)", "SDG 8 (Work)"]
        }, current_plan

    return {"error": f"Unknown tool: {name}"}, current_plan


# ═══════════════════════════════════════════════════════════════════════════════
# ReACT AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class GenderClimateAgent:
    """ReACT Agent s plánováním a historií"""

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.max_iterations = 15
        self.analyses: List[Analysis] = []

    def run(self, query: str, on_thought: callable = None) -> Analysis:
        """Spustí analýzu a vrátí kompletní historii"""

        analysis = Analysis(
            id=str(uuid.uuid4())[:8],
            query=query,
            plan=None,
            thoughts=[],
            result=None,
            status="running",
            created_at=datetime.now().isoformat()
        )

        messages = [{"role": "user", "content": query}]

        system_prompt = """Jsi expertní analytik Gender & Climate Intelligence Hub - systému propojujícího 6 datových zdrojů:

🏛️ UN Women Climate Scorecard - genderové dimenze klimatických politik
📊 World Bank Gender Data - ekonomické indikátory
🎯 UNDP Human Development - HDI, Gender Inequality Index
🌡️ Climate Watch - NDC, emise, klimatické cíle
🏥 WHO Health Data - zdravotní indikátory
👷 ILO Labour Statistics - pracovní trh, neplacená práce

TVŮJ POSTUP:
1. VŽDY začni vytvořením plánu pomocí create_analysis_plan
2. Postupuj podle plánu a aktualizuj postup pomocí update_plan_progress
3. Používej výpočetní nástroje (compute_*) pro statistické analýzy
4. Křížově analyzuj data z různých zdrojů
5. Na konci poskytni jasné závěry s čísly

DŮLEŽITÉ:
- Při komplexních analýzách VŽDY vytvoř plán
- Používej výpočetní nástroje pro statistiky a korelace
- Cituj konkrétní čísla a zdroje
- Odpovídej česky"""

        current_plan = None
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

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

                    # Zaznamenat myšlenku
                    thought = ThoughtStep(
                        id=str(uuid.uuid4())[:8],
                        type="thinking",
                        content=block.text
                    )
                    analysis.thoughts.append(thought)
                    if on_thought:
                        on_thought(thought)

                    assistant_content.append({"type": "text", "text": block.text})

                elif block.type == "tool_use":
                    has_tool_use = True
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id

                    # Zaznamenat akci
                    action_thought = ThoughtStep(
                        id=str(uuid.uuid4())[:8],
                        type="action",
                        content=f"Calling {tool_name}",
                        tool_name=tool_name,
                        tool_input=tool_input
                    )
                    analysis.thoughts.append(action_thought)
                    if on_thought:
                        on_thought(action_thought)

                    # Spustit nástroj
                    result, current_plan = execute_tool(tool_name, tool_input, current_plan)

                    # Aktualizovat plán v analýze
                    if current_plan:
                        analysis.plan = current_plan

                    # Zaznamenat výsledek
                    obs_thought = ThoughtStep(
                        id=str(uuid.uuid4())[:8],
                        type="observation",
                        content=f"Result from {tool_name}",
                        tool_name=tool_name,
                        tool_output=result
                    )
                    analysis.thoughts.append(obs_thought)
                    if on_thought:
                        on_thought(obs_thought)

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
                            "content": json.dumps(result, ensure_ascii=False, default=str)
                        }]
                    })
                    assistant_content = []

            if not has_tool_use:
                # Finální odpověď
                result_thought = ThoughtStep(
                    id=str(uuid.uuid4())[:8],
                    type="result",
                    content=final_text
                )
                analysis.thoughts.append(result_thought)
                if on_thought:
                    on_thought(result_thought)

                analysis.result = final_text
                analysis.status = "completed"
                analysis.completed_at = datetime.now().isoformat()
                break

        if analysis.status == "running":
            analysis.status = "error"
            analysis.result = "Max iterations reached"

        self.analyses.append(analysis)
        return analysis

    def get_history(self) -> List[dict]:
        """Vrátí historii všech analýz"""
        return [a.to_dict() for a in self.analyses]

    def get_analysis(self, analysis_id: str) -> Optional[dict]:
        """Vrátí konkrétní analýzu"""
        for a in self.analyses:
            if a.id == analysis_id:
                return a.to_dict()
        return None
