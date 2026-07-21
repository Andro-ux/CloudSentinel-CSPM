import { useQuery } from '@tanstack/react-query'
import { SectionHeader } from '../../components/common/SectionHeader'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card'
import { LoadingState } from '../../components/common/LoadingState'
import { ErrorState } from '../../components/common/ErrorState'
import { getGraph } from '../../api/graph'
import { Badge } from '../../components/ui/badge'

export function GraphPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['graph'],
    queryFn: getGraph,
  })

  if (isLoading) {
    return <LoadingState text="LOADING GRAPH..." />
  }

  if (error) {
    return (
      <ErrorState
        title="GRAPH ERROR"
        message="Failed to load knowledge graph."
        onRetry={() => refetch()}
      />
    )
  }

  const graph = data?.data
  const nodes = graph?.nodes || []
  const edges = graph?.edges || []

  return (
    <div className="space-y-6">
      <SectionHeader
        title="ATTACK GRAPH"
        subtitle="Knowledge graph relationships and attack paths"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card className="h-[600px]">
            <div className="p-4 border-b border-retro-border">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-retro text-retro-text tracking-wider">
                  GRAPH VISUALIZATION
                </h3>
                <div className="flex gap-2">
                  <Badge variant="secondary" className="font-mono text-xs">
                    {nodes.length} NODES
                  </Badge>
                  <Badge variant="secondary" className="font-mono text-xs">
                    {edges.length} EDGES
                  </Badge>
                </div>
              </div>
            </div>
            <div className="h-[500px] flex items-center justify-center bg-retro-bg/50">
              <div className="text-center">
                <div className="text-6xl mb-4">🕸️</div>
                <p className="text-sm font-retro text-retro-text-muted">
                  REACT FLOW INTEGRATION
                </p>
                <p className="text-xs text-retro-text-muted mt-2 font-mono">
                  {nodes.length} nodes • {edges.length} edges
                </p>
              </div>
            </div>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>NODES</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-[300px] overflow-y-auto">
                {nodes.slice(0, 20).map((node: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-2 rounded-md bg-retro-surface-alt border border-retro-border"
                  >
                    <p className="text-xs font-mono text-retro-text">
                      {node.id || node.label || `Node ${idx + 1}`}
                    </p>
                    {node.type && (
                      <Badge variant="secondary" className="text-[10px] mt-1">
                        {node.type}
                      </Badge>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>EDGES</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-[200px] overflow-y-auto">
                {edges.slice(0, 10).map((edge: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-2 rounded-md bg-retro-surface-alt border border-retro-border"
                  >
                    <p className="text-xs font-mono text-retro-text">
                      {edge.source} → {edge.target}
                    </p>
                    {edge.relation && (
                      <p className="text-[10px] text-retro-text-muted mt-1">
                        {edge.relation}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
