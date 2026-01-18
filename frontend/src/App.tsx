import { useState } from 'react'
import {
  Send, Loader2, Brain, Zap, Eye, CheckCircle2,
  Globe2, ChevronRight,
  ListChecks, FileText,
  Sparkles, ArrowRight, Clock, BarChart3
} from 'lucide-react'

// ═══════════════════════════════════════════════════════════════════════════════
// TYPY
// ═══════════════════════════════════════════════════════════════════════════════

interface ThoughtStep {
  id: string
  type: 'thinking' | 'action' | 'observation' | 'plan' | 'result'
  content: string
  tool_name?: string
  tool_input?: Record<string, unknown>
  tool_output?: unknown
  timestamp: string
}

interface Plan {
  id: string
  goal: string
  steps: string[]
  current_step: number
  status: string
}

interface Analysis {
  id: string
  query: string
  plan?: Plan
  thoughts: ThoughtStep[]
  result?: string
  status: 'running' | 'completed' | 'error'
  created_at: string
  completed_at?: string
}

interface DataSource {
  id: string
  name: string
  icon: string
  color: string
  description: string
}

interface DemoQuery {
  id: number
  query: string
  category: string
}

// ═══════════════════════════════════════════════════════════════════════════════
// DEMO DATA
// ═══════════════════════════════════════════════════════════════════════════════

const DEMO_SOURCES: DataSource[] = [
  { id: 'unwomen', name: 'UN Women Climate Scorecard', icon: '🏛️', color: '#E91E63', description: 'Gender dimensions of climate policies' },
  { id: 'worldbank', name: 'World Bank Gender Data', icon: '📊', color: '#1976D2', description: 'Economic indicators, employment' },
  { id: 'undp', name: 'UNDP Human Development', icon: '🎯', color: '#0097A7', description: 'HDI, Gender Inequality Index' },
  { id: 'climate', name: 'Climate Watch', icon: '🌡️', color: '#388E3C', description: 'NDC commitments, emissions' },
  { id: 'who', name: 'WHO Health Data', icon: '🏥', color: '#0288D1', description: 'Maternal health indicators' },
  { id: 'ilo', name: 'ILO Labour Statistics', icon: '👷', color: '#F57C00', description: 'Labor market, unpaid care' },
]

const DEMO_QUERIES: DemoQuery[] = [
  { id: 1, query: "Analyzuj genderově-klimatickou situaci v Keni a porovnej ji se Švédskem.", category: "comparison" },
  { id: 2, query: "Proveď křížovou analýzu vztahu klimatické zranitelnosti a genderové nerovnosti v Africe.", category: "cross_reference" },
  { id: 3, query: "Vypočítej korelaci mezi HDI a gender climate score pro všechny země.", category: "computation" },
  { id: 4, query: "Vytvoř policy brief pro Indonésii s konkrétními doporučeními.", category: "policy" },
  { id: 5, query: "Které země mají největší mezeru v neplacené péči a jak to souvisí s klimatickou zranitelností?", category: "analysis" },
  { id: 6, query: "Jaký je průměrný gender climate score pro země s nízkými příjmy vs vysokými příjmy?", category: "statistics" },
]

