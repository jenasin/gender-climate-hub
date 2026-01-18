# Gender & Climate Intelligence Hub

> Multi-source ReACT Agent for Gender-Responsive Climate Policy Analysis

A research platform that leverages AI agents to analyze gender-climate data from multiple international sources. Built with a ReACT (Reasoning, Acting, Observing) architecture that provides transparent chain-of-thought reasoning.

![Research Platform](https://img.shields.io/badge/Research-Platform-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **6 Data Sources** - UN Women, World Bank, UNDP, Climate Watch, WHO, ILO
- **ReACT Agent** - Transparent reasoning with chain-of-thought visualization
- **Automated Planning** - Agent creates and follows structured analysis plans
- **Computational Tools** - Statistics, correlation, trend analysis, gap analysis
- **Cross-Reference Analysis** - Multi-source data integration
- **Real-time Streaming** - WebSocket-based thought streaming
- **Analysis History** - Persistent storage of all analyses

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                            │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐   │
│  │   History   │  │  Query Input │  │ Chain of Thought  │   │
│  │   Panel     │  │              │  │   Visualization   │   │
│  └─────────────┘  └──────────────┘  └───────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │ WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   ReACT Agent                        │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────────────────┐  │    │
│  │  │ Planner │  │ Tools   │  │ Thought Recorder    │  │    │
│  │  └─────────┘  └─────────┘  └─────────────────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   Data Banks                         │    │
│  │  🏛️ UN Women  📊 World Bank  🎯 UNDP               │    │
│  │  🌡️ Climate   🏥 WHO         👷 ILO                │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Data Sources

| Source | Icon | Description |
|--------|------|-------------|
| UN Women Climate Scorecard | 🏛️ | Gender dimensions of climate policies |
| World Bank Gender Data | 📊 | Economic indicators, employment, education |
| UNDP Human Development | 🎯 | HDI, Gender Inequality Index |
| Climate Watch | 🌡️ | NDC commitments, emissions data |
| WHO Health Data | 🏥 | Maternal health, reproductive health |
| ILO Labour Statistics | 👷 | Labor market, unpaid care work |

## Agent Tools

### Planning Tools
- `create_analysis_plan` - Creates structured analysis plans
- `update_plan_progress` - Tracks plan execution

### Data Tools
- `get_country_profile` - Complete country profile from all sources
- `query_bank` - Query specific data bank
- `compare_countries` - Multi-country comparison
- `get_regional_data` - Regional aggregations

### Computational Tools
- `compute_statistics` - Mean, median, std dev, etc.
- `compute_correlation` - Correlation analysis
- `compute_composite_index` - Weighted index calculation
- `compute_gap_analysis` - Gap-to-target analysis
- `compute_trend` - Trend analysis and predictions

### Analysis Tools
- `cross_reference_analysis` - Multi-source cross-referencing
- `generate_policy_brief` - Policy recommendations

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Anthropic API Key

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/gender-climate-hub.git
cd gender-climate-hub

# Create .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### Running

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
# Server runs on http://localhost:8080
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# App runs on http://localhost:5180
```

Open http://localhost:5180 in your browser.

## Example Queries

- *"Analyze the gender-climate situation in Kenya and compare it with Sweden"*
- *"Perform cross-reference analysis of climate vulnerability and gender inequality in Africa"*
- *"Calculate correlation between HDI and gender climate score for all countries"*
- *"Create a policy brief for Indonesia with specific recommendations"*
- *"Which countries have the largest unpaid care gap and how does it relate to climate vulnerability?"*

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sources` | List all data sources |
| GET | `/api/countries` | List all countries |
| GET | `/api/country/{code}` | Country profile |
| POST | `/api/analyze` | Run analysis (sync) |
| WS | `/ws/analyze` | Run analysis (streaming) |
| GET | `/api/history` | Analysis history |
| GET | `/api/demo-queries` | Demo queries |

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI
- Anthropic Claude API
- WebSockets

**Frontend:**
- React 18
- TypeScript
- Tailwind CSS
- Vite

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Based on UN Women Climate Scorecard methodology and data from:
- UN Women
- World Bank
- UNDP
- Climate Watch
- WHO
- ILO

---

*Built with Claude Code*
