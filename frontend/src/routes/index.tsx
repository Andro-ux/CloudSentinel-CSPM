import { createBrowserRouter, Navigate } from 'react-router-dom'
import { Layout } from '../components/layout/Layout'
import { LoginPage } from '../pages/Login'
import { DashboardPage } from '../pages/Dashboard'
import { AssetsPage } from '../pages/Assets'
import { FindingsPage } from '../pages/Findings'
import { RisksPage } from '../pages/Risks'
import { GraphPage } from '../pages/Graph'
import { ProvidersPage } from '../pages/Providers'
import { SettingsPage } from '../pages/Settings'
import { ProtectedRoute } from './ProtectedRoute'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'assets',
        element: <AssetsPage />,
      },
      {
        path: 'findings',
        element: <FindingsPage />,
      },
      {
        path: 'risks',
        element: <RisksPage />,
      },
      {
        path: 'graph',
        element: <GraphPage />,
      },
      {
        path: 'providers',
        element: <ProvidersPage />,
      },
      {
        path: 'settings',
        element: <SettingsPage />,
      },
    ],
  },
])
