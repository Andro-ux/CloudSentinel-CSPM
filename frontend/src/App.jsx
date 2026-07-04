import { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  Shield, 
  Server, 
  AlertTriangle, 
  ShieldAlert, 
  CheckCircle2, 
  RefreshCw, 
  Settings, 
  LogOut, 
  Save, 
  X, 
  Lock, 
  User, 
  Terminal, 
  Check, 
  Info,
  ChevronRight,
  Eye,
  EyeOff,
  History
} from 'lucide-react'
import { format } from 'date-fns'

// Set up default axios response interceptor to handle auth expiration
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
      window.location.reload()
    }
    return Promise.reject(error)
  }
)

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loginError, setLoginError] = useState('')
  const [loginLoading, setLoginLoading] = useState(false)

  const [summary, setSummary] = useState({ CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 })
  const [findings, setFindings] = useState([])
  const [scanHistory, setScanHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [scanning, setScanning] = useState(false)
  const [activeTab, setActiveTab] = useState('findings') // 'findings' | 'history' | 'settings'

  // Details Pane State
  const [selectedFinding, setSelectedFinding] = useState(null)
  const [enrichmentText, setEnrichmentText] = useState('')
  const [enriching, setEnriching] = useState(false)

  // Settings State
  const [settings, setSettings] = useState([])
  const [settingsLoading, setSettingsLoading] = useState(false)
  const [saveStatus, setSaveStatus] = useState('')

  // Configure axios authorization token if saved
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  const fetchData = async () => {
    if (!token) return
    try {
      const [summaryRes, findingsRes, historyRes] = await Promise.all([
        axios.get('/api/summary'),
        axios.get('/api/findings'),
        axios.get('/api/scan-history')
      ])
      setSummary(summaryRes.data)
      setFindings(findingsRes.data)
      setScanHistory(historyRes.data)
    } catch (err) {
      console.error("Error fetching data", err)
    } finally {
      setLoading(false)
    }
  }

  const fetchSettings = async () => {
    setSettingsLoading(true)
    try {
      const res = await axios.get('/api/settings')
      setSettings(res.data)
    } catch (err) {
      console.error("Error fetching settings", err)
    } finally {
      setSettingsLoading(false)
    }
  }

  useEffect(() => {
    if (token) {
      fetchData()
      const interval = setInterval(fetchData, 30000)
      return () => clearInterval(interval)
    }
  }, [token])

  useEffect(() => {
    if (activeTab === 'settings') {
      fetchSettings()
    }
  }, [activeTab])

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoginLoading(true)
    setLoginError('')
    
    // Standard OAuth2 form request formatting
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)

    try {
      const res = await axios.post('/api/login', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      const accessToken = res.data.access_token
      localStorage.setItem('token', accessToken)
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
      setToken(accessToken)
    } catch (err) {
      setLoginError(err.response?.data?.detail || 'Incorrect username or password.')
    } finally {
      setLoginLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
    setToken(null)
    setFindings([])
    setSummary({ CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 })
  }

  const handleScan = async () => {
    setScanning(true)
    try {
      await axios.post('/api/scan')
      // Poll database for scan completion check
      setTimeout(fetchData, 4000)
    } catch (err) {
      console.error("Error triggering scan", err)
    } finally {
      setTimeout(() => setScanning(false), 4000)
    }
  }

  const handleEnrich = async (findingId) => {
    setEnriching(true)
    setEnrichmentText('')
    try {
      const res = await axios.post(`/api/findings/${findingId}/enrich`)
      setEnrichmentText(res.data.enrichment)
    } catch (err) {
      setEnrichmentText('Failed to fetch AI enrichment. Please make sure the OPENAI_API_KEY is configured correctly in the settings panel.')
    } finally {
      setEnriching(false)
    }
  }

  const handleSaveSetting = async (key, value, isEncrypted) => {
    setSaveStatus(`Saving ${key}...`)
    try {
      await axios.post('/api/settings', {
        key: key,
        value: value,
        is_encrypted: isEncrypted
      })
      setSaveStatus('Settings updated successfully!')
      fetchSettings()
      setTimeout(() => setSaveStatus(''), 3000)
    } catch (err) {
      setSaveStatus('Failed to save configuration.')
      setTimeout(() => setSaveStatus(''), 3000)
    }
  }

  // --- Render Login Screen if Unauthenticated ---
  if (!token) {
    return (
      <div className="min-h-screen bg-background text-text flex items-center justify-center p-6 relative overflow-hidden">
        {/* Decorative background glow circles */}
        <div className="absolute w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px] -top-40 -left-40"></div>
        <div className="absolute w-[500px] h-[500px] bg-accent/5 rounded-full blur-[150px] -bottom-40 -right-40"></div>

        <div className="glass-panel max-w-md w-full p-8 relative z-10 border border-white/10 shadow-2xl">
          <div className="flex flex-col items-center mb-8">
            <div className="bg-primary/10 p-4 rounded-2xl mb-4 border border-primary/20">
              <Shield className="w-12 h-12 text-primary" />
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight">CloudSentinel</h1>
            <p className="text-text-muted text-sm mt-1">Enterprise AWS Security Monitoring</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-text-muted mb-2">Username</label>
              <div className="relative">
                <User className="w-5 h-5 text-text-muted absolute left-3 top-3" />
                <input 
                  type="text" 
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="admin"
                  required
                  className="w-full bg-surface border border-border rounded-lg pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:border-primary transition-colors text-text placeholder-text-muted/50"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-text-muted mb-2">Password</label>
              <div className="relative">
                <Lock className="w-5 h-5 text-text-muted absolute left-3 top-3" />
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full bg-surface border border-border rounded-lg pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:border-primary transition-colors text-text placeholder-text-muted/50"
                />
              </div>
            </div>

            {loginError && (
              <div className="text-danger bg-danger/10 border border-danger/20 rounded-lg p-3 text-xs font-medium flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{loginError}</span>
              </div>
            )}

            <button 
              type="submit" 
              disabled={loginLoading}
              className="w-full bg-primary hover:bg-primary-hover text-white py-3 rounded-lg font-semibold text-sm transition-all shadow-lg shadow-primary/20 hover:shadow-primary/30 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loginLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Authenticating...
                </>
              ) : 'Access Control Console'}
            </button>

            <div className="text-center pt-2">
              <span className="text-[10px] text-text-muted uppercase tracking-widest bg-white/5 px-2 py-1 rounded">Default credentials: admin / admin123</span>
            </div>
          </form>
        </div>
      </div>
    )
  }

  // --- Render Dashboard if Authenticated ---
  return (
    <div className="min-h-screen bg-background text-text p-6 flex flex-col">
      {/* Top Banner Navigation */}
      <header className="flex justify-between items-center mb-8 glass-panel p-4 px-6 border border-white/5">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => { setActiveTab('findings'); setSelectedFinding(null); }}>
          <Shield className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-xl font-black tracking-wider uppercase">CloudSentinel</h1>
            <p className="text-[9px] text-text-muted font-bold tracking-widest uppercase -mt-1">Continuous Compliance</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <nav className="flex gap-2">
            <button 
              onClick={() => { setActiveTab('findings'); setSelectedFinding(null); }}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 ${activeTab === 'findings' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'hover:bg-white/5 text-text-muted hover:text-text'}`}
            >
              <Server className="w-4 h-4" />
              Findings
            </button>
            <button 
              onClick={() => setActiveTab('history')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 ${activeTab === 'history' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'hover:bg-white/5 text-text-muted hover:text-text'}`}
            >
              <History className="w-4 h-4" />
              Scan History
            </button>
            <button 
              onClick={() => setActiveTab('settings')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 ${activeTab === 'settings' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'hover:bg-white/5 text-text-muted hover:text-text'}`}
            >
              <Settings className="w-4 h-4" />
              Integrations
            </button>
          </nav>

          <div className="h-6 w-[1px] bg-border"></div>

          <button 
            onClick={handleScan} 
            disabled={scanning}
            className="flex items-center gap-2 bg-accent hover:bg-accent/80 text-background font-bold px-4 py-2 rounded-lg transition-all disabled:opacity-50 text-sm shadow-lg shadow-accent/15"
          >
            <RefreshCw className={`w-4 h-4 ${scanning ? 'animate-spin' : ''}`} />
            {scanning ? 'Scanning...' : 'Scan Account'}
          </button>

          <button 
            onClick={handleLogout}
            title="Log Out"
            className="p-2 text-text-muted hover:text-danger hover:bg-danger/10 rounded-lg transition-colors"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* Main Grid View */}
      <main className="max-w-7xl mx-auto w-full flex-grow flex flex-col gap-6">
        
        {/* Stats Summary Panel */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard title="Critical Risks" count={summary.CRITICAL} icon={<ShieldAlert className="text-danger w-6 h-6" />} color="border-danger" />
          <StatCard title="High Risks" count={summary.HIGH} icon={<AlertTriangle className="text-warning w-6 h-6" />} color="border-warning" />
          <StatCard title="Medium Risks" count={summary.MEDIUM} icon={<AlertTriangle className="text-yellow-400 w-6 h-6" />} color="border-yellow-400" />
          <StatCard title="Low Compliance" count={summary.LOW} icon={<CheckCircle2 className="text-accent w-6 h-6" />} color="border-accent" />
        </div>

        {/* Tab content switching */}
        {activeTab === 'findings' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            
            {/* Table of Findings (Left 2 cols) */}
            <div className="glass-panel p-6 border border-white/5 lg:col-span-2">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                <Terminal className="w-5 h-5 text-primary" />
                Active Findings List
              </h2>
              {loading ? (
                <div className="text-center py-16 text-text-muted animate-pulse flex flex-col items-center gap-3">
                  <RefreshCw className="w-8 h-8 animate-spin text-primary" />
                  <span>Loading cloud assets risk findings...</span>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-white/10 text-text-muted text-xs uppercase tracking-wider">
                        <th className="pb-3 font-bold">Severity</th>
                        <th className="pb-3 font-bold">Service</th>
                        <th className="pb-3 font-bold">Resource</th>
                        <th className="pb-3 font-bold">Risk Assessment</th>
                        <th className="pb-3 font-bold"></th>
                      </tr>
                    </thead>
                    <tbody className="text-sm">
                      {findings.length === 0 ? (
                        <tr>
                          <td colSpan="5" className="py-12 text-center text-text-muted">
                            <CheckCircle2 className="w-10 h-10 text-accent mx-auto mb-3" />
                            No active findings detected. Your cloud environment is secure!
                          </td>
                        </tr>
                      ) : (
                        findings.map(finding => (
                          <tr 
                            key={finding.id} 
                            onClick={() => {
                              setSelectedFinding(finding)
                              setEnrichmentText('')
                            }}
                            className={`border-b border-white/5 hover:bg-white/5 cursor-pointer transition-colors ${selectedFinding?.id === finding.id ? 'bg-white/5' : ''}`}
                          >
                            <td className="py-4">
                              <SeverityBadge severity={finding.severity} />
                            </td>
                            <td className="py-4 font-mono text-xs text-text-muted">{finding.service}</td>
                            <td className="py-4 font-mono text-[11px] max-w-[150px] truncate" title={finding.resource_id}>
                              {finding.resource_id.split('/').pop() || finding.resource_id}
                            </td>
                            <td className="py-4 font-medium">{finding.title}</td>
                            <td className="py-4 text-right">
                              <ChevronRight className="w-4 h-4 text-text-muted inline" />
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Findings Detail Pane (Right 1 col) */}
            <div className="glass-panel p-6 border border-white/5 lg:col-span-1 min-h-[400px] flex flex-col">
              {selectedFinding ? (
                <div className="space-y-6 flex-grow flex flex-col">
                  <div className="flex justify-between items-start gap-2">
                    <div>
                      <SeverityBadge severity={selectedFinding.severity} />
                      <h3 className="text-md font-bold mt-2 text-text">{selectedFinding.title}</h3>
                      <p className="text-[10px] text-text-muted font-mono mt-1 select-all break-all">{selectedFinding.resource_id}</p>
                    </div>
                    <button 
                      onClick={() => setSelectedFinding(null)}
                      className="p-1 text-text-muted hover:text-text rounded hover:bg-white/5"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>

                  <div className="space-y-4 text-sm flex-grow">
                    <div>
                      <h4 className="text-xs font-bold text-text-muted uppercase tracking-wider mb-1 flex items-center gap-1">
                        <Info className="w-3.5 h-3.5 text-primary" />
                        Description
                      </h4>
                      <p className="bg-white/5 p-3 rounded-lg text-xs leading-relaxed text-text/95">{selectedFinding.description}</p>
                    </div>

                    <div>
                      <h4 className="text-xs font-bold text-text-muted uppercase tracking-wider mb-1 flex items-center gap-1">
                        <Check className="w-3.5 h-3.5 text-accent" />
                        Remediation Guidelines
                      </h4>
                      <p className="bg-accent/5 border border-accent/10 p-3 rounded-lg text-xs leading-relaxed text-accent-content">{selectedFinding.recommendation}</p>
                    </div>

                    {/* AI Enrichment Container */}
                    <div className="pt-2 border-t border-white/5">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-xs font-bold text-text-muted uppercase tracking-wider">AI Security Insights</span>
                        {!enrichmentText && (
                          <button 
                            onClick={() => handleEnrich(selectedFinding.id)}
                            disabled={enriching}
                            className="bg-primary/20 hover:bg-primary/30 border border-primary/30 text-primary px-3 py-1 rounded text-xs transition-all font-semibold flex items-center gap-1 disabled:opacity-50"
                          >
                            {enriching ? 'Enriching...' : 'Ask AI'}
                          </button>
                        )}
                      </div>

                      {enriching && (
                        <div className="bg-white/5 p-4 rounded-lg text-center animate-pulse text-xs text-text-muted">
                          Generating intelligent compliance explanation and custom CLI/Terraform remediation configs...
                        </div>
                      )}

                      {enrichmentText && (
                        <div className="bg-primary/5 border border-primary/10 p-3 rounded-lg text-xs leading-relaxed max-h-[220px] overflow-y-auto whitespace-pre-wrap font-sans text-text/90">
                          {enrichmentText}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex-grow flex flex-col items-center justify-center text-center text-text-muted py-20">
                  <Shield className="w-12 h-12 text-white/10 mb-4" />
                  <p className="text-sm font-semibold">Select a security finding to inspect audit details and AI-guided remediation workflows.</p>
                </div>
              )}
            </div>

          </div>
        )}

        {/* Tab Scan History */}
        {activeTab === 'history' && (
          <div className="glass-panel p-6 border border-white/5 max-w-3xl mx-auto w-full">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <History className="w-5 h-5 text-primary" />
              Scan History Logs
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/10 text-text-muted text-xs uppercase tracking-wider">
                    <th className="pb-3 font-semibold">Execution Timestamp</th>
                    <th className="pb-3 font-semibold">Status</th>
                    <th className="pb-3 font-semibold">Findings Identified</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  {scanHistory.length === 0 ? (
                    <tr>
                      <td colSpan="3" className="py-8 text-center text-text-muted">No previous scans found in system logs.</td>
                    </tr>
                  ) : (
                    scanHistory.map(log => (
                      <tr key={log.id} className="border-b border-white/5">
                        <td className="py-3 text-text-muted">{format(new Date(log.timestamp), 'yyyy-MM-dd HH:mm:ss')}</td>
                        <td className="py-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${log.status === 'SUCCESS' ? 'bg-accent/20 text-accent' : 'bg-danger/20 text-danger'}`}>
                            {log.status}
                          </span>
                        </td>
                        <td className="py-3 font-mono font-bold">{log.findings_count}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab Integrations Configuration Console */}
        {activeTab === 'settings' && (
          <div className="glass-panel p-6 border border-white/5 max-w-2xl mx-auto w-full">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-lg font-bold flex items-center gap-2">
                  <Settings className="w-5 h-5 text-primary" />
                  Integration Settings Console
                </h2>
                <p className="text-xs text-text-muted mt-1">Configure credentials dynamically. Values fallback automatically to container environmental variables.</p>
              </div>
            </div>

            {settingsLoading ? (
              <div className="text-center py-8 text-text-muted animate-pulse">Loading dynamic settings keys...</div>
            ) : (
              <div className="space-y-6">
                {saveStatus && (
                  <div className="bg-primary/10 border border-primary/20 text-primary p-3 rounded-lg text-xs font-semibold text-center">
                    {saveStatus}
                  </div>
                )}

                <div className="space-y-4">
                  <SettingRow 
                    label="OpenAI API Key" 
                    dbKey="OPENAI_API_KEY" 
                    description="Used for AI Security Findings Remediation."
                    settings={settings}
                    onSave={handleSaveSetting}
                  />
                  <SettingRow 
                    label="Slack Webhook URL" 
                    dbKey="SLACK_WEBHOOK_URL" 
                    description="Incoming webhook url to dispatch notifications."
                    settings={settings}
                    onSave={handleSaveSetting}
                  />
                  <SettingRow 
                    label="Jira Cloud Instance URL" 
                    dbKey="JIRA_URL" 
                    description="Base URL of your Jira site (e.g. https://yourcompany.atlassian.net)."
                    settings={settings}
                    onSave={handleSaveSetting}
                  />
                  <SettingRow 
                    label="Jira Username / Email" 
                    dbKey="JIRA_USER" 
                    description="Atlassian account email address."
                    settings={settings}
                    onSave={handleSaveSetting}
                  />
                  <SettingRow 
                    label="Jira API Token" 
                    dbKey="JIRA_API_TOKEN" 
                    description="Atlassian API token created in account settings."
                    settings={settings}
                    onSave={handleSaveSetting}
                  />
                  <SettingRow 
                    label="Jira Project Key" 
                    dbKey="JIRA_PROJECT_KEY" 
                    description="Target project shorthand key (default: SEC)."
                    settings={settings}
                    onSave={handleSaveSetting}
                  />
                </div>
              </div>
            )}
          </div>
        )}

      </main>
    </div>
  )
}

