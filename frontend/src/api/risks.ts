import { apiClient } from './client'

export interface Risk {
  id: string
  title: string
  description: string
  priority: string
  category: string
  score: number
  affected_assets: string[]
  recommendation: string
}

export interface RisksResponse {
  success: boolean
  data: Risk[]
  metadata: {
    pagination: {
      page: number
      page_size: number
      total: number
      has_next: boolean
      has_previous: boolean
    }
    generated_at: string
    api_version: string
  }
}

export async function getRisks(params?: {
  page?: number
  page_size?: number
  priority?: string
  category?: string
  min_score?: number
  max_score?: number
  sort_by?: string
  order?: 'asc' | 'desc'
}): Promise<RisksResponse> {
  const response = await apiClient.get('/risks', { params })
  return response.data
}
