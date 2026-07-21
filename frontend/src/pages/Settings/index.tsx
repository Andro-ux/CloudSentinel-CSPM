import { SectionHeader } from '../../components/common/SectionHeader'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { StatusIndicator } from '../../components/common/StatusIndicator'
import { useAuth } from '../../store/auth'
import { User, Shield, Key, Palette, Monitor } from 'lucide-react'

export function SettingsPage() {
  const { user } = useAuth()

  return (
    <div className="space-y-6">
      <SectionHeader
        title="SETTINGS"
        subtitle="System configuration and preferences"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <Card>
            <div className="p-6">
              <div className="flex items-center gap-4 mb-4">
                <div className="h-16 w-16 rounded-full bg-retro-primary/10 border-2 border-retro-primary flex items-center justify-center">
                  <User className="h-8 w-8 text-retro-primary" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-retro-text">
                    {user?.username || 'User'}
                  </h3>
                  <p className="text-xs text-retro-text-muted font-mono">
                    ID: {user?.id || 'N/A'}
                  </p>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs text-retro-text-muted">
                  <Shield className="h-3 w-3" />
                  <span>Roles: {user?.role_ids?.join(', ') || 'N/A'}</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-retro-text-muted">
                  <Key className="h-3 w-3" />
                  <span>Org ID: {user?.organization_id || 'N/A'}</span>
                </div>
              </div>
            </div>
          </Card>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>PREFERENCES</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Palette className="h-4 w-4 text-retro-primary" />
                  <div>
                    <p className="text-sm font-medium text-retro-text">Theme</p>
                    <p className="text-xs text-retro-text-muted">Dark / Light mode</p>
                  </div>
                </div>
                <Badge variant="secondary">DARK</Badge>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Monitor className="h-4 w-4 text-retro-primary" />
                  <div>
                    <p className="text-sm font-medium text-retro-text">System</p>
                    <p className="text-xs text-retro-text-muted">CloudSentinel v0.12.0</p>
                  </div>
                </div>
                <StatusIndicator status="healthy" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>API KEYS</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-retro-text-muted mb-4">
                Manage API keys for programmatic access.
              </p>
              <Button variant="secondary" className="w-full">
                GENERATE NEW API KEY
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
