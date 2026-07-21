import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { SectionHeader } from '../../components/common/SectionHeader'
import { Card } from '../../components/ui/card'
import { Input } from '../../components/ui/input'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { SeverityBadge } from '../../components/common/SeverityBadge'
import { LoadingState } from '../../components/common/LoadingState'
import { ErrorState } from '../../components/common/ErrorState'
import { getFindings } from '../../api/findings'
import { Search, Filter } from 'lucide-react'

export function FindingsPage() {
  const [page, setPage] = useState(1)
  const [severityFilter, setSeverityFilter] = useState('')

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['findings', page, severityFilter],
    queryFn: () => getFindings({ page, page_size: 25, severity: severityFilter }),
  })

  if (isLoading) {
    return <LoadingState text="LOADING FINDINGS..." />
  }

  if (error) {
    return (
      <ErrorState
        title="FINDINGS ERROR"
        message="Failed to load findings."
        onRetry={() => refetch()}
      />
    )
  }

  const findings = data?.data || []
  const pagination = (data?.metadata?.pagination || {}) as {
    page: number
    page_size: number
    total: number
    has_next: boolean
    has_previous: boolean
  }

  return (
    <div className="space-y-6">
      <SectionHeader
        title="FINDINGS EXPLORER"
        subtitle="Security findings from rule evaluation"
      />

      <Card>
        <div className="p-4 border-b border-retro-border">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-retro-text-muted" />
              <Input
                placeholder="Search findings..."
                className="pl-9"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="retro-input w-40"
              >
                <option value="">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
              <Button variant="secondary" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-retro-border">
                <th className="text-left p-4 text-xs font-retro text-retro-text-muted tracking-wider">
                  ID
                </th>
                <th className="text-left p-4 text-xs font-retro text-retro-text-muted tracking-wider">
                  TITLE
                </th>
                <th className="text-left p-4 text-xs font-retro text-retro-text-muted tracking-wider">
                  SEVERITY
                </th>
                <th className="text-left p-4 text-xs font-retro text-retro-text-muted tracking-wider">
                  CATEGORY
                </th>
                <th className="text-left p-4 text-xs font-retro text-retro-text-muted tracking-wider">
                  STATUS
                </th>
              </tr>
            </thead>
            <tbody>
              {findings.map((finding) => (
                <tr
                  key={finding.id}
                  className="border-b border-retro-border/50 hover:bg-retro-surface-alt transition-colors"
                >
                  <td className="p-4">
                    <span className="text-xs font-mono text-retro-text-muted">
                      {finding.id}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="text-sm text-retro-text">{finding.title}</span>
                  </td>
                  <td className="p-4">
                    <SeverityBadge severity={finding.severity} />
                  </td>
                  <td className="p-4">
                    <span className="text-sm text-retro-text-muted">{finding.category}</span>
                  </td>
                  <td className="p-4">
                    <Badge variant="secondary" className="font-mono text-xs">
                      {finding.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between p-4 border-t border-retro-border">
          <span className="text-xs text-retro-text-muted font-mono">
            Page {pagination.page || 1} of {Math.ceil((pagination.total || 0) / (pagination.page_size || 25))}
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={!pagination.has_previous}
              onClick={() => setPage(p => p - 1)}
            >
              PREV
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!pagination.has_next}
              onClick={() => setPage(p => p + 1)}
            >
              NEXT
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
