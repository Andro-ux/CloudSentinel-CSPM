# CloudSentinel Frontend Architecture

## Overview

CloudSentinel Frontend is a React 19 + TypeScript single-page application that consumes the CloudSentinel REST API. It never implements business logic, calculates scores, or duplicates backend intelligence.

## Architecture Diagram

```
REST API (/api/v1)
    ↓
API Client (Axios)
    ↓
React Query Hooks
    ↓
Page Components
    ↓
Reusable UI Components
    ↓
Design System Primitives
```

## Core Principles

1. **API-First**: All data comes from the backend. No mock data.
2. **Read-Only Console**: The frontend renders and interacts. The backend thinks.
3. **Design System First**: Every page is assembled from reusable primitives.
4. **Accessible**: WCAG AA compliant, keyboard navigable, ARIA labels.
5. **Themeable**: Dark-first retro game theme with system preference support.
6. **Modular**: Component-driven architecture with clear separation of concerns.

## Folder Structure

```
frontend/src/
  api/                    # API client and endpoint modules
    client.ts            # Axios instance with interceptors
    dashboard.ts         # Dashboard endpoint
    assets.ts            # Asset endpoints
    findings.ts          # Finding endpoints
    risks.ts             # Risk endpoints
    graph.ts             # Graph endpoints
    providers.ts         # Provider endpoints
    auth.ts              # Authentication endpoints
  app/                    # App root component
  components/
    common/              # Design system primitives
      SecurityScoreCard.tsx
      MetricCard.tsx
      RiskBadge.tsx
      SeverityBadge.tsx
      StatusIndicator.tsx
      SectionHeader.tsx
      LoadingState.tsx
      ErrorState.tsx
      EmptyState.tsx
    dashboard/           # Dashboard-specific components
    assets/              # Asset explorer components
    findings/            # Findings explorer components
    risks/               # Risk explorer components
    graph/               # Attack graph components
    auth/                # Authentication components
    layout/              # Layout components (Sidebar, Header)
    ui/                  # shadcn/ui primitives (Button, Card, Input, Badge)
  hooks/                 # Custom React hooks
  pages/                 # Route-level page components
    Login/
    Dashboard/
    Assets/
    Findings/
    Risks/
    Graph/
    Providers/
    Settings/
  layouts/               # Route layout wrappers
  routes/                # React Router configuration
  store/                 # Zustand stores (auth, theme)
  types/                 # TypeScript type definitions
  utils/                 # Utility functions
  theme/                 # Theme configuration
  styles/                # Global CSS and Tailwind
  constants/             # Application constants
  assets/                # Static assets
  test/                  # Test suite
```

## State Management

- **React Query**: All server state (API data, caching, background refetching)
- **Zustand**: Client state only (authentication, theme, UI preferences)
- **Component State**: Local UI state (form inputs, modal open/close, filters)

## Routing

```
/login                   → LoginPage
/                        → Redirect to /dashboard
/dashboard               → DashboardPage
/assets                  → AssetsPage
/findings                → FindingsPage
/risks                   → RisksPage
/graph                   → GraphPage
/providers               → ProvidersPage
/settings                → SettingsPage
```

All routes except `/login` are protected by `ProtectedRoute`.

## API Integration

```typescript
// Example: Dashboard data flow
const { data, isLoading, error } = useQuery({
  queryKey: ['dashboard'],
  queryFn: getDashboard,
})
```

- Axios handles authentication via interceptors
- React Query manages caching, retries, and background updates
- Automatic token refresh on 401 responses
- No direct Axios calls in components

## Design System

### Color System (Retro Game Theme)

- **Primary**: `#00ff9d` (neon green)
- **Surface**: `#1a1a2e` (dark purple)
- **Background**: `#0f0f1b` (near black)
- **Border**: `#3a3a5c` (muted purple)
- **Text**: `#e0e0ff` (light lavender)
- **Risk Levels**: Critical (red), High (orange), Medium (yellow), Low (blue), Healthy (green)

### Typography

- **Retro**: `Press Start 2P` for headings and labels
- **Mono**: `Fira Code` for data and code
- **Sans**: `Inter` for body text

### Components

All UI is built from these primitives:
- `<SecurityScoreCard />` - Score display with grade
- `<MetricCard />` - KPI metric with change indicator
- `<RiskBadge />` - Risk priority badge
- `<SeverityBadge />` - Finding severity badge
- `<StatusIndicator />` - System status indicator
- `<SectionHeader />` - Page section header
- `<LoadingState />` - Loading spinner
- `<ErrorState />` - Error display with retry
- `<EmptyState />` - Empty data display

## Accessibility

- All interactive elements are keyboard navigable
- ARIA labels on all controls
- High contrast color ratios (WCAG AA)
- Focus management in modals and dialogs
- Semantic HTML elements

## Performance

- Lazy route loading
- Code splitting via React Router
- React Query caching reduces API calls
- Memoization where appropriate
- Virtualized tables for large datasets (future)

## Extension Points

- **Compliance Dashboard**: New route and API module
- **MITRE ATT&CK View**: New page and graph integration
- **Kubernetes Dashboard**: New assets filter and table
- **AI Copilot**: Chat interface component
- **Historical Trends**: Time-series data endpoints
- **Multi-tenant Admin**: Organization management page
- **Notification Center**: Real-time updates via WebSocket
- **Report Scheduling**: Background job interface

## Testing Strategy

- Unit tests for all components
- Integration tests for pages
- Hook tests for custom logic
- Accessibility tests
- Responsive layout tests
- Error and loading state tests
- Target: 150+ tests

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```
