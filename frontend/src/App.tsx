import { useState, useEffect, useRef } from 'react'
import {
  Send, Loader2, Brain, Zap, Eye, CheckCircle2,
  History, Database, Globe2, ChevronRight, Trash2,
  ListChecks, Calculator, FileText, AlertCircle,
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
        <div className="text-xs text-slate-400 truncate">{source.description.split(' - ')[0]}</div>
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

      {/* Progress bar */}
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
    thinking: {
      icon: Brain,
      label: 'Reasoning',
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      iconBg: 'bg-amber-100',
      iconColor: 'text-amber-600',
      accent: 'text-amber-700'
    },
    action: {
      icon: Zap,
      label: 'Action',
      bg: 'bg-sky-50',
      border: 'border-sky-200',
      iconBg: 'bg-sky-100',
      iconColor: 'text-sky-600',
      accent: 'text-sky-700'
    },
    observation: {
      icon: Eye,
      label: 'Observation',
      bg: 'bg-emerald-50',
      border: 'border-emerald-200',
      iconBg: 'bg-emerald-100',
      iconColor: 'text-emerald-600',
      accent: 'text-emerald-700'
    },
    plan: {
      icon: ListChecks,
      label: 'Plan',
      bg: 'bg-violet-50',
      border: 'border-violet-200',
      iconBg: 'bg-violet-100',
      iconColor: 'text-violet-600',
      accent: 'text-violet-700'
    },
    result: {
      icon: Sparkles,
      label: 'Result',
      bg: 'bg-gradient-to-br from-emerald-50 to-teal-50',
      border: 'border-emerald-300',
      iconBg: 'bg-emerald-500',
      iconColor: 'text-white',
      accent: 'text-emerald-800'
    }
  }

  const c = config[thought.type]
  const Icon = c.icon

  return (
    <div
      className={`thought-step rounded-xl border ${c.border} ${c.bg} p-4`}
      style={{ animationDelay: `${index * 50}ms` }}
    >
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

          {thought.type === 'result' ? (
            <div className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed mt-2">
              {thought.content}
            </div>
          ) : (
            <>
              <p className="text-sm text-slate-600 line-clamp-3 leading-relaxed">{thought.content}</p>

              {(thought.tool_input || thought.tool_output) && (
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
                      {thought.tool_output && (
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
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function AnalysisView({ analysis }: { analysis: Analysis }) {
  const [showAllThoughts, setShowAllThoughts] = useState(false)
  const displayedThoughts = showAllThoughts ? analysis.thoughts : analysis.thoughts.slice(-6)
  const hiddenCount = analysis.thoughts.length - 6

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <code className="text-xs bg-slate-100 px-2 py-1 rounded text-slate-500">#{analysis.id}</code>
              <span className={`text-xs px-2.5 py-1 rounded-full border font-medium ${
                analysis.status === 'completed' ? 'status-completed' :
                analysis.status === 'running' ? 'status-running' : 'status-error'
              }`}>
                {analysis.status === 'running' ? 'Probíhá...' :
                 analysis.status === 'completed' ? 'Dokončeno' : 'Chyba'}
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

      {/* Plan */}
      {analysis.plan && <PlanCard plan={analysis.plan} />}

      {/* Chain of Thought */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Chain of Thought
          </h3>
          {hiddenCount > 0 && !showAllThoughts && (
            <button
              onClick={() => setShowAllThoughts(true)}
              className="text-xs text-blue-600 hover:text-blue-700 font-medium"
            >
              Zobrazit všech {analysis.thoughts.length} kroků
            </button>
          )}
        </div>

        {!showAllThoughts && hiddenCount > 0 && (
          <button
            onClick={() => setShowAllThoughts(true)}
            className="w-full py-2 text-sm text-slate-500 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            + {hiddenCount} skrytých kroků
          </button>
        )}

        {displayedThoughts.map((thought, idx) => (
          <ThoughtCard key={thought.id} thought={thought} index={idx} />
        ))}

        {analysis.status === 'running' && (
          <div className="flex items-center justify-center gap-3 py-6 text-slate-500">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-blue-500 rounded-full typing-dot" />
              <span className="w-2 h-2 bg-blue-500 rounded-full typing-dot" />
              <span className="w-2 h-2 bg-blue-500 rounded-full typing-dot" />
            </div>
            <span className="text-sm">Agent přemýšlí...</span>
          </div>
        )}
      </div>

      {/* Final Result */}
      {analysis.result && analysis.status === 'completed' && (
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
          <div className="text-slate-700 whitespace-pre-wrap leading-relaxed">
            {analysis.result}
          </div>
        </div>
      )}
    </div>
  )
}

function HistoryPanel({
  history,
  onSelect,
  onClear,
  selectedId
}: {
  history: Analysis[]
  onSelect: (a: Analysis) => void
  onClear: () => void
  selectedId?: string
}) {
  return (
    <aside className="w-80 bg-white border-r border-slate-200 flex flex-col">
      <div className="p-5 border-b border-slate-200">
        <div className="flex items-center justify-between mb-1">
          <h2 className="font-semibold text-slate-800" style={{ fontFamily: 'var(--font-serif)' }}>
            Historie analýz
          </h2>
          {history.length > 0 && (
            <button
              onClick={onClear}
              className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
              title="Smazat historii"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
        <p className="text-xs text-slate-400">
          {history.length > 0 ? `${history.length} provedených analýz` : 'Archiv výzkumných dotazů'}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {history.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-4">
              <History className="w-8 h-8 text-slate-300" />
            </div>
            <p className="text-sm text-slate-500 mb-1">Prázdná historie</p>
            <p className="text-xs text-slate-400">Provedené analýzy se zobrazí zde</p>
          </div>
        ) : (
          history.map((analysis, idx) => (
            <button
              key={analysis.id}
              onClick={() => onSelect(analysis)}
              className={`w-full text-left p-4 rounded-xl transition-all ${
                selectedId === analysis.id
                  ? 'bg-slate-100 border-2 border-slate-300 shadow-sm'
                  : 'bg-slate-50 border-2 border-transparent hover:bg-slate-100 hover:border-slate-200'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <code className="text-xs text-slate-400 font-medium">#{analysis.id}</code>
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  analysis.status === 'completed' ? 'bg-emerald-400' :
                  analysis.status === 'running' ? 'bg-blue-400 animate-pulse' : 'bg-red-400'
                }`} />
              </div>
              <p className="text-sm text-slate-700 line-clamp-2 leading-relaxed mb-2" style={{ fontFamily: 'var(--font-serif)' }}>
                {analysis.query}
              </p>
              <div className="flex items-center gap-3 text-xs text-slate-400">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {new Date(analysis.created_at).toLocaleString('cs-CZ', {
                    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
                  })}
                </span>
                <span className="flex items-center gap-1">
                  <Brain className="w-3 h-3" />
                  {analysis.thoughts.length}
                </span>
              </div>
            </button>
          ))
        )}
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
      {/* Academic header */}
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
          Vyberte výzkumnou otázku z připravených šablon, nebo formulujte vlastní dotaz
          pro multi-dimenzionální analýzu genderově-klimatických dat.
        </p>
      </div>

      {/* Query cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 max-w-4xl w-full">
        {demoQueries.map((demo, idx) => {
          const config = categoryConfig[demo.category] || { label: demo.category, icon: '📄', color: 'bg-slate-50 text-slate-700', border: 'border-slate-200' }
          return (
            <button
              key={demo.id}
              onClick={() => onSelect(demo.query)}
              className={`group text-left p-5 bg-white rounded-xl border-2 ${config.border} transition-all duration-200 hover:shadow-lg`}
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              <div className="flex items-start gap-4">
                <div className={`w-10 h-10 rounded-lg ${config.color} flex items-center justify-center text-lg flex-shrink-0`}>
                  {config.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${config.color}`}>
                      {config.label}
                    </span>
                  </div>
                  <p className="text-slate-700 leading-relaxed group-hover:text-slate-900 transition-colors" style={{ fontFamily: 'var(--font-serif)', fontSize: '0.95rem' }}>
                    „{demo.query}"
                  </p>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-300 group-hover:text-slate-500 group-hover:translate-x-1 transition-all flex-shrink-0 mt-1" />
              </div>
            </button>
          )
        })}
      </div>

      {/* Footer note */}
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
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentAnalysis, setCurrentAnalysis] = useState<Analysis | null>(null)
  const [history, setHistory] = useState<Analysis[]>([])
  const [dataSources, setDataSources] = useState<DataSource[]>([])
  const [demoQueries, setDemoQueries] = useState<DemoQuery[]>([])
  const [error, setError] = useState<string | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const thoughtsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetch('/api/sources').then(res => res.json()).then(setDataSources).catch(console.error)
    fetch('/api/demo-queries').then(res => res.json()).then(setDemoQueries).catch(console.error)
    fetch('/api/history').then(res => res.json()).then(setHistory).catch(console.error)
  }, [])

  useEffect(() => {
    thoughtsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentAnalysis?.thoughts])

  const runAnalysis = async () => {
    if (!query.trim() || isLoading) return

    setIsLoading(true)
    setError(null)

    const ws = new WebSocket(`ws://${window.location.host}/ws/analyze`)
    wsRef.current = ws

    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'query', query: query.trim() }))
    }

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)

      if (message.type === 'start') {
        setCurrentAnalysis({
          id: 'running',
          query: message.query,
          thoughts: [],
          status: 'running',
          created_at: message.timestamp
        })
      }

      if (message.type === 'thought') {
        setCurrentAnalysis(prev => {
          if (!prev) return prev

          let plan = prev.plan
          if (message.data.tool_name === 'create_analysis_plan' && message.data.tool_output) {
            const output = message.data.tool_output
            plan = {
              id: output.plan_id,
              goal: output.goal,
              steps: output.steps.map((s: { step: string }) => s.step),
              current_step: 0,
              status: 'in_progress'
            }
          }
          if (message.data.tool_name === 'update_plan_progress' && message.data.tool_output && plan) {
            plan = {
              ...plan,
              current_step: message.data.tool_output.completed_step + 1,
              status: message.data.tool_output.remaining_steps === 0 ? 'completed' : 'in_progress'
            }
          }

          return { ...prev, plan, thoughts: [...prev.thoughts, message.data] }
        })
      }

      if (message.type === 'complete') {
        setCurrentAnalysis(message.data)
        setHistory(prev => [message.data, ...prev])
        setIsLoading(false)
        setQuery('')
        ws.close()
      }

      if (message.type === 'error') {
        setError(message.message)
        setIsLoading(false)
        ws.close()
      }
    }

    ws.onerror = () => {
      setError('Nepodařilo se připojit k serveru')
      setIsLoading(false)
    }

    ws.onclose = () => { wsRef.current = null }
  }

  const clearHistory = async () => {
    await fetch('/api/history', { method: 'DELETE' })
    setHistory([])
    setCurrentAnalysis(null)
  }

  return (
    <div className="h-screen flex flex-col bg-slate-50">
      {/* Header */}
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
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Database className="w-4 h-4" />
              <span>{dataSources.length} Data Sources</span>
            </div>
            <div className="h-8 w-px bg-slate-200" />
            <div className="text-xs text-slate-400 uppercase tracking-wider">
              Research Platform v1.0
            </div>
          </div>
        </div>
      </header>

      {/* Data Sources Bar */}
      <div className="bg-slate-100/50 border-b border-slate-200 px-6 py-4">
        <div className="max-w-screen-2xl mx-auto">
          <div className="flex gap-3 overflow-x-auto pb-1">
            {dataSources.map(source => (
              <DataSourceCard key={source.id} source={source} />
            ))}
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden max-w-screen-2xl mx-auto w-full">
        {/* History Sidebar */}
        <HistoryPanel
          history={history}
          onSelect={setCurrentAnalysis}
          onClear={clearHistory}
          selectedId={currentAnalysis?.id}
        />

        {/* Main Content */}
        <main className="flex-1 flex flex-col overflow-hidden bg-slate-50">
          <div className="flex-1 overflow-y-auto p-6">
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                <span className="text-red-700">{error}</span>
              </div>
            )}

            {currentAnalysis ? (
              <AnalysisView analysis={currentAnalysis} />
            ) : (
              <EmptyState demoQueries={demoQueries} onSelect={setQuery} />
            )}
            <div ref={thoughtsEndRef} />
          </div>

          {/* Input Bar */}
          <div className="border-t border-slate-200 bg-white p-5">
            <div className="max-w-4xl mx-auto">
              <div className="mb-2">
                <label className="text-xs uppercase tracking-wider text-slate-400 font-medium">
                  Výzkumná otázka
                </label>
              </div>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && runAnalysis()}
                  placeholder="Formulujte dotaz pro multi-dimenzionální analýzu..."
                  className="flex-1 bg-slate-50 border-2 border-slate-200 rounded-xl px-5 py-3.5 text-slate-800 placeholder:text-slate-400 focus:border-slate-400 transition-colors"
                  style={{ fontFamily: 'var(--font-serif)', fontSize: '1rem' }}
                  disabled={isLoading}
                />
                <button
                  onClick={runAnalysis}
                  disabled={!query.trim() || isLoading}
                  className="bg-slate-800 hover:bg-slate-900 disabled:bg-slate-300 text-white px-6 py-3.5 rounded-xl font-medium flex items-center gap-2 transition-colors shadow-lg shadow-slate-800/20"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Analyzuji...
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      Spustit analýzu
                    </>
                  )}
                </button>
              </div>

              <div className="flex items-center justify-center gap-8 mt-4 pt-4 border-t border-slate-100">
                <span className="flex items-center gap-2 text-xs text-slate-400">
                  <Calculator className="w-4 h-4" />
                  <span>Statistické výpočty</span>
                </span>
                <span className="flex items-center gap-2 text-xs text-slate-400">
                  <ListChecks className="w-4 h-4" />
                  <span>Automatické plánování</span>
                </span>
                <span className="flex items-center gap-2 text-xs text-slate-400">
                  <Brain className="w-4 h-4" />
                  <span>Chain of Thought</span>
                </span>
                <span className="flex items-center gap-2 text-xs text-slate-400">
                  <Sparkles className="w-4 h-4" />
                  <span>Cross-reference</span>
                </span>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
