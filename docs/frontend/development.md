# CloudSentinel Frontend Development Guide

## Prerequisites

- Node.js 18+
- npm 9+

## Setup

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## Project Structure

```
frontend/
  src/
    api/           # API client and endpoint modules
    app/           # App root component
    components/    # Reusable UI components
    hooks/         # Custom React hooks
    pages/         # Route-level pages
    layouts/       # Layout wrappers
    routes/        # Router configuration
    store/         # Zustand stores
    types/         # TypeScript types
    utils/         # Utilities
    theme/         # Theme config
    styles/        # Global CSS
    constants/     # Constants
    assets/        # Static assets
    test/          # Test suite
  docs/            # Documentation
  public/          # Public assets
```

## Adding a New Page

1. Create page component in `src/pages/NewPage/index.tsx`
2. Add route in `src/routes/index.tsx`
3. Add navigation item in `src/components/layout/Sidebar.tsx`
4. Create API module in `src/api/newpage.ts` if needed
5. Add tests in `src/test/newpage.test.tsx`

## Adding a New Component

1. Create component in appropriate `src/components/` subdirectory
2. Export from subdirectory index if needed
3. Add tests in `src/test/`
4. Document in `docs/frontend/components.md`

## API Integration

```typescript
// 1. Define endpoint in src/api/module.ts
export async function getData(params?: { page?: number }) {
  const response = await apiClient.get('/endpoint', { params })
  return response.data
}

// 2. Use in component with React Query
const { data, isLoading, error } = useQuery({
  queryKey: ['data', params],
  queryFn: () => getData(params),
})
```

## State Management

- **Server State**: Use React Query (`useQuery`, `useMutation`)
- **Auth State**: Use `useAuth()` from `src/store/auth`
- **Theme State**: Use `useTheme()` from `src/store/theme`
- **Local UI State**: Use `useState` in component

## Styling

- Use Tailwind CSS classes
- Follow retro game theme conventions
- Use `cn()` utility for class merging
- Use semantic color classes (`text-retro-critical`, etc.)

## Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

### Test Organization

- `src/test/*.test.ts` - Utility tests
- `src/test/*.test.tsx` - Component and page tests
- Group related tests in describe blocks
- Test loading, error, and empty states
- Test accessibility features

## Linting

```bash
npm run lint
```

## Building

```bash
npm run build
```

Output goes to `dist/` directory.

## Environment Variables

Create `.env` file in `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

## Troubleshooting

### Tests Fail

- Ensure `jsdom` environment is set in `vite.config.ts`
- Check that test files are in `src/test/`
- Verify imports use `.ts` or `.tsx` extensions

### Build Fails

- Check TypeScript errors: `npx tsc --noEmit`
- Ensure all imports resolve correctly
- Verify path aliases in `tsconfig.json` and `vite.config.ts`

### Styling Issues

- Ensure Tailwind CSS is installed and configured
- Check `tailwind.config.ts` for custom colors
- Verify `globals.css` is imported in `main.tsx`
