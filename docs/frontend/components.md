# CloudSentinel Frontend Components

## Design System Primitives

### SecurityScoreCard

Displays the overall security score with grade.

```tsx
<SecurityScoreCard
  score={85}
  grade="A"
  label="SECURITY SCORE"
  size="md" | "sm" | "lg"
/>
```

**Props:**
- `score: number` (0-100)
- `grade: string` (A-F)
- `label?: string`
- `size?: 'sm' | 'md' | 'lg'`
- `className?: string`

**Features:**
- Animated pulse ring
- Color-coded by score range
- Retro font for score display

### MetricCard

Displays a key performance indicator with optional change indicator.

```tsx
<MetricCard
  title="TOTAL ASSETS"
  value={42}
  change={{ value: 5, type: 'increase' }}
  icon={<Shield className="h-4 w-4" />}
/>
```

**Props:**
- `title: string`
- `value: string | number`
- `change?: { value: number; type: 'increase' | 'decrease' | 'neutral' }`
- `icon?: ReactNode`
- `className?: string`

**Features:**
- Retro card shadow
- Change indicator with arrow/icon
- Icon support

### RiskBadge

Displays risk priority with semantic coloring.

```tsx
<RiskBadge priority="critical" | "high" | "medium" | "low" />
```

**Props:**
- `priority: string`
- `className?: string`

### SeverityBadge

Displays finding severity with semantic coloring.

```tsx
<SeverityBadge severity="critical" | "high" | "medium" | "low" | "info" />
```

**Props:**
- `severity: string`
- `className?: string`

### StatusIndicator

Displays system status with animated dot.

```tsx
<StatusIndicator status="healthy" | "degraded" | "unhealthy" | "loading" label="ONLINE" />
```

**Props:**
- `status: 'healthy' | 'degraded' | 'unhealthy' | 'loading'`
- `label?: string`
- `className?: string`

### SectionHeader

Page section header with optional action.

```tsx
<SectionHeader
  title="EXECUTIVE DASHBOARD"
  subtitle="Real-time overview"
  action={<Button>Export</Button>}
/>
```

**Props:**
- `title: string`
- `subtitle?: string`
- `action?: ReactNode`
- `className?: string`

### LoadingState

Loading spinner with optional text.

```tsx
<LoadingState text="LOADING DASHBOARD..." />
```

**Props:**
- `text?: string`
- `className?: string`

### ErrorState

Error display with optional retry button.

```tsx
<ErrorState
  title="DASHBOARD ERROR"
  message="Failed to load data."
  onRetry={() => refetch()}
/>
```

**Props:**
- `title?: string`
- `message?: string`
- `onRetry?: () => void`
- `className?: string`

### EmptyState

Empty data display with optional action.

```tsx
<EmptyState
  title="NO DATA FOUND"
  description="There are no items to display."
  action={<Button>Create Item</Button>}
/>
```

**Props:**
- `title?: string`
- `description?: string`
- `action?: ReactNode`
- `className?: string`

## UI Primitives (shadcn/ui)

### Button

```tsx
<Button variant="default" | "secondary" | "destructive" | "outline" | "ghost" | "retro" size="sm" | "default" | "lg" | "icon">
  Click me
</Button>
```

### Card

```tsx
<Card variant="default" | "hover" | "glow" | "flat">
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>
```

### Input

```tsx
<Input variant="default" | "retro" placeholder="Enter text" />
```

### Badge

```tsx
<Badge variant="default" | "secondary" | "destructive" | "outline" | "critical" | "high" | "medium" | "low" | "healthy">
  Badge
</Badge>
```

## Page Components

### DashboardPage

Executive dashboard with security score, metrics, top risks, and findings.

**Widgets:**
- Security Score Card
- Metric Cards (assets, findings, risks, health)
- Top Risks list
- Recent Findings list
- Security Dimensions grid

### AssetsPage

Asset explorer with search, filters, and pagination.

**Features:**
- Search by asset name
- Provider filter
- Paginated table
- Responsive design

### FindingsPage

Findings explorer with severity filters and pagination.

**Features:**
- Severity filter dropdown
- Paginated table
- Status badges

### RisksPage

Risk explorer with priority filters and sorting.

**Features:**
- Priority filter
- Score display
- Paginated table

### GraphPage

Attack graph visualization placeholder with React Flow integration point.

**Features:**
- Node/edge count badges
- Sidebar with node/edge lists
- React Flow placeholder

### ProvidersPage

Provider overview with capabilities and services.

**Features:**
- Provider cards
- Capability badges
- Service lists

### SettingsPage

User settings with profile, preferences, and API keys.

**Features:**
- User profile card
- Theme preference
- System information
- API key management

### LoginPage

Authentication page with form validation.

**Features:**
- Username/password form
- Zod validation
- JWT authentication
- Retro game theme