const DEMO_ANALYSIS: Analysis = {
  id: "demo001",
  query: "Analyzuj genderově-klimatickou situaci v Keni a porovnej ji se Švédskem.",
  status: "completed",
  created_at: new Date().toISOString(),
  plan: {
    id: "plan001",
    goal: "Provést komparativní analýzu genderově-klimatických politik Keni a Švédska",
    steps: [
      "Získat profil Keni ze všech datových zdrojů",
      "Získat profil Švédska ze všech datových zdrojů",
      "Vypočítat statistické porovnání klíčových indikátorů",
      "Identifikovat hlavní rozdíly a podobnosti",
      "Formulovat závěry a doporučení"
    ],
    current_step: 5,
    status: "completed"
  },
  thoughts: [
    {
      id: "t1",
      type: "thinking",
      content: "Pro komplexní komparativní analýzu potřebuji data z více zdrojů. Začnu vytvořením plánu a poté systematicky získám data pro obě země.",
      timestamp: new Date(Date.now() - 50000).toISOString()
    },
    {
      id: "t2",
      type: "action",
      content: "Vytvářím strukturovaný plán analýzy",
      tool_name: "create_analysis_plan",
      tool_input: { goal: "Komparativní analýza Keňa vs Švédsko", steps: ["..."] },
      timestamp: new Date(Date.now() - 45000).toISOString()
    },
    {
      id: "t3",
      type: "action",
      content: "Získávám kompletní profil Keni",
      tool_name: "get_country_profile",
      tool_input: { country: "Kenya" },
      tool_output: {
        country: "Keňa",
        gender_climate_score: 47.2,
        climate_vulnerability: 0.68,
        gender_inequality_index: 0.518
      },
      timestamp: new Date(Date.now() - 40000).toISOString()
    },
    {
      id: "t4",
      type: "observation",
      content: "Keňa má Gender Climate Score 47.2/100, vysokou klimatickou zranitelnost (0.68) a Gender Inequality Index 0.518. Země má aktivní gender focal point a 28 referencí na gender v NDC.",
      timestamp: new Date(Date.now() - 35000).toISOString()
    },
    {
      id: "t5",
      type: "action",
      content: "Získávám kompletní profil Švédska",
      tool_name: "get_country_profile",
      tool_input: { country: "Sweden" },
      tool_output: {
        country: "Švédsko",
        gender_climate_score: 78.5,
        climate_vulnerability: 0.24,
        gender_inequality_index: 0.039
      },
      timestamp: new Date(Date.now() - 30000).toISOString()
    },
    {
      id: "t6",
      type: "action",
      content: "Vypočítávám statistické porovnání",
      tool_name: "compute_statistics",
      tool_input: { values: [47.2, 78.5], label: "Gender Climate Score comparison" },
      tool_output: { mean: 62.85, difference: 31.3, gap_percentage: 39.9 },
      timestamp: new Date(Date.now() - 25000).toISOString()
    },
    {
      id: "t7",
      type: "observation",
      content: "Švédsko dosahuje o 31.3 bodů vyššího Gender Climate Score než Keňa (78.5 vs 47.2). Rozdíl v Gender Inequality Index je dramatický: Švédsko 0.039 vs Keňa 0.518.",
      timestamp: new Date(Date.now() - 20000).toISOString()
    }
  ],
  result: `## Komparativní analýza: Keňa vs Švédsko

### Klíčové indikátory

| Indikátor | Keňa | Švédsko | Rozdíl |
|-----------|------|---------|--------|
| Gender Climate Score | 47.2 | 78.5 | +31.3 |
| Climate Vulnerability | 0.68 | 0.24 | -0.44 |
| Gender Inequality Index | 0.518 | 0.039 | -0.479 |
| Ženy v klimatické delegaci | 24% | 48% | +24 p.b. |
| HDI | 0.601 | 0.947 | +0.346 |

### Hlavní zjištění

1. **Genderová rovnost**: Švédsko patří mezi světové lídry s GII 0.039, zatímco Keňa má GII 0.518
2. **Klimatická zranitelnost**: Keňa je 2.8× více zranitelná vůči klimatickým změnám
3. **Politická reprezentace**: Švédsko má dvojnásobné zastoupení žen v klimatických delegacích

### Doporučení pro Keňu

- Posílit zastoupení žen v klimatickém rozhodování
- Rozšířit genderové reference v NDC
- Investovat do snížení klimatické zranitelnosti žen
- Čerpat z best practices severských zemí

*Analýza využila data z 6 zdrojů: UN Women, World Bank, UNDP, Climate Watch, WHO, ILO*`
}

// ═══════════════════════════════════════════════════════════════════════════════
// KOMPONENTY
// ═══════════════════════════════════════════════════════════════════════════════