// --- Settings Dynamic Sub-Row Component ---
function SettingRow({ label, dbKey, description, settings, onSave }) {
  const existing = settings.find(s => s.key === dbKey)
  const [val, setVal] = useState('')
  const [isEncrypted, setIsEncrypted] = useState(existing?.is_encrypted || dbKey.includes('KEY') || dbKey.includes('TOKEN'))
  const [showVal, setShowVal] = useState(false)

  useEffect(() => {
    if (existing) {
      setVal(existing.value || '')
      setIsEncrypted(existing.is_encrypted)
    }
  }, [existing])

  return (
    <div className="bg-white/5 border border-white/5 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div className="max-w-md">
        <label className="block text-sm font-bold text-text mb-0.5">{label}</label>
        <span className="block text-[11px] text-text-muted leading-tight">{description}</span>
      </div>
      <div className="flex items-center gap-3 shrink-0">
        <div className="relative">
          <input 
            type={isEncrypted && !showVal ? "password" : "text"}
            value={val}
            onChange={(e) => setVal(e.target.value)}
            placeholder={existing?.value ? "********" : "Not configured"}
            className="bg-surface border border-border text-text rounded-lg px-3 py-1.5 text-xs w-[240px] focus:outline-none focus:border-primary placeholder-text-muted/40"
          />
          {isEncrypted && (
            <button 
              onClick={() => setShowVal(!showVal)}
              className="absolute right-2 top-2 text-text-muted hover:text-text"
            >
              {showVal ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>
        <button 
          onClick={() => onSave(dbKey, val, isEncrypted)}
          className="bg-primary hover:bg-primary-hover p-2 rounded-lg text-white transition-colors"
          title="Save setting"
        >
          <Save className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

function StatCard({ title, count, icon, color }) {
  return (
    <div className={`glass-panel p-6 border-l-4 ${color} flex items-center justify-between border-white/5`}>
      <div>
        <p className="text-text-muted text-xs font-semibold uppercase tracking-wider mb-1">{title}</p>
        <p className="text-3xl font-black tracking-tight">{count || 0}</p>
      </div>
      <div className="bg-white/5 p-3 rounded-full">
        {icon}
      </div>
    </div>
  )
}

function SeverityBadge({ severity }) {
  const colors = {
    CRITICAL: 'bg-danger/20 text-danger border border-danger/30',
    HIGH: 'bg-warning/20 text-warning border border-warning/30',
    MEDIUM: 'bg-yellow-400/20 text-yellow-400 border border-yellow-400/30',
    LOW: 'bg-accent/20 text-accent border border-accent/30',
  }
  return (
    <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold tracking-wider border ${colors[severity] || colors.LOW}`}>
      {severity}
    </span>
  )
}

export default App
