import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { SectionHeader } from '../../components/common/SectionHeader'
import { Card } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { RiskBadge } from '../../components/common/RiskBadge'
import { LoadingState } from '../../components/common/LoadingState'
import { ErrorState } from '../../components/common/ErrorState'
import { getRisks } from '../../api/risks'

export function RisksPage() {
  const [page, setPage] = useState(1)
  const [priorityFilter, setPriorityFilter] = useState('')

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['risks', page, priorityFilter],
    queryFn: () => getRisks({ page, page_size: 25, priority: priorityFilter }),
  })

  if (isLoading) {
    return <LoadingState text="LOADING RISKS..." />
  }

  if (error) {
    return (
      <ErrorState
        title="RISKS ERROR"
        message="Failed to load risks."
        onRetry={() => refetch()}
      />
    )
  }

  const risks = data?.data || []
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
        title="RISK EXPLORER"
        subtitle="Prioritized risk assessments"
      />

      <Card>
        <div className="p-4 border-b border-retro-border">
          <div className="flex gap-4">
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="retro-input w-40"
            >
              <option value="">All Priorities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
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
                  PRIORITY
                </th>
                <th className="text-left p-4 text-xs font-retro text-retro-text-muted tracking-wider">
                  SCORE
                </th>
                <th className="text-left p-4 text-xs font-retro text-retro-text-muted tracking-wider">
                  CATEGORY
                </th>
              </tr>
            </thead>
            <tbody>
              {risks.map((risk) => (
                <tr
                  key={risk.id}
                  className="border-b border-retro-border/50 hover:bg-retro-surface-alt transition-colors"
                >
                  <td className="p-4">
                    <span className="text-xs font-mono text-retro-text-muted">
                      {risk.id}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="text-sm text-retro-text">{risk.title}</span>
                  </td>
                  <td className="p-4">
                    <RiskBadge priority={risk.priority} />
                  </td>
                  <td className="p-4">
                    <span className="text-sm font-mono text-retro-primary">
                      {risk.score}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="text-sm text-retro-text-muted">{risk.category}</span>
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
