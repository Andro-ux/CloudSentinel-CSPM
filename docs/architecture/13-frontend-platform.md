# Frontend Platform Architecture

## Document Information

- **Version**: 1.0.0
- **Sprint**: 4.5
- **Status**: Complete

## Component Hierarchy

```
App
├── QueryClientProvider
│   └── BrowserRouter
│       └── ThemeProvider
│           └── AuthProvider
│               └── RouterProvider
│                   ├── LoginPage (/login)
│                   └── ProtectedRoute (/)
│                       └── Layout
│                           ├── Sidebar
│                           │   ├── Brand
│                           │   ├── Navigation
│                           │   └── Logout
│                           ├── Header
│                           │   └── StatusIndicator
│                           └── Page Content
│                               ├── DashboardPage
│                               │   ├── SecurityScoreCard
│                               │   ├── MetricCard[]
│                               │   ├── RiskBadge[]
│                               │   ├── SeverityBadge[]
│                               │   └── Card[]
│                               ├── AssetsPage
│                               │   ├── SearchBar
│                               │   ├── FilterPanel
│                               │   └── Table
│                               ├── FindingsPage
│                               │   ├── SearchBar
│                               │   ├── FilterPanel
│                               │   └── Table
│                               ├── RisksPage
│                               │   ├── FilterPanel
│                               │   └── Table
│                               ├── GraphPage
│                               │   ├── GraphCanvas
│                               │   ├── NodeList
│                               │   └── EdgeList
│                               ├── ProvidersPage
│                               │   └── ProviderCard[]
│                               └── SettingsPage
│                                   ├── ProfileCard
│                                   ├── PreferencesCard
│                                   └── ApiKeysCard
```

## Routing

### Public Routes

| Path | Component | Description |
|------|-----------|-------------|
| `/login` | LoginPage | Authentication page |

### Protected Routes

| Path | Component | Description |
|------|-----------|-------------|
| `/` | Redirect | Redirects to `/dashboard` |
| `/dashboard` | DashboardPage | Executive dashboard |
| `/assets` | AssetsPage | Asset explorer |
| `/findings` | FindingsPage | Findings explorer |
| `/risks` | RisksPage | Risk explorer |
| `/graph` | GraphPage | Attack graph |
| `/providers` | ProvidersPage | Provider overview |
| `/settings` | SettingsPage | User settings |

## API Integration

### Client Configuration

- Base URL: `/api/v1`
- Authentication: Bearer token in Authorization header
- Token refresh: Automatic on 401 responses
- Request/Response interceptors for logging

### Data Flow

```
Component
    ↓ useQuery/useMutation
React Query
    ↓ queryFn
API Module (e.g., getDashboard)
    ↓ apiClient.get/post
Axios Instance
    ↓ HTTP Request
Backend API (/api/v1/...)
```

### Caching Strategy

- Stale time: 5 minutes
- Cache time: 10 minutes
- Background refetching: Disabled
- Retry: 1 attempt on failure

## State Management

### Server State (React Query)

- Dashboard data
- Asset lists
- Finding lists
- Risk lists
- Graph data
- Provider data

### Client State (Zustand)

- Authentication state (user, tokens, isAuthenticated)
- Theme preference (dark, light, system)
- UI preferences (sidebar collapsed, etc.)

### Local State (useState)

- Form inputs
- Filter values
- Pagination page numbers
- Modal open/close states

## Design System

### Colors

Semantic color system with retro game theme:

- **Primary**: Neon green (`#00ff9d`)
- **Surface**: Dark purple (`#1a1a2e`)
- **Background**: Near black (`#0f0f1b`)
- **Risk Colors**: Critical (red), High (orange), Medium (yellow), Low (blue), Healthy (green)

### Typography

- **Retro**: `Press Start 2P` - Headings and branding
- **Mono**: `Fira Code` - Data and metrics
- **Sans**: `Inter` - Body text

### Components

All UI built from primitives:
- SecurityScoreCard
- MetricCard
- RiskBadge
- SeverityBadge
- StatusIndicator
- SectionHeader
- LoadingState
- ErrorState
- EmptyState
- Button, Card, Input, Badge

## Accessibility

### WCAG AA Compliance

- Color contrast ratios meet AA standards
- All interactive elements keyboard accessible
- ARIA labels on controls
- Focus management in modals
- Semantic HTML elements

### Keyboard Navigation

- Tab through all interactive elements
- Enter/Space to activate
- Escape to close modals
- Arrow keys for navigation

### Screen Readers

- Descriptive labels
- Status announcements
- Error messages
- Loading states

## Performance

### Optimization Strategies

- Lazy route loading
- Code splitting
- React Query caching
- Memoization
- Virtualized tables (future)

### Bundle Size

- Target: < 500KB gzipped
- Tree shaking enabled
- Dynamic imports for routes

## Security

### Authentication

- JWT tokens stored in localStorage
- Automatic token refresh
- Secure logout (clears tokens)
- Protected routes

### Authorization

- Role-based access (future)
- Organization isolation
- API key management (future)

### Headers

- Content Security Policy (future)
- X-Frame-Options
- X-Content-Type-Options

## Extension Guide

### Adding a New Dashboard Widget

1. Create widget component in `src/components/dashboard/`
2. Add to DashboardPage
3. Create API endpoint in backend
4. Add API module in `src/api/`
5. Use React Query to fetch data

### Adding a New Page

1. Create page component in `src/pages/NewPage/`
2. Add route in `src/routes/index.tsx`
3. Add navigation item in Sidebar
4. Create API module
5. Add tests

### Adding a New API Endpoint

1. Add endpoint function in `src/api/module.ts`
2. Define TypeScript types in `src/types/`
3. Use in component with React Query
4. Add error handling

### Adding a New Design Component

1. Create component in `src/components/common/`
2. Follow naming convention (PascalCase)
3. Add TypeScript props interface
4. Add tests
5. Document in `docs/frontend/components.md`

## Future Enhancements

- **WebSocket Support**: Real-time updates for findings and risks
- **Virtualized Tables**: For large asset inventories
- **Advanced Filtering**: Multi-criteria filters with saved searches
- **Export/Reporting**: PDF and CSV export
- **Collaboration**: Comments and annotations
- **AI Copilot**: Natural language query interface
- **Historical Trends**: Time-series charts
- **Compliance Dashboard**: Framework-specific views
- **MITRE ATT&CK**: Technique mapping
- **Kubernetes Dashboard**: Container security view
