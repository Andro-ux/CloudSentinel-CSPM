import { useQuery } from '@tanstack/react-query'
import { SectionHeader } from '../../components/common/SectionHeader'
import { Card } from '../../components/ui/card'
import { Badge } from '../../components/ui/badge'
import { LoadingState } from '../../components/common/LoadingState'
import { ErrorState } from '../../components/common/ErrorState'
import { getProviders } from '../../api/providers'
import { Server } from 'lucide-react'

export function ProvidersPage() {
  const { data: providersData, isLoading: providersLoading, error: providersError } = useQuery({
    queryKey: ['providers'],
    queryFn: getProviders,
  })

  if (providersLoading) {
    return <LoadingState text="LOADING PROVIDERS..." />
  }

  if (providersError) {
    return (
      <ErrorState
        title="PROVIDERS ERROR"
        message="Failed to load providers."
        onRetry={() => {}}
      />
    )
  }

  const providers = providersData?.data || []

  return (
    <div className="space-y-6">
      <SectionHeader
        title="PROVIDERS"
        subtitle="Registered cloud provider plugins"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {providers.map((provider: any) => {
          return (
            <Card key={provider.provider_id} variant="hover">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-retro-primary/10 border border-retro-primary/30 flex items-center justify-center">
                      <Server className="h-5 w-5 text-retro-primary" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-retro-text">
                        {provider.name}
                      </h3>
                      <p className="text-xs text-retro-text-muted font-mono">
                        v{provider.version}
                      </p>
                    </div>
                  </div>
                  <Badge variant="healthy" className="font-mono text-[10px]">
                    ACTIVE
                  </Badge>
                </div>

                <p className="text-xs text-retro-text-muted mb-4">
                  {provider.description}
                </p>

                <div className="space-y-3">
                  <div>
                    <p className="text-[10px] font-retro text-retro-text-muted tracking-wider mb-2">
                      CAPABILITIES
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {provider.capabilities?.slice(0, 4).map((cap: string) => (
                        <Badge key={cap} variant="secondary" className="text-[10px]">
                          {cap}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="text-[10px] font-retro text-retro-text-muted tracking-wider mb-2">
                      SERVICES
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {provider.supported_services?.slice(0, 3).map((service: string) => (
                        <Badge key={service} variant="outline" className="text-[10px]">
                          {service}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
