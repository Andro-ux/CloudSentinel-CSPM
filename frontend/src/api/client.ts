import axios from 'axios'
import { QueryClient } from '@tanstack/react-query'

export const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const tokens = localStorage.getItem('cloudsentinel_tokens')
  if (tokens) {
    const { access_token } = JSON.parse(tokens)
    config.headers.Authorization = `Bearer ${access_token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      const tokens = localStorage.getItem('cloudsentinel_tokens')
      if (tokens) {
        const stored = JSON.parse(tokens)
        try {
          const refreshRes = await axios.post(
            'http://127.0.0.1:8000/api/v1/auth/refresh',
            {
              refresh_token: stored.refresh_token,
            }
          )
          const { access_token, refresh_token } = refreshRes.data.data
          localStorage.setItem('cloudsentinel_tokens', JSON.stringify({ access_token, refresh_token }))
          error.config.headers.Authorization = `Bearer ${access_token}`
          return axios(error.config)
        } catch {
          localStorage.removeItem('cloudsentinel_tokens')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      gcTime: 1000 * 60 * 10,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})
