import { useQuery } from '@tanstack/react-query'
import { SectionHeader } from '../../components/common/SectionHeader'
import { SecurityScoreCard } from '../../components/common/SecurityScoreCard'
import { MetricCard } from '../../components/common/MetricCard'
import { RiskBadge } from '../../components/common/RiskBadge'
import { SeverityBadge } from '../../components/common/SeverityBadge'
import { LoadingState } from '../../components/common/LoadingState'
import { ErrorState } from '../../components/common/ErrorState'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card'
import { getDashboard } from '../../api/dashboard'
import { Shield, AlertTriangle, CheckCircle, Activity } from 'lucide-react'

export function DashboardPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
  })

  if (isLoading) {
    return <LoadingState text="LOADING DASHBOARD..." />
  }

  if (error) {
    return (
      <ErrorState
        title="DASHBOARD ERROR"
        message="Failed to load dashboard data."
        onRetry={() => refetch()}
      />
    )
  }

  const dashboard = data?.data
  if (!dashboard) {
    return <ErrorState title="NO DATA" message="Dashboard data is unavailable." />
  }

  const summary = dashboard.summary

  return (
    <div className="space-y-6">
      <SectionHeader
        title="EXECUTIVE DASHBOARD"
        subtitle="Real-time security posture overview"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <SecurityScoreCard
            score={dashboard.security_score.overall}
            grade={dashboard.security_score.grade}
            size="lg"
          />
        </div>

        <div className="lg:col-span-2 grid grid-cols-2 gap-4">
          <MetricCard
            title="TOTAL ASSETS"
            value={summary.total_assets}
            icon={<Shield className="h-4 w-4" />}
          />
          <MetricCard
            title="FINDINGS"
            value={summary.total_findings}
            icon={<AlertTriangle className="h-4 w-4" />}
          />
          <MetricCard
            title="RISKS"
            value={summary.total_risks}
            icon={<Activity className="h-4 w-4" />}
          />
          <MetricCard
            title="HEALTH SCORE"
            value={`${dashboard.security_score.overall}%`}
            icon={<CheckCircle className="h-4 w-4" />}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card variant="hover">
          <CardHeader>
            <CardTitle>TOP RISKS</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {summary.top_risks.slice(0, 5).map((risk: any, idx: number) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 rounded-md bg-retro-surface-alt"
                >
                  <div>
                    <p className="text-sm font-medium text-retro-text">
                      {risk.title || risk.category || `Risk ${idx + 1}`}
                    </p>
                    <p className="text-xs text-retro-text-muted mt-1">
                      Score: {risk.score || risk.risk_score || 'N/A'}
                    </p>
                  </div>
                  <RiskBadge priority={risk.priority || 'medium'} />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card variant="hover">
          <CardHeader>
            <CardTitle>RECENT FINDINGS</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {summary.insights.slice(0, 5).map((insight: any, idx: number) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 rounded-md bg-retro-surface-alt"
                >
                  <div>
                    <p className="text-sm font-medium text-retro-text">
                      {insight.title || insight.type || `Finding ${idx + 1}`}
                    </p>
                    <p className="text-xs text-retro-text-muted mt-1">
                      {insight.category || 'General'}
                    </p>
                  </div>
                  <SeverityBadge severity={insight.severity || 'medium'} />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>SECURITY DIMENSIONS</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(summary.dimensions || {}).map(([key, value]) => (
              <div
                key={key}
                className="p-4 rounded-md bg-retro-surface-alt border border-retro-border"
              >
                <p className="text-xs font-retro text-retro-text-muted mb-2">
                  {key.toUpperCase()}
                </p>
                <p className="text-xl font-bold text-retro-text font-mono">
                  {typeof value === 'number' ? `${value}%` : value}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
