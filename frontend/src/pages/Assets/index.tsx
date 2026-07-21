import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { SectionHeader } from '../../components/common/SectionHeader'
import { Card } from '../../components/ui/card'
import { Input } from '../../components/ui/input'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { LoadingState } from '../../components/common/LoadingState'
import { ErrorState } from '../../components/common/ErrorState'
import { getAssets } from '../../api/assets'
import { Search, Filter } from 'lucide-react'

export function AssetsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [providerFilter, setProviderFilter] = useState('')

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['assets', page, search, providerFilter],
    queryFn: () => getAssets({ page, page_size: 25, search, provider: providerFilter }),
  })

  if (isLoading) {
    return <LoadingState text="LOADING ASSETS..." />
  }

  if (error) {
    return (
      <ErrorState
        title="ASSETS ERROR"
        message="Failed to load assets."
        onRetry={() => refetch()}
      />
    )
  }

  const assets = data?.data || []
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
        title="ASSET EXPLORER"
        subtitle="Cloud asset inventory and metadata"
      />

      <Card>
        <div className="p-4 border-b border-retro-border">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-retro-text-muted" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search assets..."
                className="pl-9"
              />
            </div>
            <div className="flex gap-2">
              <Input
                value={providerFilter}
                onChange={(e) => setProviderFilter(e.target.value)}
                placeholder="Provider filter"
                className="w-40"
              />
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
                  TYPE
                </th>
                <th className="text-left p-4 text-xs font-retro text-retro-text-muted tracking-wider">
                  COUNT
                </th>
                <th className="text-left p-4 text-xs font-retro text-retro-text-muted tracking-wider">
                  PROVIDER
                </th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset, idx) => (
                <tr
                  key={idx}
                  className="border-b border-retro-border/50 hover:bg-retro-surface-alt transition-colors"
                >
                  <td className="p-4">
                    <span className="text-sm font-mono text-retro-text">
                      {asset.asset_type}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="text-sm font-mono text-retro-primary">
                      {asset.count}
                    </span>
                  </td>
                  <td className="p-4">
                    <Badge variant="secondary" className="font-mono text-xs">
                      {asset.provider}
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