function DataSourceCard({ source }: { source: DataSource }) {
  return (
    <div
      className="flex items-center gap-3 px-4 py-3 bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-all cursor-default min-w-[200px]"
      style={{ borderTopColor: source.color, borderTopWidth: 3 }}
    >
      <span className="text-xl">{source.icon}</span>
      <div className="flex-1 min-w-0">
        <div className="font-medium text-slate-700 text-sm" style={{ fontFamily: 'var(--font-serif)' }}>{source.name}</div>
        <div className="text-xs text-slate-400 truncate">{source.description}</div>
      </div>
    </div>
  )
}

function PlanCard({ plan }: { plan: Plan }) {
  const progress = plan.steps.length > 0 ? (plan.current_step / plan.steps.length) * 100 : 0

  return (
    <div className="card p-5 border-l-4 border-l-violet-500">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-violet-100 flex items-center justify-center">
            <ListChecks className="w-4 h-4 text-violet-600" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-800">Plán analýzy</h3>
            <p className="text-xs text-slate-500">{plan.steps.length} kroků</p>
          </div>
        </div>
        <span className={`text-xs px-2.5 py-1 rounded-full border font-medium ${
          plan.status === 'completed' ? 'status-completed' :
          plan.status === 'in_progress' ? 'status-running' : 'bg-slate-50 text-slate-600 border-slate-200'
        }`}>
          {plan.status === 'completed' ? 'Dokončeno' : plan.status === 'in_progress' ? 'Probíhá' : 'Čeká'}
        </span>
      </div>

      <div className="h-1.5 bg-slate-100 rounded-full mb-4 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-violet-500 to-purple-500 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      <p className="text-sm text-slate-600 mb-4 italic">„{plan.goal}"</p>

      <div className="space-y-2">
        {plan.steps.map((step, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3 text-sm p-2 rounded-lg transition-colors ${
              idx < plan.current_step ? 'bg-emerald-50' :
              idx === plan.current_step ? 'bg-blue-50' : 'bg-slate-50'
            }`}
          >
            <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${
              idx < plan.current_step ? 'bg-emerald-500 text-white' :
              idx === plan.current_step ? 'bg-blue-500 text-white' : 'bg-slate-200 text-slate-500'
            }`}>
              {idx < plan.current_step ? (
                <CheckCircle2 className="w-3 h-3" />
              ) : idx === plan.current_step ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <span className="text-xs">{idx + 1}</span>
              )}
            </div>
            <span className={`${
              idx < plan.current_step ? 'text-emerald-700' :
              idx === plan.current_step ? 'text-blue-700 font-medium' : 'text-slate-500'
            }`}>{step}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function ThoughtCard({ thought, index }: { thought: ThoughtStep; index: number }) {
  const [expanded, setExpanded] = useState(false)

  const config = {
    thinking: { icon: Brain, label: 'Reasoning', bg: 'bg-amber-50', border: 'border-amber-200', iconBg: 'bg-amber-100', iconColor: 'text-amber-600', accent: 'text-amber-700' },
    action: { icon: Zap, label: 'Action', bg: 'bg-sky-50', border: 'border-sky-200', iconBg: 'bg-sky-100', iconColor: 'text-sky-600', accent: 'text-sky-700' },
    observation: { icon: Eye, label: 'Observation', bg: 'bg-emerald-50', border: 'border-emerald-200', iconBg: 'bg-emerald-100', iconColor: 'text-emerald-600', accent: 'text-emerald-700' },
    plan: { icon: ListChecks, label: 'Plan', bg: 'bg-violet-50', border: 'border-violet-200', iconBg: 'bg-violet-100', iconColor: 'text-violet-600', accent: 'text-violet-700' },
    result: { icon: Sparkles, label: 'Result', bg: 'bg-gradient-to-br from-emerald-50 to-teal-50', border: 'border-emerald-300', iconBg: 'bg-emerald-500', iconColor: 'text-white', accent: 'text-emerald-800' }
  }

  const c = config[thought.type]
  const Icon = c.icon

  return (
    <div className={`thought-step rounded-xl border ${c.border} ${c.bg} p-4`} style={{ animationDelay: `${index * 50}ms` }}>
      <div className="flex items-start gap-3">
        <div className={`w-8 h-8 rounded-lg ${c.iconBg} flex items-center justify-center flex-shrink-0`}>
          <Icon className={`w-4 h-4 ${c.iconColor}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <span className={`text-sm font-semibold ${c.accent}`}>{c.label}</span>
              {thought.tool_name && (
                <code className="text-xs bg-white/60 px-2 py-0.5 rounded border border-slate-200 text-slate-600">
                  {thought.tool_name}
                </code>
              )}
            </div>
            <span className="text-xs text-slate-400 mono">
              {new Date(thought.timestamp).toLocaleTimeString('cs-CZ', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </span>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed">{thought.content}</p>
          {(thought.tool_input !== undefined || thought.tool_output !== undefined) && (
            <>
              <button
                onClick={() => setExpanded(!expanded)}
                className="flex items-center gap-1.5 text-xs text-slate-500 mt-3 hover:text-slate-700 transition-colors"
              >
                <ChevronRight className={`w-3.5 h-3.5 transition-transform ${expanded ? 'rotate-90' : ''}`} />
                {expanded ? 'Skrýt data' : 'Zobrazit data'}
              </button>
              {expanded && (
                <div className="mt-3 space-y-2 animate-fadeInUp">
                  {thought.tool_input && (
                    <div className="bg-white/80 rounded-lg p-3 border border-slate-200">
                      <div className="text-xs font-medium text-slate-500 mb-1.5 flex items-center gap-1">
                        <ArrowRight className="w-3 h-3" /> Input
                      </div>
                      <pre className="text-xs text-slate-700 overflow-x-auto mono">
                        {JSON.stringify(thought.tool_input, null, 2)}
                      </pre>
                    </div>
                  )}
                  {thought.tool_output !== undefined && (
                    <div className="bg-white/80 rounded-lg p-3 border border-slate-200">
                      <div className="text-xs font-medium text-slate-500 mb-1.5 flex items-center gap-1">
                        <ArrowRight className="w-3 h-3 rotate-180" /> Output
                      </div>
                      <pre className="text-xs text-slate-700 overflow-x-auto max-h-48 mono">
                        {JSON.stringify(thought.tool_output, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function AnalysisView({ analysis }: { analysis: Analysis }) {
  return (
    <div className="space-y-6">
      <div className="card p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <code className="text-xs bg-slate-100 px-2 py-1 rounded text-slate-500">#{analysis.id}</code>
              <span className={`text-xs px-2.5 py-1 rounded-full border font-medium ${
                analysis.status === 'completed' ? 'status-completed' :
                analysis.status === 'running' ? 'status-running' : 'status-error'
              }`}>
                {analysis.status === 'completed' ? 'Dokončeno' : 'Probíhá...'}
              </span>
            </div>
            <h2 className="text-lg font-semibold text-slate-800 leading-snug">{analysis.query}</h2>
            <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                {new Date(analysis.created_at).toLocaleString('cs-CZ')}
              </span>
              <span className="flex items-center gap-1">
                <Brain className="w-3.5 h-3.5" />
                {analysis.thoughts.length} kroků
              </span>
            </div>
          </div>
        </div>
      </div>

      {analysis.plan && <PlanCard plan={analysis.plan} />}

      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
          <BarChart3 className="w-4 h-4" />
          Chain of Thought
        </h3>
        {analysis.thoughts.map((thought, idx) => (
          <ThoughtCard key={thought.id} thought={thought} index={idx} />
        ))}
      </div>

      {analysis.result && (
        <div className="card p-6 border-l-4 border-l-emerald-500 bg-gradient-to-br from-emerald-50 to-white">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-emerald-800">Výsledek analýzy</h3>
              <p className="text-xs text-emerald-600">Kompletní odpověď</p>
            </div>
          </div>
          <div className="prose prose-sm max-w-none text-slate-700">
            <div dangerouslySetInnerHTML={{ __html: analysis.result.replace(/\n/g, '<br/>').replace(/\|/g, ' | ').replace(/#{1,3}\s/g, () => `<strong>`) }} />
          </div>
        </div>
      )}
    </div>
  )
}

function HistoryPanel({ history, onSelect, selectedId }: { history: Analysis[]; onSelect: (a: Analysis) => void; selectedId?: string }) {
  return (
    <aside className="w-80 bg-white border-r border-slate-200 flex flex-col">
      <div className="p-5 border-b border-slate-200">
        <h2 className="font-semibold text-slate-800" style={{ fontFamily: 'var(--font-serif)' }}>Historie analýz</h2>
        <p className="text-xs text-slate-400">{history.length} provedených analýz</p>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {history.map((analysis) => (
          <button
            key={analysis.id}
            onClick={() => onSelect(analysis)}
            className={`w-full text-left p-4 rounded-xl transition-all ${
              selectedId === analysis.id ? 'bg-slate-100 border-2 border-slate-300' : 'bg-slate-50 border-2 border-transparent hover:bg-slate-100'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <code className="text-xs text-slate-400">#{analysis.id}</code>
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
            </div>
            <p className="text-sm text-slate-700 line-clamp-2" style={{ fontFamily: 'var(--font-serif)' }}>{analysis.query}</p>
          </button>
        ))}
      </div>
    </aside>
  )
}

function EmptyState({ demoQueries, onSelect }: { demoQueries: DemoQuery[]; onSelect: (q: string) => void }) {
  const categoryConfig: Record<string, { label: string; icon: string; color: string; border: string }> = {
    comparison: { label: 'Komparativní studie', icon: '⚖️', color: 'bg-indigo-50 text-indigo-800', border: 'border-indigo-200 hover:border-indigo-400' },
    cross_reference: { label: 'Křížová analýza', icon: '🔗', color: 'bg-violet-50 text-violet-800', border: 'border-violet-200 hover:border-violet-400' },
    computation: { label: 'Kvantitativní výzkum', icon: '📐', color: 'bg-amber-50 text-amber-800', border: 'border-amber-200 hover:border-amber-400' },
    policy: { label: 'Policy analýza', icon: '📋', color: 'bg-emerald-50 text-emerald-800', border: 'border-emerald-200 hover:border-emerald-400' },
    analysis: { label: 'Exploratorní analýza', icon: '🔍', color: 'bg-rose-50 text-rose-800', border: 'border-rose-200 hover:border-rose-400' },
    statistics: { label: 'Deskriptivní statistika', icon: '📊', color: 'bg-sky-50 text-sky-800', border: 'border-sky-200 hover:border-sky-400' }
  }

  return (
    <div className="flex flex-col items-center justify-center py-12 px-8">
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 text-sm text-slate-500 mb-4">
          <div className="w-8 h-px bg-slate-300" />
          <span className="uppercase tracking-widest text-xs">Research Interface</span>
          <div className="w-8 h-px bg-slate-300" />
        </div>
        <h2 className="text-3xl font-semibold text-slate-800 mb-3" style={{ fontFamily: 'var(--font-serif)' }}>
          Zahájit novou analýzu
        </h2>
        <p className="text-slate-500 max-w-lg mx-auto leading-relaxed" style={{ fontFamily: 'var(--font-serif)' }}>
          Vyberte výzkumnou otázku z připravených šablon pro multi-dimenzionální analýzu genderově-klimatických dat.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 max-w-4xl w-full">
        {demoQueries.map((demo) => {
          const config = categoryConfig[demo.category]
          return (
            <button
              key={demo.id}
              onClick={() => onSelect(demo.query)}
              className={`group text-left p-5 bg-white rounded-xl border-2 ${config.border} transition-all duration-200 hover:shadow-lg`}
            >
              <div className="flex items-start gap-4">
                <div className={`w-10 h-10 rounded-lg ${config.color} flex items-center justify-center text-lg flex-shrink-0`}>
                  {config.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${config.color}`}>{config.label}</span>
                  <p className="text-slate-700 leading-relaxed mt-2 group-hover:text-slate-900" style={{ fontFamily: 'var(--font-serif)', fontSize: '0.95rem' }}>
                    „{demo.query}"
                  </p>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-300 group-hover:text-slate-500 group-hover:translate-x-1 transition-all" />
              </div>
            </button>
          )
        })}
      </div>

      <div className="mt-10 text-center">
        <p className="text-xs text-slate-400 uppercase tracking-wider">
          Powered by ReACT Agent Architecture • 6 Data Sources • 50+ Indicators
        </p>
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
// HLAVNÍ APLIKACE
// ═══════════════════════════════════════════════════════════════════════════════

export default function App() {
  const [currentAnalysis, setCurrentAnalysis] = useState<Analysis | null>(null)
  const [history] = useState<Analysis[]>([DEMO_ANALYSIS])
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const runDemo = (q: string) => {
    setQuery(q)
    setIsLoading(true)

    // Simulace analýzy
    setTimeout(() => {
      setCurrentAnalysis(DEMO_ANALYSIS)
      setIsLoading(false)
    }, 1500)
  }

  return (
    <div className="h-screen flex flex-col bg-slate-50">
      <header className="bg-white border-b border-slate-200 px-6 py-5">
        <div className="max-w-screen-2xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-5">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center shadow-xl">
              <Globe2 className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl text-slate-800" style={{ fontFamily: 'var(--font-serif)', fontWeight: 600 }}>
                Gender & Climate Intelligence Hub
              </h1>
              <p className="text-sm text-slate-500 tracking-wide">
                Multi-source ReACT Agent • Automated Planning • Computational Analysis
              </p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <span className="text-xs text-slate-400 uppercase tracking-wider bg-amber-100 text-amber-700 px-3 py-1 rounded-full">
              Demo Mode
            </span>
            <a
              href="https://github.com/jenasin/gender-climate-hub"
              target="_blank"
              className="text-sm text-slate-500 hover:text-slate-700"
            >
              GitHub →
            </a>
          </div>
        </div>
      </header>

      <div className="bg-slate-100/50 border-b border-slate-200 px-6 py-4">
        <div className="max-w-screen-2xl mx-auto flex gap-3 overflow-x-auto">
          {DEMO_SOURCES.map(source => (
            <DataSourceCard key={source.id} source={source} />
          ))}
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden max-w-screen-2xl mx-auto w-full">
        <HistoryPanel history={history} onSelect={setCurrentAnalysis} selectedId={currentAnalysis?.id} />

        <main className="flex-1 flex flex-col overflow-hidden bg-slate-50">
          <div className="flex-1 overflow-y-auto p-6">
            {currentAnalysis ? (
              <AnalysisView analysis={currentAnalysis} />
            ) : (
              <EmptyState demoQueries={DEMO_QUERIES} onSelect={runDemo} />
            )}
          </div>

          <div className="border-t border-slate-200 bg-white p-5">
            <div className="max-w-4xl mx-auto">
              <label className="text-xs uppercase tracking-wider text-slate-400 font-medium mb-2 block">
                Výzkumná otázka
              </label>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && runDemo(query)}
                  placeholder="Formulujte dotaz pro multi-dimenzionální analýzu..."
                  className="flex-1 bg-slate-50 border-2 border-slate-200 rounded-xl px-5 py-3.5 text-slate-800 placeholder:text-slate-400"
                  style={{ fontFamily: 'var(--font-serif)' }}
                />
                <button
                  onClick={() => runDemo(query)}
                  disabled={!query.trim() || isLoading}
                  className="bg-slate-800 hover:bg-slate-900 disabled:bg-slate-300 text-white px-6 py-3.5 rounded-xl font-medium flex items-center gap-2"
                >
                  {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                  {isLoading ? 'Analyzuji...' : 'Spustit analýzu'}
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
