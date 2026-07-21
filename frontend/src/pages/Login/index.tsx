import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Card } from '../../components/ui/card'
import { useAuth } from '../../store/auth'
import { login } from '../../api/auth'

const loginSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  password: z.string().min(12, 'Password must be at least 12 characters'),
})

type LoginForm = z.infer<typeof loginSchema>

export function LoginPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await login(data.username, data.password)
      setAuth(
        { ...response.data.user, role_ids: [] },
        {
          access_token: response.data.access_token,
          refresh_token: response.data.refresh_token,
        }
      )
      navigate('/dashboard')
    } catch (err) {
      setError('Invalid credentials. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-retro-bg p-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-retro-primary/5 via-transparent to-retro-secondary/5" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTAgNDBMODAgMEgwIiBmaWxsPSJub25lIiBzdHJva2U9InJnYmEoMCwgMjU1LCAyNTUsIDAuMDIpIiBzdHJva2Utd2lkdGg9IjEiLz48L3N2Zz4=')] opacity-30" />
      </div>

      <Card variant="glow" className="w-full max-w-md relative z-10">
        <div className="p-8">
          <div className="flex flex-col items-center mb-8">
            <div className="h-16 w-16 rounded-lg bg-retro-primary flex items-center justify-center shadow-retro mb-4">
              <span className="font-retro text-2xl text-retro-bg">CS</span>
            </div>
            <h1 className="text-2xl font-retro text-retro-text tracking-wider">
              CLOUDSENTINEL
            </h1>
            <p className="text-xs text-retro-text-muted font-mono mt-2">
              SECURITY CONSOLE v0.12.0
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
              <label className="text-xs font-retro text-retro-text-muted tracking-wider">
                USERNAME
              </label>
              <Input
                {...register('username', {
                  onChange: () => error && setError(null),
                })}
                variant="retro"
                placeholder="Enter username"
                autoComplete="username"
              />
              {errors.username && (
                <p className="text-xs text-retro-critical font-mono">
                  {errors.username.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-xs font-retro text-retro-text-muted tracking-wider">
                PASSWORD
              </label>
              <Input
                {...register('password', {
                  onChange: () => error && setError(null),
                })}
                type="password"
                variant="retro"
                placeholder="Enter password"
                autoComplete="current-password"
              />
              {errors.password && (
                <p className="text-xs text-retro-critical font-mono">
                  {errors.password.message}
                </p>
              )}
            </div>

            {error && (
              <div className="p-3 rounded-md border border-retro-critical/30 bg-retro-critical/10">
                <p className="text-xs text-retro-critical font-mono">{error}</p>
              </div>
            )}

            <Button
              type="submit"
              variant="retro"
              size="lg"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? 'AUTHENTICATING...' : 'LOGIN'}
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t border-retro-border">
            <p className="text-[10px] text-retro-text-muted font-mono text-center">
              AUTHORIZED ACCESS ONLY
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
